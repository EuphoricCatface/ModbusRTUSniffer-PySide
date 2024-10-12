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


def main():
    dotenv.load_dotenv()
    reader = SerialReader(
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
    timer.setInterval(1)
    timer.timeout.connect(serial_inject)
    timer.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
