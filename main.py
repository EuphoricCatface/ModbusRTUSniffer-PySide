import sys
import os

import serial
import dotenv

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

import modbus_parser_viewer


class SerialReader:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate

        self.connection = serial.Serial(port=port, baudrate=baudrate)

    def read(self):
        in_waiting = self.connection.in_waiting
        if not in_waiting:
            return b""
        return self.connection.read(in_waiting)


class SerialReaderTest:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate

        self.cur_line = 0
        self.test_lines = [
            b"\x01\x03\x01\x31\x00\x01\xD4\x39",  # msg 1
            b"\x01\x03\x02\x2E\x30\xA5\xF0",  # msg 2
            b"\x01\x03\x01",  # msg 1
            b"\x31\x00\x01",  # msg 1
            b"\xD4\x39\x01\x03",  # msg 1 / msg 2
            b"\x02\x2E",  # msg 2
            b"\x30\xA5\xF0",  # msg 2
        ]  # TODO: check many packets in one line

    def read(self):
        rtn = self.test_lines[self.cur_line]
        self.cur_line += 1
        if self.cur_line >= len(self.test_lines):
            self.cur_line = 0
        return rtn


def main():
    dotenv.load_dotenv()
    # reader = SerialReader(
    reader = SerialReaderTest(
        os.getenv("PORT"),
        int(os.getenv("BAUDRATE"))
    )

    app = QApplication(sys.argv)

    viewer = modbus_parser_viewer.ModbusParserViewer(None)
    viewer.show()

    def serial_inject():
        data = reader.read()
        if not data:
            return
        viewer.inject(data)
    timer = QTimer(app)
    # timer.setInterval(1)
    timer.setInterval(500)
    timer.timeout.connect(serial_inject)
    timer.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
