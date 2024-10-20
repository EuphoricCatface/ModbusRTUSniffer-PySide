import datetime
import collections
import typing
import os

from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QListWidgetItem, QFileDialog
from PySide6.QtGui import QTextCursor, QIntValidator
from PySide6.QtCore import QTimer

import modbus_parser
import device_addr_widget
import tools
import serial_reader

from modbus_parser_viewer_ui import Ui_ModbusParserViewer


class ModbusParserViewer(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_ModbusParserViewer()
        self.ui.setupUi(self)

        self.serial_reader: typing.Optional[serial_reader.SerialReader] = None
        self.reader_timer = QTimer(self)
        if os.getenv("TEST_SERIAL") == "1":
            self.reader_timer.setInterval(500)
        else:
            self.reader_timer.setInterval(1)
        self.reader_timer.timeout.connect(self.inject)
        self.parser = modbus_parser.ModbusParser(self.parser_callback, self.parser_callback)

        self.device_dict: dict[int, device_addr_widget.DeviceAddrWidget] = dict()
        self.block_idx_to_packet_dict = dict()

        self.ui.lineEdit_baudrate.setValidator(QIntValidator(0, 999999))
        self.ui.pushButton_start.clicked.connect(self.read_start)
        self.ui.pushButton_pause.toggled.connect(self.unpause_handler)
        self.ui.pushButton_pause.toggled.connect(self.pause_to_scrollEnd)
        self.raw_text_pause_queue: collections.deque[tuple[str, any]] = collections.deque()
        self.ui.pushButton_stop.clicked.connect(self.read_stop)

        self.ui.plainTextEdit_Raw.cursorPositionChanged.connect(self.packet_show_parsed_by_cursor)
        self.current_parsed_blk_idx = -1
        self.current_parsed_packet_type = type(None)
        self.sub_packet_highlighting = False

        self.ui.pushButton_showPair.pressed.connect(self.show_pair)
        self.res_req_dict = dict()
        self.last_req = None

        self.ui.listWidget_addrValue.itemClicked.connect(self.highlight_raw_register_value)

        self.raw_data = bytearray()
        self.ui.pushButton_saveRaw.pressed.connect(self.save_raw)

    def read_start(self):
        self.ui.pushButton_pause.setEnabled(True)

        if self.serial_reader is None:
            # Previously stopped
            if os.getenv("TEST_SERIAL") == "1":
                self.serial_reader = serial_reader.SerialReaderTest()
            else:
                port = self.ui.lineEdit_port.text()
                baudrate = int(self.ui.lineEdit_baudrate.text())
                self.serial_reader = serial_reader.SerialReader(port, baudrate)

            while self.ui.tabWidget.count() > 1:
                self.ui.tabWidget.removeTab(1)
            self.device_dict.clear()
            self.block_idx_to_packet_dict.clear()
            self.current_parsed_blk_idx = -1
            self.current_parsed_packet_type = type(None)
            self.sub_packet_highlighting = False
            self.res_req_dict.clear()
            self.last_req = None
            self.ui.plainTextEdit_Raw.clear()
            self.ui.plainTextEdit_Parsed.clear()
            self.ui.listWidget_addrValue.clear()

            self.parser.clear()

        self.reader_timer.start()

    def read_stop(self):
        self.ui.pushButton_pause.setDisabled(True)
        self.reader_timer.stop()
        self.serial_reader.close()
        self.serial_reader = None

    def inject(self):
        data = self.serial_reader.read()
        self.raw_data.extend(data)
        while data:
            # The program is built on an assumption that only one packet gets found in one processing.
            # 6 is the length of a shortest possible modbus RTU packet.
            self.add_to_raw(data[:11])
            self.parser.process_incoming_packet(data[:11])
            data = data[11:]

    def add_to_raw(self, data: bytes):
        if self.ui.pushButton_pause.isChecked():
            self.raw_text_pause_queue.append(("add", data))
            return
        hex_str = self.bytes_to_hex_str(data)
        # QPlainTextEdit.appendPlainText() will add a newline before the appending text
        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        t_cursor.movePosition(QTextCursor.MoveOperation.End)
        if t_cursor.positionInBlock() != 0:
            t_cursor.insertText(" ")
            t_cursor.movePosition(QTextCursor.MoveOperation.Right)
        t_cursor.insertText(hex_str)

        if self.ui.checkBox_scrollEnd.isChecked():
            # keep tracking to the end
            self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)

    def unpause_handler(self, checked):
        if checked:
            return
        self.packet_show_parsed(None, -1)
        while self.raw_text_pause_queue:
            task, data = self.raw_text_pause_queue.popleft()
            match task:
                case "add":
                    self.add_to_raw(data)
                case "packet_reg":
                    self.packet_register(*data)

    def pause_to_scrollEnd(self, checked):
        if not checked:
            self.ui.checkBox_scrollEnd.setEnabled(True)
        if checked:
            self.ui.checkBox_scrollEnd.setChecked(False)
            self.ui.checkBox_scrollEnd.setEnabled(False)

    @staticmethod
    def bytes_to_hex_str(data: bytes):
        hex_list = [f"{b:02X}" for b in data]
        return " ".join(hex_list)

    def parser_callback(self, msg, packet):
        now = datetime.datetime.now()
        self.packet_register(msg, packet, now)

    def packet_register(self, msg, packet, now):
        if self.ui.pushButton_pause.isChecked():
            self.raw_text_pause_queue.append(("packet_reg", (msg, packet, now)))
            return

        if type(msg).__name__ in ["IllegalFunctionRequest"]:
            print("Filtering out message type from ANY processing", type(msg).__name__)
            return

        block_idx = self.packet_reg_to_raw(msg, packet, now)
        self.pair_req_res(msg, block_idx)

        if self.ui.checkBox_scrollEnd.isChecked():
            self.packet_show_parsed(msg, block_idx)

        if type(msg) not in tools.function_table_rw:
            print("Filtering out message type from parsing", type(msg).__name__)
            return

        if msg.slave_id not in self.device_dict:
            table = device_addr_widget.DeviceAddrWidget(self.ui.tabWidget)
            self.ui.tabWidget.addTab(table, f"Addr {msg.slave_id}")
            self.device_dict[msg.slave_id] = table
            table.msg_show_req.connect(self.msg_show_handler)
            table.breakpoint_req.connect(self.breakpoint_handler)

        self.device_dict[msg.slave_id].inject_msg(block_idx, msg, now)

    def packet_reg_to_raw(self, msg, packet, now: datetime.datetime):
        packet_hex = self.bytes_to_hex_str(packet)
        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        t_cursor.movePosition(QTextCursor.MoveOperation.End)
        block = t_cursor.block()
        block_text = block.text()
        index_in_block = block_text.rfind(packet_hex)
        if index_in_block == -1:
            print("WARNING: search fail in the last block of RAW!", type(msg).__name__, "|", packet_hex)
        global_index = block.position() + index_in_block
        global_index_end = global_index + len(packet_hex)

        t_cursor.setPosition(global_index_end)
        t_cursor.deleteChar()
        t_cursor.insertText("\n")
        t_cursor.setPosition(global_index)
        if t_cursor.positionInBlock() != 0:
            t_cursor.deletePreviousChar()
        if t_cursor.positionInBlock() != 0:
            t_cursor.insertText("\n")

        packet_block_idx = t_cursor.block().blockNumber()
        self.block_idx_to_packet_dict[packet_block_idx] = (now, msg, block)

        t_cursor.insertText("[" + now.time().isoformat() + "] ")

        if self.ui.checkBox_scrollEnd.isChecked():
            # keep tracking to the end
            self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)

        return packet_block_idx

    def packet_show_parsed(self, msg, block_idx):
        self.ui.plainTextEdit_Parsed.clear()
        self.ui.listWidget_addrValue.clear()
        if msg is None or block_idx == -1:
            self.ui.pushButton_showPair.setDisabled(True)
            return

        self.ui.plainTextEdit_Parsed.appendPlainText(msg.__class__.__name__)
        self.ui.plainTextEdit_Parsed.appendPlainText(str(msg.__dict__))

        self.current_parsed_blk_idx = block_idx
        if not self.ui.checkBox_scrollEnd.isChecked():
            self.ui.pushButton_showPair.setEnabled(block_idx in self.res_req_dict)

        self.current_parsed_packet_type = type(msg)

        if type(msg).__name__ not in [
            "ReadHoldingRegistersResponse", "ReadInputRegistersResponse",
            "WriteSingleRegisterRequest", "WriteSingleRegisterResponse",
            "WriteMultipleRegistersRequest",
            "ReadDiscreteInputsResponse", "ReadCoilsResponse",
            "WriteSingleCoilRequest", "WriteSingleCoilResponse",
            "WriteMultipleCoilsRequest"
        ]:
            return

        if type(msg).__name__ in ["WriteMultipleRegistersRequest", "WriteMultipleCoilsRequest"]:
            addr = msg.address
            values = msg.values
        elif type(msg).__name__ in ["WriteSingleRegisterRequest", "WriteSingleRegisterResponse",
                                    "WriteSingleCoilRequest", "WriteSingleCoilResponse"]:
            addr = msg.address
            values = [msg.value]
        elif type(msg).__name__ in ["ReadDiscreteInputsResponse", "ReadCoilsResponse"]:
            req_idx = self.res_req_dict.get(block_idx)
            if req_idx is None:
                self.ui.listWidget_addrValue.addItem("Corresponding request packet not found")
                return
            req = self.block_idx_to_packet_dict[req_idx][1]
            addr = req.address
            values = msg.bits[:req.count]
        else:  # type(msg).__name__ in ["ReadHoldingRegistersResponse", "ReadDiscreteInputsResponse"]:
            req_idx = self.res_req_dict.get(block_idx)
            if req_idx is None:
                self.ui.listWidget_addrValue.addItem("Corresponding request packet not found")
                return
            req = self.block_idx_to_packet_dict[req_idx][1]
            addr = req.address
            values = msg.registers

        for offset, value in enumerate(values):
            self.ui.listWidget_addrValue.addItem(
                f"0x{addr + offset:04X} = {value} ({value:04X})"
            )

    def packet_show_parsed_by_cursor(self):
        if self.ui.checkBox_scrollEnd.isChecked():
            return
        if self.sub_packet_highlighting:
            return
        block_idx = self.ui.plainTextEdit_Raw.textCursor().block().blockNumber()
        msg_with_meta = self.block_idx_to_packet_dict.get(block_idx)
        msg = msg_with_meta[1] if msg_with_meta is not None else None
        self.packet_show_parsed(msg, block_idx)

    def msg_show_handler(self, block_idx):
        self.ui.checkBox_scrollEnd.setChecked(False)
        self.ui.tabWidget.setCurrentIndex(0)
        then, msg, block = self.block_idx_to_packet_dict[block_idx]
        t_cursor_idx = block.position()
        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        t_cursor.setPosition(t_cursor_idx)
        # packet_show_parsed() will naturally be called because of the cursorPositionChanged signal.
        t_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        self.ui.plainTextEdit_Raw.setTextCursor(t_cursor)

    def breakpoint_handler(self, block_idx):
        self.ui.pushButton_pause.click()
        self.msg_show_handler(block_idx)

    def pair_req_res(self, msg, block_idx):
        # A bit of parsing here, so that we can tell associated addresses later
        if type(msg).__name__.endswith("Request"):
            self.last_req = (msg, block_idx)
            return
        if not type(msg).__name__.endswith("Response"):
            return
        if self.last_req is None:
            return

        req, req_block_idx = self.last_req
        self.last_req = None
        if type(req).__name__[:-7] != type(msg).__name__[:-8]:
            return

        self.res_req_dict[req_block_idx] = block_idx
        self.res_req_dict[block_idx] = req_block_idx

    def show_pair(self):
        opposite_idx = self.res_req_dict.get(self.current_parsed_blk_idx)
        if opposite_idx is None:
            return
        self.msg_show_handler(opposite_idx)

    def highlight_raw_register_value(self, item: QListWidgetItem):
        index = self.ui.listWidget_addrValue.row(item)
        base_offset_reg = {
            "ReadHoldingRegistersResponse": 27,
            "ReadInputRegistersResponse": 27,
            "WriteSingleRegisterRequest": 30,
            "WriteSingleRegisterResponse": 30,
            "WriteMultipleRegistersRequest": 39
        }
        base_offset_bit = {
            "ReadDiscreteInputsResponse": 27,
            "ReadCoilsResponse": 27,
            "WriteSingleCoilRequest": 30,
            "WriteSingleCoilResponse": 30,
            "WriteMultipleCoilsRequest": 39
        }

        self.sub_packet_highlighting = True
        then, msg, block = self.block_idx_to_packet_dict[self.current_parsed_blk_idx]
        t_cursor_idx = block.position()
        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        if type(msg).__name__ in base_offset_reg:
            stride = 6
            width = 5
            t_cursor.setPosition(t_cursor_idx + base_offset_reg[type(msg).__name__] + stride * index)
        else:
            stride = 3
            width = 2
            t_cursor.setPosition(t_cursor_idx + base_offset_bit[type(msg).__name__] + stride * (index // 8))
        t_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, n=width)
        self.ui.plainTextEdit_Raw.setTextCursor(t_cursor)
        self.sub_packet_highlighting = False

    def save_raw(self):
        filename, _filter = QFileDialog.getSaveFileName(self, "Save Raw Data", filter="Raw Data (*.raw)")
        if not filename.endswith(".raw") and "." not in os.path.basename(filename):
            filename += ".raw"
        with open(filename, mode="wb") as fp:
            fp.write(self.raw_data)
