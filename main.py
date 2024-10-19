import sys

import dotenv

from PySide6.QtWidgets import QApplication

import modbus_parser_viewer


def main():
    dotenv.load_dotenv()
    app = QApplication(sys.argv)

    viewer = modbus_parser_viewer.ModbusParserViewer(None)
    viewer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
