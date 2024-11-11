import struct

from .packet import Packet


class StaticLightPacket(Packet):

    _FMT_PARSE = "<xx10B10B10B10BHBBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2s10B10B10B10BHBBB"
    _TYPE_HEADER = b"!I"

    def __init__(self, leftTop, leftBottom, rightTop, rightBottom, duration, leftRepetitions, rightRepetitions, brightness):
        if len(leftTop) == 10 and all(0 <= l <= 7 for l in leftTop):
            self._leftTop = leftTop
        else:
            raise ValueError(
                "{}: Left Top must be an 10 member tuple of values between 0 and 7".format(leftTop))
        if len(leftBottom) == 10 and all(0 <= l <= 7 for l in leftBottom):
            self._leftBottom = leftBottom
        else:
            raise ValueError(
                "{}: Left Bottom must be an 10 member tuple of values between 0 and 7".format(leftBottom))

        if len(rightTop) == 10 and all(0 <= r <= 7 for r in rightTop):
            self._rightTop = rightTop
        else:
            raise ValueError(
                "{}: Right Top must be an 10 member tuple of values between 0 and 7".format(rightTop))
        if len(rightBottom) == 10 and all(0 <= r <= 7 for r in rightBottom):
            self._rightBottom = rightBottom
        else:
            raise ValueError(
                "{}: Right Bottom must be an 10 member tuple of values between 0 and 7".format(rightBottom))
        if isinstance(leftRepetitions, int) and leftRepetitions > 0 and leftRepetitions < 5:
            self._leftRepetitions = leftRepetitions
        else:
            raise ValueError(
                "{}: leftRepetitions is meant to be an int between 1 and 4".format(leftRepetitions))
        if isinstance(rightRepetitions, int) and rightRepetitions > 0 and rightRepetitions < 5:
            self._rightRepetitions = rightRepetitions
        else:
            raise ValueError(
                "{}: rightRepetitions is meant to be an int between 1 and 4".format(rightRepetitions))
        if isinstance(duration, int):
            self._duration = duration
        else:
            raise ValueError(
                "Duration must be an int")
        if isinstance(brightness, int):
            self._brightness = brightness
        else:
            raise ValueError(
                "Brightness must be an int between 0 and 255")
        print('Static made')

    @classmethod
    def parse_private(cls, packet):
        params = struct.unpack(cls._FMT_PARSE, packet)
        leftTop = params[0:10]
        leftBottom = params[10:20]
        rightTop = params[20:30]
        rightBottom = params[30:40]
        duration = params[40]
        leftRepetitions = params[41]
        rightRepetitions = params[42]
        brightness = params[43]
        return cls(leftTop, leftBottom, rightTop, rightBottom, duration, leftRepetitions, rightRepetitions, brightness)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._leftTop, self._leftBottom, self._rightTop,  self._rightBottom, self._duration, self._leftRepetitions, self._rightRepetitions, self._brightness
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Static light: Left Top: {}, Left Bottom: {}, Right Top: {}, Right Bottom {}, duration: {}, intensity {}, leftRepetitions {}, rightRepetitions {}".format(
            self._leftTop, self._leftBottom, self._rightTop, self._rightBottom, self._duration, self._leftRepetitions, self._rightRepetitions)
    
    def to_save_string(self):
        return "!I|{}|{}|{}|{}|{}|{}|{}".format(self._leftTop, self._leftBottom, self._rightTop, self._rightBottom, self._duration, self._leftRepetitions, self._rightRepetitions)

    @property
    def leftTop(self):
        return self._leftTop

    @property
    def rightTop(self):
        return self._rightTop


    @property
    def leftBottom(self):
        return self._leftBottom

    @property
    def rightBottom(self):
        return self._rightBottom

    @property
    def duration(self):
        return self._duration

    @property
    def leftRepetitions(self):
        return self._leftRepetitions

    @property
    def rightRepetitions(self):
        return self._rightRepetitions

    @property
    def brightness(self):
        return self._brightness

# Register this class with the superclass. This allows the user to import only what is needed.
StaticLightPacket.register_packet_type()
