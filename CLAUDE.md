# CLAUDE.md

## Project Overview

ModbusRTUSniffer-PySide is a PySide6 desktop application that sniffs Modbus RTU packets on serial connections and displays real-time register/coil values organized by device address. It uses internal (undocumented) pymodbus 3.7.3 parsing APIs.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Set `TEST_SERIAL=1` in environment (or `.env` file) to run without a real serial device.

## Project Structure

```
main.py                      # Entry point: loads .env, creates QApplication + main window
modbus_parser.py             # Core Modbus RTU framing with dual client/server framers
modbus_parser_viewer.py      # Main window: serial I/O, packet display, device tabs (395 lines, largest module)
serial_reader.py             # SerialReader (real) and SerialReaderTest (hardcoded test data)
tools.py                     # function_table_rw: maps pymodbus request/response classes
device_addr_widget.py        # Per-device tab containing bit and register tables
device_value_table.py        # Table widget with color-fade cells, breakpoints, animations

modbus_parser_viewer.ui      # Qt Designer UI files (edit these, not the *_ui.py)
device_addr_widget.ui
device_value_table.ui
modbus_parser_viewer_ui.py   # Generated from .ui files — DO NOT EDIT MANUALLY
device_addr_widget_ui.py
device_value_table_ui.py
```

## Architecture

### Data Flow

```
SerialReader.read() → ModbusParserViewer.inject(data)
  → ModbusParser.process_incoming_packet()
    → Server framer (decodes requests) + Client framer (decodes responses)
    → parser_callback(msg, packet)
  → packet_register() → DeviceAddrWidget.inject_msg()
    → DeviceValueTable.inject_msg() → ColorFadeItem cell updates
```

### Key Design Decisions

- **Dual framers**: Both a client and server `FramerRTU` run in parallel to distinguish request vs response direction on the shared serial bus. Databuffers are synchronized between them.
- **WriteSingleCoil/Register ambiguity**: Request and response have identical binary structure. Resolved via state machine flags (`writesingleregisterrequest_detected`, etc.).
- **Monkey-patched pymodbus**: `processIncomingPacket_mod` replaces `FramerRTU.processIncomingPacket` to handle fragmentation, CRC, and the ambiguity resolution.
- **Pause system**: Parsing continues during pause (preserving timestamps). UI updates queue into `raw_text_pause_queue` and replay on unpause.
- **Sparse tables**: `DeviceValueTable` only allocates rows for addresses that have been seen, with "..." separator rows for gaps.

### UI Pattern

Each `.ui` file is compiled to a `*_ui.py` file. The manual Python class instantiates the generated `Ui_*` class as `self.ui` and calls `self.ui.setupUi(self)`. Access UI elements via `self.ui.<element_name>`.

## Regenerating UI Files

When `.ui` files are modified, regenerate with:

```bash
pyside6-uic modbus_parser_viewer.ui > modbus_parser_viewer_ui.py
pyside6-uic device_addr_widget.ui > device_addr_widget_ui.py
pyside6-uic device_value_table.ui > device_value_table_ui.py
```

The `*_ui.py` files are committed to the repo. Never edit them by hand.

## Dependencies

Defined in `requirements.txt`:
- **PySide6** — Qt GUI framework
- **python-dotenv** — `.env` file loading
- **pymodbus==3.7.3** — Modbus protocol (pinned; internal APIs used, will break on upgrade)
- **pyserial** — Serial port I/O

Requires **Python 3.10+** (uses walrus operator, `match` statements, `X | Y` type unions).

## Coding Conventions

- **Naming**: Modules `snake_case`, classes `PascalCase`, methods/variables `snake_case`
- **UI element names**: Prefixed by widget type (`pushButton_start`, `plainTextEdit_Raw`, `lineEdit_port`)
- **Imports**: stdlib → third-party (PySide6, pymodbus, etc.) → local modules
- **Type hints**: Used selectively on parameters and member variables; return types generally omitted
- **Docstrings**: Minimal — only one exists in the codebase (in `modbus_parser.py`)
- **String formatting**: f-strings throughout
- **Signals/slots**: PySide6 `Signal()` with `.connect()` / `.emit()`
- **Async model**: `QTimer`-based polling (no threads)

## Commit Message Style

- Imperative mood, capitalized first word, no trailing period
- Optional subsystem prefix: `Viewer:`, `README:`, etc.
- Keep subject line under ~60 characters
- Examples: `Add requirements.txt and update README installation instructions`, `Viewer: disable port and baudrate edit during sniffing`

## Known Limitations

- Framers can get confused after extended sniffing — restart if packets stop appearing
- Assumes Input/Holding Registers share memory, same for Coils/Discrete Inputs
- Read and write operations assumed to produce same values
- No test suite or CI

## TODO (from README)

- Support for separate holding/input registers and coils/discrete inputs
- Support for separate values on read/write operations
