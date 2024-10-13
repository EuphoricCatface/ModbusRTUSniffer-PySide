from PySide6.QtWidgets import QWidget, QTableWidgetItem
from PySide6.QtCore import Signal

from device_value_table_ui import Ui_DeviceValueTable


class DeviceValueTable(QWidget):
    msg_show_req = Signal(int)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceValueTable()
        self.ui.setupUi(self)

        self.ui.tableWidget_main.cellDoubleClicked.connect(self.cell_double_click)

        self.row_dict: dict[int, list[list | None]] = dict()
        self.last_request = None

    def inject_msg(self, block_idx, msg, now):
        if "Coil" in type(msg).__name__:
            print("Coil operation NYI")

        if type(msg).__name__.endswith("Request"):
            if (type(msg).__name__ == "WriteSingleRegisterRequest" and
                    self.last_request is not None and
                    type(self.last_request[0]).__name__ == "WriteSingleRegisterRequest"):
                pass
            else:
                self.last_request = (msg, block_idx)
                return

        if self.last_request is None:
            print("A response has arrived without a previous request")
            return

        if type(self.last_request[0]).__name__[:-7] != type(msg).__name__[:-8]:
            if type(msg).__name__ == "WriteSingleRegisterRequest":
                pass
            else:
                print("Request - response type mismatch", self.last_request[0], msg)
                return

        if type(msg).__name__ == "WriteSingleRegisterRequest":
            pass
        else:
            if msg.isError():
                print("Response is error")
                return

        request, req_idx = self.last_request
        response = msg
        self.last_request = None

        address = request.address
        values: list[int] = []
        match type(response).__name__:
            case "ReadHoldingRegistersResponse" | "ReadInputRegistersResponse":
                values = response.registers
            case "WriteSingleRegisterRequest":  # NOT WriteSingleRegisterResponse - WORKAROUND!
                values = [request.value]
                block_idx = req_idx
            case "WriteMultipleRegistersResponse":
                values = request.values
                block_idx = req_idx

        for offset, value in enumerate(values):
            cell_addr = address + offset
            row = cell_addr // 16
            column = cell_addr % 16

            if row not in self.row_dict:
                self.insert_row(row)

            cell_with_meta = self.row_dict[row][column]
            if cell_with_meta is None:
                cell_with_meta = self.row_dict[row][column] = [block_idx, self.create_cell(row, column), now]
            cell_with_meta[0] = block_idx
            cell = cell_with_meta[1]
            cell.setText(str(value))

    def insert_row(self, new_row):
        self.row_dict[new_row] = [None for _ in range(16)]

        table_row = self.quotient_to_table_row(new_row)

        prev_exist = (new_row == 0) or ((new_row - 1) in self.row_dict)
        next_exist = (new_row == 65535) or ((new_row + 1) in self.row_dict)

        new_row_header = QTableWidgetItem()
        new_row_header.setText(f"{new_row * 16:04X}")

        match (prev_exist, next_exist):
            case (True, True):
                self.ui.tableWidget_main.setVerticalHeaderItem(table_row, new_row_header)
            case (True, False) | (False, True):
                self.ui.tableWidget_main.insertRow(table_row)
                self.ui.tableWidget_main.setVerticalHeaderItem(table_row, new_row_header)
            case (False, False):
                dummy_header = QTableWidgetItem()
                dummy_header.setText("...")
                self.ui.tableWidget_main.insertRow(table_row)
                self.ui.tableWidget_main.setVerticalHeaderItem(table_row, dummy_header)
                self.ui.tableWidget_main.insertRow(table_row)
                self.ui.tableWidget_main.setVerticalHeaderItem(table_row, new_row_header)

    def create_cell(self, row, column):
        table_row = self.quotient_to_table_row(row)

        item = QTableWidgetItem()
        self.ui.tableWidget_main.setItem(table_row, column, item)
        return item

    def quotient_to_table_row(self, quot):
        rows = sorted(self.row_dict)
        rows_padded = []
        prev_row = -1
        for row in rows:
            if prev_row + 1 != row:
                rows_padded.append(-1)
            rows_padded.append(row)
            prev_row = row
        if rows_padded[-1] != 65535:
            rows_padded.append(-1)

        return rows_padded.index(quot)

    def cell_double_click(self, row_on_table, column):
        if self.ui.tableWidget_main.item(row_on_table, column) is None:
            return
        row_header = self.ui.tableWidget_main.verticalHeaderItem(row_on_table).text()
        row = int(row_header, 16) // 16
        cell_with_meta = self.row_dict[row][column]
        block_idx = cell_with_meta[0]
        self.msg_show_req.emit(block_idx)
