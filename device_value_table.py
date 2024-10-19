import datetime

from PySide6.QtWidgets import QWidget, QTableWidgetItem
from PySide6.QtCore import Signal, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor

from device_value_table_ui import Ui_DeviceValueTable


class ColorFadeItem(QTableWidgetItem):
    def __init__(self):
        super().__init__()
        self.start_color = QColor("#00FF00")
        self.animation = QVariantAnimation(None)
        self.animation.valueChanged.connect(self.color_mix)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(10000)
        self.animation.setEasingCurve(QEasingCurve.Type.OutExpo)

        self.block_idx = -1
        self.update_time = datetime.datetime.fromtimestamp(0)

    def color_mix(self, value):
        gr = self.start_color
        wh = QColor("#FFFFFF")
        r = gr.red() * (1 - value) + wh.red() * value
        g = gr.green() * (1 - value) + wh.green() * value
        b = gr.blue() * (1 - value) + wh.blue() * value
        self.setBackground(QColor(r, g, b))

    def setText(self, text):
        super().setText(text)
        self.animation.stop()
        self.animation.start()


class DeviceValueTable(QWidget):
    msg_show_req = Signal(int)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceValueTable()
        self.ui.setupUi(self)

        self.ui.tableWidget_main.itemDoubleClicked.connect(self.item_double_click)

        self.row_dict: dict[int, list[ColorFadeItem | None]] = dict()
        self.last_request = None

    def inject_msg(self, block_idx, msg, now):
        if "Coil" in type(msg).__name__:
            print("Coil operation NYI")

        if type(msg).__name__.endswith("Request"):
            if self.last_request is not None:
                print("A request has arrived right after another request")
            self.last_request = (msg, block_idx)
            return

        if self.last_request is None:
            print("A response has arrived without a previous request")
            return

        if type(self.last_request[0]).__name__[:-7] != type(msg).__name__[:-8]:
            print("Request - response type mismatch", self.last_request[0], msg)
            return

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
            case "WriteSingleRegisterResponse":
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

            cell = self.row_dict[row][column]
            if cell is None:
                cell = ColorFadeItem()
                table_row = self.quotient_to_table_row(row)
                self.ui.tableWidget_main.setItem(table_row, column, cell)
                self.row_dict[row][column] = cell
            cell.block_idx = block_idx
            cell.update_time = now
            if type(response).__name__.startswith("Write"):
                cell.start_color = QColor("#FF0000")
            elif type(response).__name__.startswith("Read"):
                cell.start_color = QColor("#00FF00")
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

    def item_double_click(self, item):
        self.msg_show_req.emit(item.block_idx)
