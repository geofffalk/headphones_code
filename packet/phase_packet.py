import struct

from .packet import Packet


class PhasePacket(Packet):

    _FMT_PARSE = "<xxB10B10Bx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sB10B10B"
    _TYPE_HEADER = b"!P"

    def __init__(self, side, top, bottom):
        if isinstance(side, int) and (side == 0 or side == 1):
            self._side = side
        else:
            raise ValueError(
                "Side must be 0 (left) or 1 (right)")
        if len(top) == 10 and all(0 <= l <= 7 for l in top):
            self._top = top
        else:
            raise ValueError(
                "{}:Top must be an 10 member tuple of values between 0 and 7".format(top))
        if len(bottom) == 10 and all(0 <= l <= 7 for l in bottom):
            self._bottom = bottom
        else:
            raise ValueError(
                "{}: Bottom must be an 10 member tuple of values between 0 and 7".format(bottom))

    @classmethod
    def parse_private(cls, packet):
        params = struct.unpack(cls._FMT_PARSE, packet)
        side = params[0]
        top = params[1:11]
        bottom = params[11:21]
        return cls(side, top, bottom)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._side, self._top, self._bottom
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Phase on side {}: Top: {}, Bottom: {}".format(
            self._side, self._top, self._bottom)
    
    def to_save_string(self):
        return "!P|{}|{}|{}".format(self._side, self._top, self._bottom)

    @property
    def side(self):
        return self._side
    @property
    def top(self):
        return self._top

    @property
    def bottom(self):
        return self._bottom


# Register this class with the superclass. This allows the user to import only what is needed.
PhasePacket.register_packet_type()
