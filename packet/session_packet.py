import struct

from .packet import Packet


class SessionPacket(Packet):
    """A packet containing the total number of phases."""

    _FMT_PARSE = "<xxBBBBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBBBBB"
    _TYPE_HEADER = b"!S"

    def __init__(self, phaseCountLeft, phaseCountRight, speedLeft, speedRight, intensity):
        if isinstance(phaseCountLeft, int):
            self._phaseCountLeft = phaseCountLeft
        else:
            raise ValueError(
                "phaseCountLeft must be an int")
        if isinstance(phaseCountRight, int):
            self._phaseCountRight = phaseCountRight
        else:
            raise ValueError(
                "phaseCountRight must be an int")
        if isinstance(speedLeft, int):
            self._speedLeft = speedLeft
        else:
            raise ValueError(
                "speedLeft must be an int")
        if isinstance(speedRight, int):
            self._speedRight = speedRight
        else:
            raise ValueError(
                "speedRight must be an int")
        if isinstance(intensity, int)  and intensity >= 0 and intensity <= 4:
            self._intensity = intensity
    
    # @classmethod
    # def parse_private(cls, packet):
    #     print('Creating Session Packet with packet {}'.format(packet))
    #     params = struct.unpack(cls._FMT_PARSE, packet)
    #     print('Creating Session Packet with params {}'.format(params))
    #     phaseCountLeft = params[0]
    #     phaseCountRight = params[1]
    #     speedLeft = params[2]
    #     speedRight = params[3]
    #     intensity = params[4]
    #     return cls(phaseCountLeft, phaseCountRight, speedLeft, speedRight, intensity)

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._phaseCountLeft, self._phaseCountRight, self._speedLeft, self._speedRight, self._intensity
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        return "Session with {} left phases at speed {}, and {} right phases at speed {} with intensity {}".format(self._phaseCountLeft, self._speedLeft, self._phaseCountRight, self._speedRight, self._intensity)

    @property
    def phaseCountLeft(self):
        return self._phaseCountLeft

    @property
    def phaseCountRight(self):
        return self._phaseCountRight

    @property
    def speedLeft(self):
        return self._speedLeft

    @property
    def speedRight(self):
        return self._speedRight

    @property
    def intensity(self):
        return self._intensity



# Register this class with the superclass. This allows the user to import only what is needed.
SessionPacket.register_packet_type()
