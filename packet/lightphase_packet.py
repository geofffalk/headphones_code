import struct

from packet import Packet


class LightPhasePacket(Packet):

    _FMT_PARSE = "<xx3B3BBBBHBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2s3B3BBBBHB"
    _TYPE_HEADER = b"!L"

    def __init__(self, startColor, endColor, startPosition, endPosition, pattern, duration, alternatingRate):
        if isinstance(startPosition, int):
            self._startPosition = startPosition
        else:
            raise ValueError(
                "Start position must be an int")
        if isinstance(endPosition, int):
            self._endPosition = endPosition
        else:
            raise ValueError(
                "Start position must be an int")
        if isinstance(pattern, int) and pattern > 0 and pattern < 5:
            self._pattern = pattern
        else:
            raise ValueError(
                "Unrecognised pattern - it should have value between 1-4")
        if isinstance(duration, int):
            self._duration = duration
        else:
            raise ValueError(
                "Duration must be an int")
        if isinstance(startColor, int):
            self._startColor = tuple(startColor.to_bytes("BBB", "big"))
        elif len(startColor) == 3 and all(0 <= c <= 255 for c in startColor):
            self._startColor = startColor
        else:
            raise ValueError(
                "Start color must be an integer 0xRRGGBB or a tuple(r,g,b)")
        if isinstance(endColor, int):
            self._endColor = tuple(endColor.to_bytes("BBB", "big"))
        elif len(endColor) == 3 and all(0 <= c <= 255 for c in endColor):
            self._endColor = endColor
        else:
            raise ValueError(
                "End color must be an integer 0xRRGGBB or a tuple(r,g,b)")
        if isinstance(alternatingRate, int):
            self._alternatingRate = alternatingRate
        else:
            raise ValueError(
                "Alternating rate must be an int")

    @classmethod
    def parse_private(cls, packet):
        params = struct.unpack(cls._FMT_PARSE, packet)
        startColor = params[0:3]
        endColor = params[3:6]
        startPosition = params[6]
        endPosition = params[7]
        pattern = params[8]
        duration = params[9]
        alternatingRate = params[10]
        return cls(startColor, endColor, startPosition, endPosition, pattern, duration, alternatingRate)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._startColor, self._endColor, self._startPosition, self._endPosition, self._alternatingRate
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Light Phase: Start color: {}, End color: {}, Start position: {}, End position: {}, Pattern: {}, Duration: {}, Alternating rate: {}".format(
            self._startColor, self._endColor, self._startPosition, self._endPosition, self._pattern, self._duration, self._alternatingRate)
    
    def to_save_string(self):
        return "!L|{}|{}|{}|{}|{}|{}|{}".format(self._startColor, self._endColor, self._startPosition, self._endPosition, self._pattern, self._duration, self._alternatingRate)

    @property
    def startColor(self):
        """A :class:`tuple` ``(red, green, blue)``
        """
        return self._startColor

    @property
    def endColor(self):
        return self._endColor

    @property
    def startPosition(self):
        return self._startPosition

    @property
    def endPosition(self):
        return self._endPosition

    @property
    def duration(self):
        return self._duration

    @property
    def pattern(self):
        return self._pattern

    @property
    def alternatingRate(self):
        return self._alternatingRate


# Register this class with the superclass. This allows the user to import only what is needed.
LightPhasePacket.register_packet_type()
