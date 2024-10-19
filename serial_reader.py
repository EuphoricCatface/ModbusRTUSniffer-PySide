import typing

import serial


class SerialReader:
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate

        self.connection = self.connection = serial.Serial(port=port, baudrate=baudrate)

    def close(self):
        self.connection.close()

    def read(self):
        in_waiting = self.connection.in_waiting
        if not in_waiting:
            return b""
        return self.connection.read(in_waiting)


class SerialReaderTest:
    def __init__(self):
        self.cur_line = 0
        # self.test_lines = [
        #     b"\x01\x03\x01\x31\x00\x01\xD4\x39",  # msg 1
        #     b"\x01\x03\x02\x2E\x30\xA5\xF0",  # msg 2
        #     b"\x01\x03\x01",  # msg 1
        #     b"\x31\x00\x01",  # msg 1
        #     b"\xD4\x39\x01\x03",  # msg 1 / msg 2
        #     b"\x02\x2E",  # msg 2
        #     b"\x30\xA5\xF0",  # msg 2
        # ]
        self.test_lines = [
            b"\x01\x03\x01\x31\x00\x02\x94\x38",
            b"\x01\x03\x04\x30\x31\x32\x33\xF1\x89",  # ReadHoldingRegisters (3)
            b"\x0B\x10\x00\x12\x00\x02\x04\x0B\x0A\xC1\x02\xA0\xD5",
            b"\x0B\x10\x00\x12\x00\x02\xE1\x67",  # WriteMultipleRegisters (16)
            b"\x0B\x04\x00\x0A\x00\x01\x11\x62",
            b"\x0B\x04\x02\x10\x2F\x6D\x2D",  # ReadInputRegisters (4)
            b"\x0B\x06\x00\x04\xAB\xCD\x76\x04",
            b"\x0B\x06\x00\x04\xAB\xCD\x76\x04",  # WriteSingleRegister (6)
        ]

    def close(self):
        pass

    def read(self):
        rtn = self.test_lines[self.cur_line]
        self.cur_line += 1
        if self.cur_line >= len(self.test_lines):
            self.cur_line = 0
        return rtn
