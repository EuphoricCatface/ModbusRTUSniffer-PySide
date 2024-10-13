import datetime
import collections

from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout
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

        self.ui.plainTextEdit_Raw.cursorPositionChanged.connect(self.packet_show_parsed_by_cursor)

    def inject(self, data: bytes):
        self.add_to_raw(data)
        self.parser.process_incoming_packet(data)

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

    def unpause_handler(self, checked: Qt.CheckState):
        if checked == Qt.CheckState.Checked:
            return
        while self.raw_text_pause_queue:
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

        block_idx = self.packet_reg_to_raw(msg, packet, now)
        self.packet_show_parsed(msg)

        if type(msg) not in tools.function_table_rw:
            print("Filtering out message type", type(msg).__name__)
            return

        if msg.slave_id not in self.device_dict:
            tab_page = QWidget()
            tab_page_layout = QGridLayout(tab_page)
            table = device_value_table.DeviceValueTable(tab_page)
            tab_page_layout.addChildWidget(table)
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
        return packet_block_idx

    def packet_show_parsed(self, msg):
        self.ui.plainTextEdit_Parsed.clear()
        self.ui.plainTextEdit_Parsed.appendPlainText(msg.__class__.__name__)
        self.ui.plainTextEdit_Parsed.appendPlainText(str(msg.__dict__))

    def packet_show_parsed_by_cursor(self):
        if not self.ui.checkBox_pause.isChecked():
            return
        block_idx = self.ui.plainTextEdit_Raw.textCursor().block().blockNumber()
        if block_idx not in self.block_idx_to_packet_dict:
            self.ui.plainTextEdit_Parsed.clear()
            return
        _, msg, _ = self.block_idx_to_packet_dict[block_idx]
        self.packet_show_parsed(msg)

    def msg_show_handler(self, block_idx):
        self.ui.checkBox_pause.setChecked(True)
        self.ui.tabWidget.setCurrentIndex(0)
        then, msg, block = self.block_idx_to_packet_dict[block_idx]
        t_cursor_idx = block.position()
        t_cursor = self.ui.plainTextEdit_Raw.textCursor()
        t_cursor.setPosition(t_cursor_idx)
        # packet_show_parsed() will naturally be called because of the cursorPositionChanged signal.
        t_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        self.ui.plainTextEdit_Raw.setTextCursor(t_cursor)
