import copy

from pymodbus.factory import ClientDecoder
from pymodbus.factory import ServerDecoder
from pymodbus.framer import FramerRTU

from pymodbus.exceptions import ModbusIOException


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
        wastebin = self.databuffer[:used_len]
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
            full_packet_length = len(data) + 3  # assuming slave_addr (1 byte) + CRC (2 byte)
            full_packet = wastebin[-full_packet_length:]
            callback(msg=result, packet=full_packet)  # defer or push to a thread?


class ModbusParser:
    def __init__(self, client_framer_callback, server_framer_callback):
        self.client_framer = FramerRTU(ClientDecoder(), [])
        self.client_framer.processIncomingPacket = \
            lambda *args, **kwargs: processIncomingPacket_mod(self.client_framer, *args, **kwargs)
        self.server_framer = FramerRTU(ServerDecoder(), [])
        self.server_framer.processIncomingPacket = \
            lambda *args, **kwargs: processIncomingPacket_mod(self.server_framer, *args, **kwargs)

        self.client_framer_callback_ = client_framer_callback
        self.server_framer_callback_ = server_framer_callback

        # The framers often get confused after a while, especially the client framer.
        # Each databuffer is manually snipped when the other framer finds a packet.
        self.server_made_it = False
        self.client_made_it = False

        # WriteSingleRegister(Request/Response) are exactly the same.
        # We need to assume the first one must be the request and the next must be response.
        self.writesingleregisterrequest_detected = False
        self.writesingleregisterresponse_expected = False

    def process_incoming_packet(self, data):
        self.server_framer.processIncomingPacket(data, self.server_framer_callback)
        self.client_framer.processIncomingPacket(data, self.client_framer_callback)

        if self.client_made_it:
            self.server_framer.databuffer = copy.deepcopy(self.client_framer.databuffer)
            self.client_made_it = False

        if self.server_made_it:
            self.client_framer.databuffer = copy.deepcopy(self.server_framer.databuffer)
            self.server_made_it = False

        if self.writesingleregisterrequest_detected:
            self.writesingleregisterresponse_expected = True
            self.writesingleregisterrequest_detected = False

    def client_framer_callback(self, *args, **kwargs):  # Response
        if (type(kwargs["msg"]).__name__ == "WriteSingleRegisterResponse"
                and not self.writesingleregisterresponse_expected):
            return

        self.client_made_it = True
        self.client_framer_callback_(*args, **kwargs)
        self.writesingleregisterresponse_expected = False

    def server_framer_callback(self, *args, **kwargs):  # Request
        if type(kwargs["msg"]).__name__ == "WriteSingleRegisterRequest":
            if self.writesingleregisterresponse_expected:
                return
            else:
                self.writesingleregisterrequest_detected = True

        self.server_made_it = True
        self.server_framer_callback_(*args, **kwargs)
        self.writesingleregisterresponse_expected = False


def main():
    def print_msg_client(msg, packet):
        print("client framer:")
        print(packet)
        print(type(msg).__name__, msg.__dict__)

    def print_msg_server(msg, **kwargs):
        print("server framer:")
        print(kwargs.get("packet", None))
        print(type(msg).__name__, msg.__dict__)

    parser = ModbusParser(print_msg_client, print_msg_server)

    test_stream = [
        b"\x01\x03\x01\x31\x00\x1E\x95\xF1",  # msg 1
        b"\x01\x03\x02\x2E\x30\xA5\xF0",  # msg 2
        b"\x01\x03\x01",  # msg 1
        b"\x31\x00\x1E",  # msg 1
        b"\x95\xF1\x01\x03\x02",  # msg 1 / msg 2
        b"\x2E\x30\xA5\xF0",  # msg 2
    ]

    for data in test_stream:
        parser.process_incoming_packet(data)


if __name__ == "__main__":
    main()
