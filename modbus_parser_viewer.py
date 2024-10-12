import datetime

from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt

import modbus_parser
import collections

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
        self.packet_show_parsed(msg)

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
