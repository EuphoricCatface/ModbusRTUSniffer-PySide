from PySide6.QtWidgets import QWidget

from device_value_table_ui import Ui_DeviceValueTable


class DeviceValueTable(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceValueTable()
        self.ui.setupUi(self)
