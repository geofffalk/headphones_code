import struct

from .packet import Packet

class TemperatureStatusPacket(Packet):

    _FMT_PARSE = "<xxBBHHH"
    PACKET_LENGTH = struct.calcsize(_FMT_PARSE)
    _FMT_CONSTRUCT = "<2sBBHHH"
    _TYPE_HEADER = b"!U"
    _READABLE_STATUS = {
        0: 'Not Detected',
        1: 'Faulty reading',
        2: 'OK'
    }
    _POLARITY = {
        0: '+',
        1: '-'
    }

    def __init__(self, sensorStatus, polarity, temperatureChange, millisSinceLastReading, temperature):
        self._sensorStatus = sensorStatus
        self._polarity = polarity
        self._temperatureChange = temperatureChange
        self._millisSinceLastReading = millisSinceLastReading
        self._temperature = temperature
    
    def to_bytes(self):
        partial_packet = struct.pack(self._FMT_CONSTRUCT, self._TYPE_HEADER, self._sensorStatus, self._polarity, self._temperatureChange, self._millisSinceLastReading, self._temperature)
        return self.add_checksum(partial_packet)

    def __str__(self):
        return "Sensor Status: {}, temperatureChange {}{}, millisSinceLastReading {}, temperature {}".format(self._READABLE_STATUS[self._sensorStatus], self._POLARITY[self._polarity], self._temperatureChange, self._millisSinceLastReading, self._temperature)