import struct

from .packet import Packet


class TickerPacket(Packet):

    _FMT_PARSE = "<xxBBB8B8BBBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBBB8B8BBBB"
    _TYPE_HEADER = b"!T"

    def __init__(self, speed, length, pattern, left, right, offsetFront, offsetBack, brightness):
        if isinstance(speed, int):
            self._speed = speed
        else:
            raise ValueError(
                "Speed must be int")
        if isinstance(length, int):
            self._length = length
        else:
            raise ValueError(
                "Length must be int")
        if isinstance(pattern, int) and (pattern >= 0 and pattern <= 9):
            self._pattern = pattern
        else:
            raise ValueError(
                "pattern must be int between 0 and 9")
        if len(left) == 8 and all(0 <= l <= 7 for l in left):
            self._left = left
        else:
            raise ValueError(
                "Left must be an 8 member tuple of values between 0 and 7")
        if len(right) == 8 and all(0 <= l <= 7 for l in right):
            self._right = right
        else:
            raise ValueError(
                "Right must be an 8 member tuple of values between 0 and 7")
        if isinstance(offsetFront, int) and (offsetFront < 10):
            self._offsetFront = offsetFront
        else:
            raise ValueError(
                "offsetFront must be an int lower than 10"
            )
        if isinstance(offsetBack, int) and (offsetBack < 10):
            self._offsetBack = offsetBack
        else:
            raise ValueError(
                "offsetBack must be an int lower than 10"
            )
        if isinstance(brightness, int):
            self._brightness = brightness
        else:
            raise ValueError(
                "brightness must be an int lower than 255"
            )

    @classmethod
    def parse_private(cls, packet):
        params = struct.unpack(cls._FMT_PARSE, packet)
        speed = params[0]
        length = params[1]
        pattern = params[2]
        left = params[3:11]
        right = params[11:19]
        offsetFront = params[19]
        offsetBack = params[20]
        brightness = params[21]
        return cls(speed, length, pattern, left, right, offsetFront, offsetBack, brightness)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._speed, self._length, self._pattern, self._left, self._right, self._offsetFront, self._offsetBack, self._brightness
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Ticker speed {} length {}, pattern {}, Left: {}, Right: {}, Offset front: {}, Offset back: {}, Brightness {}".format(
            self._speed, self._length, self._pattern, self._left, self._right, self._offsetFront, self._offsetBack, self._brightness)
    
    def to_save_string(self):
        return "!T|{}|{}|{}|{}|{}|{}|{}|{}".format(self._speed, self._length, self._pattern, self._left, self._right, self._offsetFront, self._offsetBack, self._brightness)

    @property
    def speed(self):
        return self._speed

    @property
    def length(self):
        return self._length

    @property
    def pattern(self):
        return self._pattern

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right
    
    @property
    def offsetFront(self):
        return self._offsetFront

    @property
    def offsetBack(self):
        return self._offsetBack

    @property
    def brightness(self):
        return self._brightness

# Register this class with the superclass. This allows the user to import only what is needed.
TickerPacket.register_packet_type()
