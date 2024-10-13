import collections

from PySide6.QtWidgets import QWidget

from device_value_table_ui import Ui_DeviceValueTable


class DeviceValueTable(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceValueTable()
        self.ui.setupUi(self)

        self.row_dict: collections.defaultdict[int, list[int | None]]\
            = collections.defaultdict(lambda: [None for _ in range(16)])
        self.last_request = None

    def inject_msg(self, callback_count, msg, now):
        if "Coil" in type(msg).__name__:
            print("Coil operation NYI")

        if type(msg).__name__.endswith("Request"):
            self.last_request = msg
            return

        if self.last_request is None:
            print("A response has arrived without a previous request")
            return

        if type(self.last_request).__name__[:-7] != type(msg).__name__[:-8]:
            print("Request - response type mismatch")
            return

        if msg.isError():
            print("Response is error")
            return

        request = self.last_request
        response = msg

        address = request.address
        values: list[int] = []
        match type(response).__name__:
            case "ReadHoldingRegistersResponse" | "ReadInputRegistersResponse":
                values = response.registers
            case "WriteSingleRegisterResponse":
                values = [request.value]
            case "WriteMultipleRegistersResponse":
                values = request.values

        print(address, values)

        for offset, value in enumerate(values):
            cell_addr = address + offset
            row = cell_addr // 16
            column = cell_addr % 16
            self.row_dict[row][column] = value
