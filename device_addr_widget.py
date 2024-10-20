from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal

from device_addr_widget_ui import Ui_DeviceAddrWidget


class DeviceAddrWidget(QWidget):
    msg_show_req = Signal(int)
    breakpoint_req = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceAddrWidget()
        self.ui.setupUi(self)

        self.ui.tab_register.msg_show_req.connect(self.msg_show_req.emit)
        self.ui.tab_register.breakpoint_req.connect(self.breakpoint_req.emit)
        self.ui.tab_bit.msg_show_req.connect(self.msg_show_req.emit)
        self.ui.tab_bit.breakpoint_req.connect(self.breakpoint_req.emit)

    def inject_msg(self, block_idx, msg, now):
        if "Coil" in type(msg).__name__ or "Discrete" in type(msg).__name__:
            self.ui.tab_bit.inject_msg(block_idx, msg, now)
        elif "Register" in type(msg).__name__:
            self.ui.tab_register.inject_msg(block_idx, msg, now)
