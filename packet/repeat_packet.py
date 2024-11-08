import struct

from packet import Packet


class RepeatPacket(Packet):
    """A packet containing an RGB color value."""

    _FMT_PARSE = "<xxBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBB"
    _TYPE_HEADER = b"!O"

    def __init__(self, repeatFrom, repetitions):
        self._repeatFrom = repeatFrom
        self._repetitions = repetitions

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._repeatFrom, self._repetitions
        )
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Repeat Phase: from {}, repetitions {}".format(
            self._repeatFrom, self._repetitions)
    
    def to_save_string(self):
        return "!O|{}|{}".format(self._repeatFrom, self._repetitions)

    @property
    def repeatFrom(self):
        return self._repeatFrom

    @property
    def repetitions(self):
        return self._repetitions


# Register this class with the superclass. This allows the user to import only what is needed.
RepeatPacket.register_packet_type()
