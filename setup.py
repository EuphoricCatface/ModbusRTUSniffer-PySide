import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but they might need fine-tuning
build_exe_options = {
    "packages": [
        "PySide6",
        "pymodbus",
        "pyserial",
        "dotenv",
        "serial",
    ],
    "includes": [
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "pymodbus.framer.rtu_framer",
        "pymodbus.pdu",
        "pymodbus.constants",
        "pymodbus.utilities",
        "pymodbus.exceptions",
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "email",
        "http",
        "xml",
        "pydoc",
    ],
    "include_files": [
        ("modbus_parser_viewer.ui", "modbus_parser_viewer.ui"),
        ("device_addr_widget.ui", "device_addr_widget.ui"),
        ("device_value_table.ui", "device_value_table.ui"),
    ],
}

# GUI applications require a different base on Windows (the default is for a console application)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="ModbusRTUSniffer",
    version="1.0",
    description="PySide6 desktop application that sniffs Modbus RTU packets on serial connections",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, target_name="ModbusRTUSniffer")],
)
