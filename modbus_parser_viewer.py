import datetime
import collections

from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QListWidgetItem
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt

import modbus_parser
import device_value_table
import tools

from modbus_parser_viewer_ui import Ui_ModbusParserViewer


class ModbusParserViewer(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_ModbusParserViewer()
        self.ui.setupUi(self)

        self.parser = modbus_parser.ModbusParser(self.parser_callback, self.parser_callback)
        self.raw_text_pause_queue: collections.deque[tuple[str, any]] = collections.deque()
        self.ui.checkBox_pause.checkStateChanged.connect(self.unpause_handler)
        self.device_dict: dict[int, device_value_table.DeviceValueTable] = dict()
        self.block_idx_to_packet_dict = dict()

        self.res_req_dict = dict()
        self.last_req = None

        self.ui.plainTextEdit_Raw.cursorPositionChanged.connect(self.packet_show_parsed_by_cursor)
        self.current_parsed_blk_idx = -1
        self.current_parsed_packet_type = type(None)
        self.sub_packet_highlighting = False

        self.ui.pushButton_showPair.pressed.connect(self.show_pair)

        self.ui.listWidget_addrValue.itemClicked.connect(self.highlight_raw_register_value)

        self.ui.checkBox_pause.checkStateChanged.connect(self.pause_to_scrollEnd)

    def inject(self, data: bytes):
        while data:
            # The program is built on an assumption that only one packet gets found in one processing.
            # 6 is the length of a shortest possible modbus RTU packet.
            self.add_to_raw(data[:6])
            self.parser.process_incoming_packet(data[:6])
            data = data[6:]

    def add_to_raw(self, data: bytes):
        if self.ui.checkBox_pause.isChecked():
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

    def unpause_handler(self, checked: Qt.CheckState):
        if checked == Qt.CheckState.Checked:
            return
        self.packet_show_parsed(None, -1)
        while self.raw_text_pause_queue:
            # NOTE: packet_show_parsed() will be needlessly called in fast succession. This could be optimized maybe.
            task, data = self.raw_text_pause_queue.popleft()
            match task:
                case "add":
                    self.add_to_raw(data)
                case "packet_reg":
                    self.packet_register(*data)

    @staticmethod
    def bytes_to_hex_str(data: bytes):
        hex_list = [f"{b:02X}" for b in data]
        return " ".join(hex_list)

    def parser_callback(self, msg, packet):
        now = datetime.datetime.now()
        self.packet_register(msg, packet, now)

    def packet_register(self, msg, packet, now):
        if self.ui.checkBox_pause.isChecked():
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
            tab_page = QWidget()
            table = device_value_table.DeviceValueTable(tab_page)
            tab_page_layout = QGridLayout(tab_page)
            tab_page.layout().addChildWidget(table)
            tab_page.setLayout(tab_page_layout)
            self.ui.tabWidget.addTab(tab_page, f"Addr {msg.slave_id}")
            self.device_dict[msg.slave_id] = table
            table.msg_show_req.connect(self.msg_show_handler)

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
            "WriteMultipleRegistersRequest"
        ]:
            return

        if type(msg).__name__ in ["WriteMultipleRegistersRequest"]:
            addr = msg.address
            values = msg.values
        elif type(msg).__name__ in ["WriteSingleRegisterRequest", "WriteSingleRegisterResponse"]:
            addr = msg.address
            values = [msg.value]
        else:
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
        base_offset = {
            "ReadHoldingRegistersResponse": 27,
            "ReadInputRegistersResponse": 27,
            "WriteSingleRegisterRequest": 30,
            "WriteSingleRegisterResponse": 30,
            "WriteMultipleRegistersRequest": 39
        }
        stride = 6
        width = 5

        self.sub_packet_highlighting = True
        then, msg, block = self.block_idx_to_packet_dict[self.current_parsed_blk_idx]
        t_cursor_idx = block.position()
        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        t_cursor.setPosition(t_cursor_idx + base_offset[type(msg).__name__] + stride * index)
        t_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, n=width)
        self.ui.plainTextEdit_Raw.setTextCursor(t_cursor)
        self.sub_packet_highlighting = False

    def pause_to_scrollEnd(self, checked):
        if checked == Qt.CheckState.Unchecked:
            self.ui.checkBox_scrollEnd.setEnabled(True)
        if checked == Qt.CheckState.Checked:
            self.ui.checkBox_scrollEnd.setChecked(False)
            self.ui.checkBox_scrollEnd.setEnabled(False)
