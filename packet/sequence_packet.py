import struct

from packet import Packet


class SequencePacket(Packet):

    _FMT_PARSE = "<xxBB10B10B10B10B10B10B10B10Bx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBB10B10B10B10B10B10B10B10B"
    _TYPE_HEADER = b"!Q"

    def __init__(self, leftSpeed, rightSpeed,  leftTop1, leftBottom1, rightTop1, rightBottom1, leftTop2, leftBottom2, rightTop2, rightBottom2):
        if isinstance(leftSpeed, int):
            self._leftSpeed = leftSpeed
        else:
            raise ValueError(
                "Left Speed must be an int")
        if isinstance(rightSpeed, int):
            self._rightSpeed = rightSpeed
        else:
            raise ValueError(
                "Right Speed must be an int")
        if len(leftTop1) == 10 and all(0 <= l <= 7 for l in leftTop1):
            self._leftTop1 = leftTop1
        else:
            raise ValueError(
                "{}: Left Top 1 must be an 10 member tuple of values between 0 and 7".format(leftTop1))
        if len(leftBottom1) == 10 and all(0 <= l <= 7 for l in leftBottom1):
            self._leftBottom1 = leftBottom1
        else:
            raise ValueError(
                "{}: Left Bottom 1 must be an 10 member tuple of values between 0 and 7".format(leftBottom1))

        if len(rightTop1) == 10 and all(0 <= r <= 7 for r in rightTop1):
            self._rightTop1 = rightTop1
        else:
            raise ValueError(
                "{}: Right Top 1 must be an 10 member tuple of values between 0 and 7".format(rightTop1))
        if len(rightBottom1) == 10 and all(0 <= r <= 7 for r in rightBottom1):
            self._rightBottom1 = rightBottom1
        else:
            raise ValueError(
                "{}: Right Bottom 1 must be an 10 member tuple of values between 0 and 7".format(rightBottom1))
        if len(leftTop2) == 10 and all(0 <= l <= 7 for l in leftTop2):
            self._leftTop2 = leftTop2
        else:
            raise ValueError(
                "{}: Left Top 2 must be an 10 member tuple of values between 0 and 7".format(leftTop2))
        if len(leftBottom2) == 10 and all(0 <= l <= 7 for l in leftBottom2):
            self._leftBottom2 = leftBottom2
        else:
            raise ValueError(
                "{}: Left Bottom 2 must be an 10 member tuple of values between 0 and 7".format(leftBottom2))

        if len(rightTop2) == 10 and all(0 <= r <= 7 for r in rightTop2):
            self._rightTop2 = rightTop2
        else:
            raise ValueError(
                "{}: Right Top 2 must be an 10 member tuple of values between 0 and 7".format(rightTop2))
        if len(rightBottom2) == 10 and all(0 <= r <= 7 for r in rightBottom2):
            self._rightBottom2 = rightBottom2
        else:
            raise ValueError(
                "{}: Right Bottom 2 must be an 10 member tuple of values between 0 and 7".format(rightBottom2))

    
    @classmethod
    def parse_private(cls, packet):
        params = struct.unpack(cls._FMT_PARSE, packet)
        position = params[0]
        leftSpeed = params[1]
        rightSpeed = params[2]
        leftTop1 = params[3:13]
        leftBottom1 = params[13:23]
        rightTop1 = params[23:33]
        rightBottom1 = params[33:43]
        leftTop2 = params[43:53]
        leftBottom2 = params[53:63]
        rightTop2 = params[63:73]
        rightBottom2 = params[73:83]
        return cls(position, leftSpeed, rightSpeed, leftTop1, leftBottom1, rightTop1,  rightBottom1,  leftTop2, leftBottom2, rightTop2, rightBottom2)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._position, self._leftSpeed, self._rightSpeed, self._leftTop1, self._leftBottom1, self._rightTop1, self._rightBottom1, self._leftTop2, self._leftBottom2, self._rightTop2, self._rightBottom2
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Sequence: Left Speed: {},  Right Speed: {}, Start position: {}, left top 1: {}, left bottom 1: {}, right top 1: {}, right bottom 1: {}, left top 2: {}, left bottom 2: {}, right top 2: {}, right bottom 2: {}".format(
            self._leftSpeed, self._rightSpeed, self._position, self._leftTop1, self._leftBottom1, self._rightTop1, self._rightBottom1, self._leftTop2, self._leftBottom2, self._rightTop2, self._rightBottom2)
    
    @property
    def leftSpeed(self):
        return self._leftSpeed

    @property
    def rightSpeed(self):
        return self._rightSpeed

    @property
    def leftTop1(self):
        return self._leftTop1

    @property
    def rightTop1(self):
        return self._rightTop1


    @property
    def leftBottom1(self):
        return self._leftBottom1

    @property
    def rightBottom1(self):
        return self._rightBottom1

    @property
    def leftTop2(self):
        return self._leftTop2

    @property
    def rightTop2(self):
        return self._rightTop2

    @property
    def leftBottom2(self):
        return self._leftBottom2

    @property
    def rightBottom2(self):
        return self._rightBottom2




# Register this class with the superclass. This allows the user to import only what is needed.
SequencePacket.register_packet_type()
