import struct

from packet import Packet


class AnimationPacket(Packet):
    """A packet containing an RGB color value."""

    _FMT_PARSE = "<xxBHx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBH"
    _TYPE_HEADER = b"!A"

    def __init__(self, animationCode, duration):
        if isinstance(duration, int):
            self._duration = duration
        else:
            raise ValueError(
                "Duration must be an int")
        if isinstance(animationCode, int):
            self._animationCode = animationCode
        else:
            raise ValueError(
                "Start position must be an int")

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._animationCode, self._duration
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Animation: duration {} animationCode {}".format(self._animationCode)
        
    def to_save_string(self):
        return "!A|{}|{}".format(self._duration, self._animationCode)


    @property
    def duration(self):
        return self._duration
    
    @property
    def animationCode(self):
        return self._animationCode


# Register this class with the superclass. This allows the user to import only what is needed.
AnimationPacket.register_packet_type()
