from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QTextCursor

from modbus_parser_viewer_ui import Ui_ModbusParserViewer


class ModbusParserViewer(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_ModbusParserViewer()
        self.ui.setupUi(self)

    def inject(self, data: bytes):
        self.add_to_raw(data)

    def add_to_raw(self, data: bytes):
        hex_list = [f"{b:02X}" for b in data]
        hex_str = " ".join(hex_list)
        # QPlainTextEdit.appendPlainText() will add a newline before the appending text
        self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)
        if self.ui.plainTextEdit_Raw.textCursor().positionInBlock() != 0:
            self.ui.plainTextEdit_Raw.insertPlainText(" ")
            self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.Right)
        self.ui.plainTextEdit_Raw.insertPlainText(hex_str)
        self.ui.plainTextEdit_Raw.moveCursor(QTextCursor.MoveOperation.End)
