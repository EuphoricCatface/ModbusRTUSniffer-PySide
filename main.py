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

    test_packet = b"\x01\x03\x01\x31\x00\x1E\x95\xF1"

    print("client_framer:")
    client_framer.processIncomingPacket(test_packet, callback)
    print("server_framer:")
    server_framer.processIncomingPacket(test_packet, callback)


if __name__ == "__main__":
    main()
