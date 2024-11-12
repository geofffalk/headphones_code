import struct

from .packet import Packet


class StopVideoPacket(Packet):
    """A packet controlling video playback"""

    _FMT_PARSE = "<xxx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2s"
    _TYPE_HEADER = b"!E"

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        return "Stop Video packet"

# Register this class with the superclass. This allows the user to import only what is needed.
StopVideoPacket.register_packet_type()