import collections

from PySide6.QtWidgets import QWidget, QTableWidgetItem

from device_value_table_ui import Ui_DeviceValueTable


class DeviceValueTable(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceValueTable()
        self.ui.setupUi(self)

        self.row_dict: dict[int, list[tuple | None]] = dict()
        self.last_request = None

    def inject_msg(self, block_idx, msg, now):
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
        self.last_request = None

        address = request.address
        values: list[int] = []
        match type(response).__name__:
            case "ReadHoldingRegistersResponse" | "ReadInputRegistersResponse":
                values = response.registers
            case "WriteSingleRegisterResponse":
                values = [request.value]
            case "WriteMultipleRegistersResponse":
                values = request.values

        for offset, value in enumerate(values):
            cell_addr = address + offset
            row = cell_addr // 16
            column = cell_addr % 16

            if row not in self.row_dict:
                self.insert_row(row)

            cell_with_meta = self.row_dict[row][column]
            if cell_with_meta is None:
                cell_with_meta = self.row_dict[row][column] = (block_idx, self.create_cell(row, column), now)
            cell = cell_with_meta[1]
            cell.setText(str(value))

    def insert_row(self, new_row):
        self.row_dict[new_row] = [None for _ in range(16)]

        rows = sorted(self.row_dict)
        rows_padded = []
        prev_row = -1
        for row in rows:
            if prev_row + 1 != row:
                rows_padded.append(-1)
            rows_padded.append(row)
        if rows_padded[-1] != 65535:
            rows_padded.append(-1)

        index_new_row = rows_padded.index(new_row)
        prev_exist = (new_row == 0) or ((new_row - 1) in self.row_dict)
        next_exist = (new_row == 65535) or ((new_row + 1) in self.row_dict)

        new_row_header = QTableWidgetItem()
        new_row_header.setText(f"{new_row * 16:04X}")

        match (prev_exist, next_exist):
            case (True, True):
                self.ui.tableWidget_main.setVerticalHeaderItem(index_new_row, new_row_header)
            case (True, False) | (False, True):
                self.ui.tableWidget_main.insertRow(index_new_row)
                self.ui.tableWidget_main.setVerticalHeaderItem(index_new_row, new_row_header)
            case (False, False):
                dummy_header = QTableWidgetItem()
                dummy_header.setText("...")
                self.ui.tableWidget_main.insertRow(index_new_row)
                self.ui.tableWidget_main.setVerticalHeaderItem(index_new_row, dummy_header)
                self.ui.tableWidget_main.insertRow(index_new_row)
                self.ui.tableWidget_main.setVerticalHeaderItem(index_new_row, new_row_header)

    def create_cell(self, row, column):
        rows = sorted(self.row_dict)
        rows_padded = []
        prev_row = -1
        for row in rows:
            if prev_row + 1 != row:
                rows_padded.append(-1)
            rows_padded.append(row)
        if rows_padded[-1] != 65535:
            rows_padded.append(-1)

        row_index = rows_padded.index(row)

        item = QTableWidgetItem()
        self.ui.tableWidget_main.setItem(row_index, column, item)
        return item
