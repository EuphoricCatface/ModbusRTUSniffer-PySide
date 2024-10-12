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

    @staticmethod
    def bytes_to_hex_str(data: bytes):
        hex_list = [f"{b:02X}" for b in data]
        return " ".join(hex_list)

    def parser_callback(self, msg, packet):
        pass
