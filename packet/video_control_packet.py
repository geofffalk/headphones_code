import struct

from .packet import Packet


class VideoControlPacket(Packet):
    """A packet controlling video playback"""

    _FMT_PARSE = "<xxBBx"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    # _FMT_CONSTRUCT doesn't include the trailing checksum byte.
    _FMT_CONSTRUCT = "<2sBB"
    _TYPE_HEADER = b"!V"

    def __init__(self, videoIndex, controlCode):
        self._videoIndex = videoIndex
        self._controlCode = controlCode

    def to_bytes(self):
        """Return the bytes needed to send this packet."""
        partial_packet = struct.pack(
            self._FMT_CONSTRUCT, self._TYPE_HEADER, self._videoIndex, self._controlCode
        )
        return self.add_checksum(partial_packet)
    
    def __str__(self):
        controlCodes = {
            3: 'start',
            2: 'resume',
            1: 'pause',
            0: 'stop'
        }
        return "Video Control packet: index {}, code {}".format(self._videoIndex, controlCodes[self._controlCode])

    @property
    def videoIndex(self):
        return self._videoIndex

# Control codes: 3 = START, 2 = RESUME, 1 = PAUSE, 0 = STOP
    @property
    def controlCode(self):
        return self._controlCode



# Register this class with the superclass. This allows the user to import only what is needed.
VideoControlPacket.register_packet_type()