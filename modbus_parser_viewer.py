import datetime
import collections

from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt

import modbus_parser
import device_value_table

from modbus_parser_viewer_ui import Ui_ModbusParserViewer


class ModbusParserViewer(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_ModbusParserViewer()
        self.ui.setupUi(self)

        self.parser = modbus_parser.ModbusParser(self.parser_callback, self.parser_callback)
        self.raw_text_pause_queue: collections.deque[tuple[str, any]] = collections.deque()
        self.ui.checkBox_pause.checkStateChanged.connect(self.unpause_handler)
        self.raw_line_to_packet_dict = dict()
        self.device_dict: dict[int, device_value_table.DeviceValueTable] = dict()

    def inject(self, data: bytes):
        self.add_to_raw(data)
        self.parser.process_incoming_packet(data)

    def add_to_raw(self, data: bytes):
        if self.ui.checkBox_pause.isChecked():
            self.raw_text_pause_queue.append(("add", data))
            return
        hex_str = self.bytes_to_hex_str(data)
        # QPlainTextEdit.appendPlainText() will add a newline before the appending text
        self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)
        if self.ui.plainTextEdit_Raw.textCursor().positionInBlock() != 0:
            self.ui.plainTextEdit_Raw.insertPlainText(" ")
            self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.Right)
        self.ui.plainTextEdit_Raw.insertPlainText(hex_str)
        self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)

    def unpause_handler(self, checked: Qt.CheckState):
        if checked == Qt.CheckState.Checked:
            return
        while self.raw_text_pause_queue:
            task, data = self.raw_text_pause_queue.popleft()
            match task:
                case "add":
                    self.add_to_raw(data)
                case "packet_reg":
                    self.packet_reg_to_raw(data[0], data[1], data[2])

    @staticmethod
    def bytes_to_hex_str(data: bytes):
        hex_list = [f"{b:02X}" for b in data]
        return " ".join(hex_list)

    def parser_callback(self, msg, packet):
        now = datetime.datetime.now()
        self.packet_reg_to_raw(msg, packet, now)
        if not self.ui.checkBox_pause.isChecked():
            self.packet_show_parsed(msg)

        #  -- from pymodbus/factory.py --  #
        from pymodbus.pdu import bit_read_message as bit_r_msg
        from pymodbus.pdu import bit_write_message as bit_w_msg
        # from pymodbus.pdu import diag_message as diag_msg
        # from pymodbus.pdu import file_message as file_msg
        # from pymodbus.pdu import mei_message as mei_msg
        # from pymodbus.pdu import other_message as o_msg
        # from pymodbus.pdu import pdu
        from pymodbus.pdu import register_read_message as reg_r_msg
        from pymodbus.pdu import register_write_message as reg_w_msg
        function_table = [
            reg_r_msg.ReadHoldingRegistersRequest,
            bit_r_msg.ReadDiscreteInputsRequest,
            reg_r_msg.ReadInputRegistersRequest,
            bit_r_msg.ReadCoilsRequest,
            bit_w_msg.WriteMultipleCoilsRequest,
            reg_w_msg.WriteMultipleRegistersRequest,
            reg_w_msg.WriteSingleRegisterRequest,
            bit_w_msg.WriteSingleCoilRequest,
            # reg_r_msg.ReadWriteMultipleRegistersRequest,
            # diag_msg.DiagnosticStatusRequest,
            # o_msg.ReadExceptionStatusRequest,
            # o_msg.GetCommEventCounterRequest,
            # o_msg.GetCommEventLogRequest,
            # o_msg.ReportSlaveIdRequest,
            # file_msg.ReadFileRecordRequest,
            # file_msg.WriteFileRecordRequest,
            # reg_w_msg.MaskWriteRegisterRequest,
            # file_msg.ReadFifoQueueRequest,
            # mei_msg.ReadDeviceInformationRequest,
            # ---- #
            reg_r_msg.ReadHoldingRegistersResponse,
            bit_r_msg.ReadDiscreteInputsResponse,
            reg_r_msg.ReadInputRegistersResponse,
            bit_r_msg.ReadCoilsResponse,
            bit_w_msg.WriteMultipleCoilsResponse,
            reg_w_msg.WriteMultipleRegistersResponse,
            reg_w_msg.WriteSingleRegisterResponse,
            bit_w_msg.WriteSingleCoilResponse,
            # reg_r_msg.ReadWriteMultipleRegistersResponse,
            # diag_msg.DiagnosticStatusResponse,
            # o_msg.ReadExceptionStatusResponse,
            # o_msg.GetCommEventCounterResponse,
            # o_msg.GetCommEventLogResponse,
            # o_msg.ReportSlaveIdResponse,
            # file_msg.ReadFileRecordResponse,
            # file_msg.WriteFileRecordResponse,
            # reg_w_msg.MaskWriteRegisterResponse,
            # file_msg.ReadFifoQueueResponse,
            # mei_msg.ReadDeviceInformationResponse,
        ]
        #  -- from pymodbus/factory.py --  #
        if type(msg) not in function_table:
            return

        if msg.slave_id not in self.device_dict:
            tab_page = QWidget()
            tab_page_layout = QGridLayout()
            table = device_value_table.DeviceValueTable(None)
            tab_page.setLayout(tab_page_layout)
            tab_page_layout.addChildWidget(table)
            self.ui.tabWidget.addTab(tab_page, f"Addr {msg.slave_id}")
            self.device_dict[msg.slave_id] = table

    def packet_reg_to_raw(self, msg, packet, now: datetime.datetime):
        if self.ui.checkBox_pause.isChecked():
            self.raw_text_pause_queue.append(("packet_reg", (msg, packet, now)))
            return

        packet_hex = self.bytes_to_hex_str(packet)
        self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)
        block = self.ui.plainTextEdit_Raw.textCursor().block()
        block_text = block.text()
        index_in_block = block_text.rfind(packet_hex)
        global_index = block.position() + index_in_block
        global_index_end = global_index + len(packet_hex)

        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        t_cursor.setPosition(global_index_end)
        t_cursor.deleteChar()
        self.ui.plainTextEdit_Raw.setTextCursor(t_cursor)
        self.ui.plainTextEdit_Raw.insertPlainText("\n")
        t_cursor.setPosition(global_index)
        self.ui.plainTextEdit_Raw.setTextCursor(t_cursor)
        if t_cursor.positionInBlock() != 0:
            t_cursor.deletePreviousChar()
        if t_cursor.positionInBlock() != 0:
            self.ui.plainTextEdit_Raw.insertPlainText("\n")

        packet_block_idx = self.ui.plainTextEdit_Raw.textCursor().block().blockNumber()
        self.raw_line_to_packet_dict[packet_block_idx] = (now, msg)

        self.ui.plainTextEdit_Raw.insertPlainText("[" + now.isoformat(' ') + "] ")

    def packet_show_parsed(self, msg):
        self.ui.plainTextEdit_Parsed.clear()
        self.ui.plainTextEdit_Parsed.appendPlainText(msg.__class__.__name__)
        self.ui.plainTextEdit_Parsed.appendPlainText(str(msg.__dict__))
