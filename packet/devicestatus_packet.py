import struct

from packet import Packet

class DeviceStatusPacket(Packet):

    _FMT_PARSE = "<xxBHHB"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    _FMT_CONSTRUCT = "<2sBHHB"
    _TYPE_HEADER = b"!D"
    _READABLE_STATUS = {
        0: 'Empty',
        1: 'Initializing',
        2: 'Ready',
        3: 'Playing',
        4: 'Stopped',
        5: 'Error',
        6: 'TickerStarting',
        7: 'TickerComplete'
    }

    def __init__(self, deviceStatus, sessionId, lightPhase, errorCode):
        self._deviceStatus = deviceStatus
        self._sessionId = sessionId
        self._lightPhase = lightPhase
        self._errorCode = errorCode
    
    def to_bytes(self):
        partial_packet = struct.pack(self._FMT_CONSTRUCT, self._TYPE_HEADER, self._deviceStatus, self._sessionId, self._lightPhase, self._errorCode)
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Device Status: {}, session Id {}, light phase {}, error {}".format(self._READABLE_STATUS[self._deviceStatus], self._sessionId, self._lightPhase, self._errorCode)