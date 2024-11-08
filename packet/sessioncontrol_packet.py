import struct

from .packet import Packet


class SessionControlPacket(Packet):
    """A packet controlling session playback."""

    _FMT_PARSE = "<xxBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sB"
    _TYPE_HEADER = b"!X"

    def __init__(self, controlCode):
        self._controlCode = controlCode

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._controlCode
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        return "Session Control packet: {}".format(self._controlCode)

    @property
    def controlCode(self):
        return self._controlCode


# Register this class with the superclass. This allows the user to import only what is needed.
SessionControlPacket.register_packet_type()
