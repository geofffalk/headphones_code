import struct

from .packet import Packet


class SensorControlPacket(Packet):
    """A packet controlling the sensor reading. 0 for off, 1 for on"""

    _FMT_PARSE = "<xxBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBB"
    _TYPE_HEADER = b"!Y"

    def __init__(self, controlCode, pollRateInMillis):
        self._controlCode = controlCode
        self._pollRateInMillis = pollRateInMillis

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._controlCode, self._pollRateInMillis
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        return "Sensor Control packet: {}, poll rate in millis: {}".format(self._controlCode, self._pollRateInMillis)

    @property
    def controlCode(self):
        return self._controlCode
    

    @property
    def pollRateInMillis(self):
        return self._pollRateInMillis


# Register this class with the superclass. This allows the user to import only what is needed.
SensorControlPacket.register_packet_type()
