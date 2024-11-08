import struct

from .packet import Packet


class BrightnessPacket(Packet):
    """A packet containing an RGB color value."""

    _FMT_PARSE = "<xxBHx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBH"
    _TYPE_HEADER = b"!B"

    def __init__(self, brightness, duration):
        if isinstance(duration, int):
            self._duration = duration
        else:
            raise ValueError(
                "Duration must be an int representing deciseconds")
        if isinstance(brightness, int) and brightness >= 0 and brightness <= 255:
            self._brightness = brightness
        else:
            raise ValueError(
                "Brightness must be an int 0 - 255")

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._brightness, self._duration
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Animation: duration {} brightness {}".format(self._duration, self._brightness)
        
    def to_save_string(self):
        return "!B|{}|{}".format(self._duration, self._brightness)


    @property
    def duration(self):
        return self._duration
    
    @property
    def brightness(self):
        return self._brightness


# Register this class with the superclass. This allows the user to import only what is needed.
BrightnessPacket.register_packet_type()
