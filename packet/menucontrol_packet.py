import struct

from .packet import Packet

class MenuControlPacket(Packet):
    """A packet that controls the sensor reading. 0 for off, 1 for on"""

    _FMT_PARSE = "<xxBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sB"
    _TYPE_HEADER = b"!M"

    def __init__(self, menuIndex):
        self._menuIndex = menuIndex

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._menuIndex
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        return "Menu Control packet: {}, poll rate in millis: {}".format(self._menuIndex)

    @property
    def menuIndex(self):
        return self._menuIndex
    


# Register this class with the superclass. This allows the user to import only what is needed.
MenuControlPacket.register_packet_type()
