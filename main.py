from pymodbus.factory import ClientDecoder
from pymodbus.factory import ServerDecoder
from pymodbus.framer import FramerRTU

from pymodbus.exceptions import ModbusIOException


def print_msg_client(msg, **kwargs):
    print("client framer:")
    print(kwargs.get("packet", None))
    print(type(msg).__name__, msg.__dict__)


def print_msg_server(msg, **kwargs):
    print("server framer:")
    print(kwargs.get("packet", None))
    print(type(msg).__name__, msg.__dict__)


def processIncomingPacket_mod(self: FramerRTU, data: bytes, callback, tid=None):
    """Process new packet pattern.

    This takes in a new request packet, adds it to the current
    packet stream, and performs framing on it. That is, checks
    for complete messages, and once found, will process all that
    exist.  This handles the case when we read N + 1 or 1 // N
    messages at a time instead of 1.

    The processed and decoded messages are pushed to the callback
    function to process and send.
    """
    # Log.debug("Processing: {}", data, ":hex")
    self.databuffer += data
    while True:
        if self.databuffer == b'':
            return
        used_len, data = self.decode(self.databuffer)
        self.databuffer = self.databuffer[used_len:]
        if not data:
            if used_len:
                continue
            return
        if self.dev_ids and self.incoming_dev_id not in self.dev_ids:
            # Log.debug("Not a valid slave id - {}, ignoring!!", self.incoming_dev_id)
            self.databuffer = b''
            continue
        if (result := self.decoder.decode(data)) is None:
            self.databuffer = b''
            raise ModbusIOException("Unable to decode request")
        result.slave_id = self.incoming_dev_id
        result.transaction_id = self.incoming_tid
        # Log.debug("Frame advanced, resetting header!!")
        if tid and result.transaction_id and tid != result.transaction_id:
            self.databuffer = b''
        else:
            callback(result, packet=data)  # defer or push to a thread?


def main():
    client_framer = FramerRTU(ClientDecoder(), [])
    client_framer.processIncomingPacket = \
        lambda *args, **kwargs: processIncomingPacket_mod(client_framer, *args, **kwargs)
    server_framer = FramerRTU(ServerDecoder(), [])
    server_framer.processIncomingPacket = \
        lambda *args, **kwargs: processIncomingPacket_mod(server_framer, *args, **kwargs)

    test_stream = [
        b"\x01\x03\x01\x31\x00\x1E\x95\xF1",  # msg 1
        b"\x01\x03\x02\x2E\x30\xA5\xF0",  # msg 2
        b"\x01\x03\x01",  # msg 1
        b"\x31\x00\x1E",  # msg 1
        b"\x95\xF1\x01\x03\x02",  # msg 1 / msg 2
        b"\x2E\x30\xA5\xF0",  # msg 2
    ]

    for data in test_stream:
        client_framer.processIncomingPacket(data, print_msg_client)
        server_framer.processIncomingPacket(data, print_msg_server)


if __name__ == "__main__":
    main()
