# ModbusRTUSniffer-PySide

## Overview
This program sniffs modbus RTU packets, and shows the last known values neatly organized into a table for each device.

Currently, it assumes Input Registers and Holding Registers are in the same memory, 
the same for Coils and Discrete Inputs, and read and write will result in the same values.

This program is inspired by another python modbus sniffer https://github.com/snhobbs/ModbusSniffer/.

## Installation
This program depends on `PySide6`, `dotenv`, `pymodbus===3.7.3` and `pyserial`.

Because this program uses the internal parsing code of `pymodbus` which is not formally documented, it may easily
get broken as `pymodbus` gets upgraded. Current version of this program is developed against the 3.7.3 version. 

## Options
If you want to test this program without actually connecting to a serial device, you can add `TEST_SERIAL=1` to the
environment variables.

## UI
Above the tabs, you can input port name and baudrate, and select `Start` to start the sniffing.

`Pause` will stop updating the UI, so you can observe the states at that moment.  
(Parsing will still be running in the background, so that the timestamps showing up after unpause remains accurate)

`Stop` will disconnect you from the serial connection.  
The data collected on the program will be preserved until next time `Start` is pressed.

When sniffing is not running, you can import a raw data file to assess with this tool.  
`Example Packet.raw` is also included in the repository, even though it's identical to the contents of
`SerialReaderTest` in `serial_reader.py`.

### Raw Packets
On the main `Raw Packets` page, the raw bytes will show up on the left side. When a packet is detected, the packet
will have its own line, along with the time when the detection occurred.

The right side shows the parsed contents of a packet. Upper side shows the contents of the packet parsed by `pymodbus`,
and the lower side shows the address and value pairs of the contents of the packet.

When `Scroll to End` is checked, the most recently parsed packet will be shown on the right side.
Otherwise, you can click a packet on the left side to see its contents parsed. When you click on a address/value pair
on the bottom right side, it will highlight the corresponding part of the packet on the left side.
If available, you can switch to the other packet of the request/response pair by clicking on 
`Show Corresponding Pair` button (even though the packets are usually right next to each other).

You can save raw data to import later. It won't preserve the timing of each packet arriving.

### Slave Tables
When the parser detects a packet for a slave address, a page for the address will be created.
Each page has two tables, namely Bits and Registers.
Each row shows 16 registers, and unoccupied rows will be skipped. Recently updated cells will be highlighted
with colors, green for reading and red for writing, decaying as time goes.

Double-clicking on a cell will take you to the `Raw Packets` page, highlighting the packet that updated the cell.

Right-clicking on a cell will give you options to add breakpoints on a cell, with the options of "Change", "Read"
and "Write". When a packet triggers a breakpoint, the UI will be paused, and will take you to the `Raw Packets` page,
highlighting the packet.

## Disclaimer
This program is not guaranteed to always succeed on sniffing. If you find the program not finding any packets
for a while, try restarting the sniffing.

## TODO
* Support for separate holding/input registers // coils/discrete inputs
* Support for separate values on read/write operations
