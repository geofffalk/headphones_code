import struct

from adafruit_bluefruit_connect.packet import Packet


class ColorUpdatePacket(Packet):

    _FMT_PARSE = "<xxBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBB"
    _TYPE_HEADER = b"!C"

    def __init__(self, leftColor, rightColor):
        if isinstance(leftColor, int) and (0 <= leftColor < 8):
            self._leftColor = leftColor
        else:
            raise ValueError(
                "left color must be an int between 0 and 7"
            )
        if isinstance(rightColor, int) and (0 <= rightColor < 8):
            self._rightColor = rightColor
        else:
            raise ValueError(
                "right color must be an int between 0 and 7"
            )

    @classmethod
    def parse_private(cls, packet):
        params = struct.unpack(cls._FMT_PARSE, packet)
        leftColor = params[0]
        rightColor = params[1]
        return cls(leftColor, rightColor)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._color
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Color update left {} right {}".format(
            self._leftColor, self._rightColor)
    
    def to_save_string(self):
        return "!C|{}|{}".format(self._leftColor, self._rightColor)

    @property
    def leftColor(self):
        return self._leftColor
    
    @property
    def rightColor(self):
        return self._rightColor

# Register this class with the superclass. This allows the user to import only what is needed.
ColorUpdatePacket.register_packet_type()
