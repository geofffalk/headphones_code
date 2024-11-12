import struct

from .packet import Packet


class PlayVideoPacket(Packet):
    """A packet controlling video playback"""

    _FMT_PARSE = "<xxBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sB"
    _TYPE_HEADER = b"!V"

    def __init__(self, videoIndex):
        self._videoIndex = videoIndex

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._videoIndex
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        return "Play Video packet: index {}".format(self._videoIndex)

    @property
    def videoIndex(self):
        return self._videoIndex


# Register this class with the superclass. This allows the user to import only what is needed.
PlayVideoPacket.register_packet_type()