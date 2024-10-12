import logging

from pymodbus.factory import ClientDecoder
from pymodbus.factory import ServerDecoder

from pymodbus.framer import FramerRTU


def callback(*args, **kwargs):
    for msg in args:
        print(type(msg), msg.__dict__)


def main():
    logging.getLogger().setLevel(logging.DEBUG)

    client_framer = FramerRTU(ClientDecoder(), [])
    server_framer = FramerRTU(ServerDecoder(), [])

    test_stream = [
        b"\x01\x03\x01\x31\x00\x1E\x95\xF1",  # msg 1
        b"\x01\x03\x02\x2E\x30\xA5\xF0",  # msg 2
        b"\x01\x03\x01",  # msg 1
        b"\x31\x00\x1E",  # msg 1
        b"\x95\xF1\x01\x03\x02",  # msg 1 / msg 2
        b"\x2E\x30\xA5\xF0",  # msg 2
    ]

    for data in test_stream:
        print("client_framer:")
        client_framer.processIncomingPacket(data, callback)
        print("server_framer:")
        server_framer.processIncomingPacket(data, callback)


if __name__ == "__main__":
    main()
