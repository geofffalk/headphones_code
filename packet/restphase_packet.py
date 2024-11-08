import struct

from .packet import Packet


class RestPhasePacket(Packet):
    """A packet containing an RGB color value."""

    _FMT_PARSE = "<xxHx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sH"
    _TYPE_HEADER = b"!R"

    def __init__(self, duration):
        if isinstance(duration, int):
            self._duration = duration
        else:
            raise ValueError(
                "Duration must be an int")

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._duration
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Rest Phase: duration {}".format(self._duration)
        
    def to_save_string(self):
        return "!R|{}".format(self._duration)


    @property
    def duration(self):
        return self._duration


# Register this class with the superclass. This allows the user to import only what is needed.
RestPhasePacket.register_packet_type()
