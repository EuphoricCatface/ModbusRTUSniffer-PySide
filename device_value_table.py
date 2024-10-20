import datetime

from PySide6.QtWidgets import QWidget, QTableWidgetItem, QMenu
from PySide6.QtCore import Signal, QVariantAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QColor, QAction

from device_value_table_ui import Ui_DeviceValueTable


class ColorFadeItem(QTableWidgetItem):
    def __init__(self, breakpoint_signal):
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
        self.rw = ""

        self.breakpoint_signal = breakpoint_signal
        self.breakpoint_condition = 0x00
        # 0x04 = change, 0x02 = read, 0x01 = write

    def color_mix(self, value):
        gr = self.start_color
        wh = QColor("#FFFFFF")
        r = gr.red() * (1 - value) + wh.red() * value
        g = gr.green() * (1 - value) + wh.green() * value
        b = gr.blue() * (1 - value) + wh.blue() * value
        self.setBackground(QColor(r, g, b))

    def set_text_with_metadata(self, text, block_idx, update_time, rw):
        self.block_idx = block_idx
        self.update_time = update_time
        self.rw = rw

        signal_emit = False

        text_before = self.text()
        if (self.breakpoint_condition & 0x04) and text_before != text:
            signal_emit = True
        match self.rw:
            case "r":
                self.start_color = QColor("#00FF00")
                if self.breakpoint_condition & 0x02:
                    signal_emit = True
            case "w":
                self.start_color = QColor("#FF0000")
                if self.breakpoint_condition & 0x01:
                    signal_emit = True
        self.setText(text)

        if signal_emit:
            self.breakpoint_signal.emit(block_idx)

    def setText(self, text):
        super().setText(text)
        self.animation.stop()
        self.animation.start()


class DeviceValueTable(QWidget):
    msg_show_req = Signal(int)
    breakpoint_req = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = Ui_DeviceValueTable()
        self.ui.setupUi(self)

        self.ui.tableWidget_main.itemDoubleClicked.connect(self.item_double_click)
        self.ui.tableWidget_main.customContextMenuRequested.connect(self.table_context)

        self.row_dict: dict[int, list[ColorFadeItem | None]] = dict()
        self.last_request = None

    def inject_msg(self, block_idx, msg, now):
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
                cell = ColorFadeItem(self.breakpoint_req)
                table_row = self.quotient_to_table_row(row)
                self.ui.tableWidget_main.setItem(table_row, column, cell)
                self.row_dict[row][column] = cell

            rw = ""
            if type(response).__name__.startswith("Write"):
                rw = "w"
            elif type(response).__name__.startswith("Read"):
                rw = "r"
            cell.set_text_with_metadata(str(value), block_idx, now, rw)

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

    def table_context(self, e: QPoint):
        item: ColorFadeItem = self.ui.tableWidget_main.itemAt(e)
        if not item:
            return
        menu_pos = self.ui.tableWidget_main.viewport().mapToGlobal(e)
        menu = QMenu(self.ui.tableWidget_main)

        current_bp_cond = item.breakpoint_condition
        submenu_breakpoint = QMenu("Breakpoint on", menu)
        for idx, action_name in enumerate(["Write", "Read", "Change"]):
            action = QAction(action_name, submenu_breakpoint)
            action.setCheckable(True)
            if current_bp_cond & (1 << idx):
                action.setChecked(True)
            submenu_breakpoint.addAction(action)

        menu.addMenu(submenu_breakpoint)
        menu.exec(menu_pos)

        new_bp_cond = 0
        for idx, action in enumerate(submenu_breakpoint.actions()):
            if action.isChecked():
                new_bp_cond += 1 << idx
        item.breakpoint_condition = new_bp_cond
