
from packet.staticlight_packet import StaticLightPacket
from packet.devicestatus_packet import DeviceStatusPacket
from packet.sensorcontrol_packet import SensorControlPacket
from packet.ticker_packet import TickerPacket
from packet.brightness_packet import BrightnessPacket
from packet.color_update_packet import ColorUpdatePacket
from packet.packet import Packet
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.color import BLUE
import time
import board
import neopixel_spi as neopixel

class DisplayController:

    NANOS_PER_MS = 1000000
    MS_PER_SECOND = 1000
    DS_PER_SECOND = 10
    NUM_PIXELS = 10
    PIXEL_ORDER = neopixel.GRB
    spi = board.SPI()
    pixels = neopixel.NeoPixel_SPI(spi, NUM_PIXELS,
                                pixel_order=PIXEL_ORDER, auto_write=False)

    staticLeftSequence = []
    staticLeftSequenceCursor = 0
    staticRightSequence = []
    staticRightSequenceCursor = 0
    pulseGapMillis = 200
    deviceStatus = DeviceStatusPacket(0, 0, 0, 0)
    isDeviceStatusChanged = True
    tickerDuration= 0
    lastTickTime = 0
    lastLeftStaticTickTime = 0
    lastRightStaticTickTime = 0
    tickerLeft = [0]
    tickerRight= [0]
    tickerPattern = (1)
    patternCursor = 0
    tickerProgress = 0
    tickerLength = 0
    tickerOffsetFront = 0
    tickerOffsetBack = 0
    pixelLeftStart = []
    pixelRightStart = []
    isOpeningAnimationComplete = False

    baselineBrightness = 255
    tempBrightness = 255
    currentBrightness = baselineBrightness
    tempBrightnessDuration = 0
    tempBrightnessStartTime = 0

    tickerPatternMap = {
        0: (1, 1),
        1: (1,1,-1),
        2: (1,1,0),
        3: (1,1,0,-1,0),
        4: (1,0,1,0,-1,-1,1,1),
        5: (1,0,1,0,1,1,-1,1),
        6: (2,0,0,6,0,0,-8,0),
        7: (4,0,0,8,0,0,-10,0),
        8: (1, 1),
        9: (1, 1)
    }

    colorMap = {
        0: (0, 0, 0),
        1: (1, 0, 0),
        2: (1, 1, 0),
        3: (0, 1, 0),
        4: (0, 1, 1),
        5: (0, 0, 1),
        6: (1, 0, 1),
        7: (1, 1, 1)
    }

    # 0 = standby, 1 = static initialised, 2 = static playing, 3 = ticker initialised, 4 = ticket playing
    PS_STANDBY = 0
    PS_STATIC_READY = 1
    PS_STATIC_PLAYING = 2
    PS_TICKER_READY = 3
    PS_TICKER_PLAYING = 4
    PS_IDLE = 5
    playState = PS_STANDBY
             
    def __init__(self):
        openingAnimation = Comet(self.pixels, speed=0.15, color=BLUE, tail_length=3)
        openingAnimation.add_cycle_complete_receiver(self.onOpeningAnimationComplete)
        openingAnimation.animate()
        self._running = True

    def update(self, packet: Packet): 
        if isinstance(packet, BrightnessPacket): 
            self.updateBrightness(packet)
        elif isinstance(packet, StaticLightPacket):
            self.showStaticLights(packet)
        elif isinstance(packet, TickerPacket):
            self.showTicker(packet)
        elif isinstance(packet, ColorUpdatePacket):
            self.updateColor(packet)
    
    def terminate(self):
        self._running = False
    
    def run(self):
        while self._running:
            self.tickTime = self.monotonic_ms()
            self.currentBrightness = self.tempBrightness if self.tempBrightness != self.baselineBrightness and (self.tempBrightnessDuration == 0 or self.tickTime - self.tempBrightnessStartTime < self.tempBrightnessDuration) else self.baselineBrightness
            if self.playState == self.PS_TICKER_READY or self.playState == self.PS_TICKER_PLAYING:
                if self.playState == self.PS_TICKER_READY or self.tickTime - self.lastTickTime > self.tickerDuration:
                    self.playState = self.PS_TICKER_PLAYING
                    self.lastTickTime = self.tickTime
                    patternCursor = 0 if patternCursor >= len(self.tickerPattern) - 1 else patternCursor + 1
                    step = self.tickerPattern[patternCursor]
                    if step != 0:
                        # tickerLeftTop = tickerLeftTop[-step:] + tickerLeftTop[:-step]
                        self.tickerLeft = self.tickerLeft[-step:] + self.tickerLeft[:-step]
                        #tickerRightTop = tickerRightTop[-step:] + tickerRightTop[:-step]
                        self.tickerRight = self.tickerRight[-step:] + self.tickerRight[:-step]
                        self.tickerProgress += step
                        if self.tickerProgress >= self.tickerLength:
                            self.playState = self.PS_IDLE
                            self.updateDeviceStatus(7)
                    if self.playState == self.PS_TICKER_PLAYING:
                        frontMargin = [0 for i in range(self.tickerOffsetFront)]
                        backMargin = [0 for i in range(self.tickerOffsetBack)]
                        left = frontMargin + self.tickerLeft[-self.tickerVisibleLength:] + backMargin
                        right = frontMargin + self.tickerRight[-self.tickerVisibleLength:] + backMargin, frontMargin + self.tickerRight[-self.tickerVisibleLength:] + backMargin
                        for i in range(self.NUM_PIXELS / 2):
                            self.pixels[(self.NUM_PIXELS / 2) + i] = self.apply_brightness(self.colorMap[left[i]])
                        for i in range(self.NUM_PIXELS / 2):
                            self.pixels[(self.NUM_PIXELS / 2) - 1 - i] = self.apply_brightness(self.colorMap[right[i]])
                        self.pixels.show()
                    else:
                        self.pixels.fill((0, 0, 0))
                    self.pixels.show()
            elif self.playState == self.PS_STATIC_READY or self.playState == self.PS_STATIC_PLAYING:
                if self.playState == self.PS_STATIC_READY or self.tickTime - self.lastLeftStaticTickTime > self.staticLeftSequence[self.staticLeftSequenceCursor]:
                    self.lastLeftStaticTickTime = self.tickTime
                    if self.staticLeftSequenceCursor >= len(self.staticLeftSequence) - 1:
                        for i in range(self.NUM_PIXELS / 2):
                            self.pixels[(self.NUM_PIXELS / 2) + i] = (0, 0, 0)
                        self.pixels.show()
                    else:
                        if self.staticLeftSequenceCursor % 2 == 0:
                            for i in range(self.NUM_PIXELS / 2):
                                self.pixels[(self.NUM_PIXELS / 2) + i] = self.apply_brightness(self.pixelLeftStart[i])
                            self.pixels.show()
                        else:
                            for i in range(self.NUM_PIXELS / 2):
                                self.pixels[(self.NUM_PIXELS / 2) + i] = (0, 0, 0)
                            self.pixels.show()
                        self.staticLeftSequenceCursor += 1
                if self.playState == self.PS_STATIC_READY or self.tickTime - self.lastRightStaticTickTime > self.staticRightSequence[staticRightSequenceCursor]:
                    self.lastRightStaticTickTime = self.tickTime
                    if self.staticRightSequenceCursor >= len(self.staticRightSequence) - 1:
                        for i in range(self.NUM_PIXELS / 2):
                            self.pixels[(self.NUM_PIXELS / 2) - 1 - i] = (0, 0, 0)
                        self.pixels.show()
                    else:
                        if staticRightSequenceCursor % 2 == 0:
                            for i in range(self.NUM_PIXELS / 2):
                                self.pixels[(self.NUM_PIXELS / 2) - 1 - i]  = self.apply_brightness(self.pixelRightStart[i])
                            self.pixels.show()
                        else:
                            for i in range(self.NUM_PIXELS / 2):
                                self.pixels[(self.NUM_PIXELS / 2) - 1 - i] = (0, 0, 0)
                            self.pixels.show()
                        staticRightSequenceCursor += 1
                if self.staticRightSequenceCursor >= len(self.staticRightSequence) - 1 and self.staticLeftSequenceCursor >= len(self.staticLeftSequence) - 1:
                # if self.staticLeftSequenceCursor >= len(self.staticLeftSequence) - 1:
                    self.playState = self.PS_STANDBY
                else:
                    self.playState = self.PS_STATIC_PLAYING

            if self.isDeviceStatusChanged:
                # print('Updating device status: {}'.format(deviceStatus))
                try:
                    statusBytes = self.deviceStatus.to_bytes()
                    # uart_server.write(statusBytes)
                    self.isDeviceStatusChanged = False
                except OSError:
                    pass


    def updateDeviceStatus(self, state):
        self.deviceStatus = DeviceStatusPacket(state, 0, 0, 0)
        self.isDeviceStatusChanged = True

    def hideAllPixels(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()

    def apply_brightness(self, color):
        return (
            int(color[0] * self.currentBrightness),
            int(color[1] * self.currentBrightness),
            int(color[2] * self.currentBrightness),
        )

    def monotonic_ms(self):
        return int(time.monotonic() * self.MS_PER_SECOND)

    def twoByteCeil(self, input):
        return input if input > -32768 and input < 65535 else 0

    def onOpeningAnimationComplete(self, anim):
        self.isOpeningAnimationComplete = True
    
    def updateBrightness(self, packet: BrightnessPacket):
        if packet.duration == 0:
            self.baselineBrightness = packet.brightness
            self.currentBrightness = self.baselineBrightness
        else:
            self.tempBrightness = packet.brightness
            self.tempBrightnessDuration = packet.duration * 100
            self.tempBrightnessStartTime = self.monotonic_ms()
    
    def showStaticLights(self, packet: StaticLightPacket):
        pixelLeftStart = []
        pixelRightStart = []
        # bottom
        for i in range(10):
            leftVal = packet.leftBottom[i]
            rightVal = packet.rightBottom[i]
            leftColor = self.colorMap[leftVal]
            rightColor = self.colorMap[rightVal]
            pixelLeftStart.append(leftColor)
            pixelRightStart.append(rightColor)

        self.staticLeftSequenceCursor = 0
        self.staticLeftSequence = [0]
        gap = 0 if packet.leftRepetitions == 1 else self.pulseGapMillis
        leftPulseDuration = ((packet.duration * 100) // packet.leftRepetitions) - gap
        for i in range(packet.leftRepetitions):
            self.staticLeftSequence += [leftPulseDuration, self.pulseGapMillis]
        self.staticRightSequenceCursor = 0
        self.staticRightSequence = [0]
        gap = 0 if packet.rightRepetitions == 1 else self.pulseGapMillis
        rightPulseDuration = ((packet.duration * 100) // packet.rightRepetitions) - gap
        for i in range(packet.rightRepetitions):
            self.staticRightSequence += [rightPulseDuration, self.pulseGapMillis]
        self.playState = self.PS_STATIC_READY
        self.tempBrightness = self.baselineBrightness if packet.brightness == 0 else packet.brightness
        self.updateDeviceStatus(3)
    
    def showTicker(self, packet: TickerPacket):
        self.tickerPattern = self.tickerPatternMap[packet.pattern]
        self.patternCursor = 0
        left = []
        right = []
        colCursor = 0
        tickerOffsetFront = packet.offsetFront
        tickerOffsetBack = packet.offsetBack
        tickerVisibleLength = 10 - tickerOffsetFront - tickerOffsetBack
        self.tempBrightness = self.baselineBrightness if packet.brightness == 0 else packet.brightness
        for i in range(packet.length):
            left.append(packet.left[colCursor])
            right.append(packet.right[colCursor])
            colCursor = colCursor + 2 if colCursor < len(packet.left) - 2 else 0
        left += [0] * tickerVisibleLength
        right += [0] * tickerVisibleLength
        self.tickerLength = packet.length + tickerVisibleLength
        self.tickerLeft = left
        self.tickerRight = right
        self.tickerDuration = packet.speed * self.DS_PER_SECOND
        self.tickerProgress = 0
        self.updateDeviceStatus(6)
        self.playState = self.PS_TICKER_READY

def updateColor(self, packet: ColorUpdatePacket):
    if self.playState == self.PS_TICKER_READY or self.playState == self.PS_TICKER_PLAYING:
        self.tickerLeft = list(map(lambda x: packet.leftColor if x != 0 else 0, self.tickerLeft))
        self.tickerRight = list(map(lambda x: packet.rightColor if x != 0 else 0, self.tickerRight))
    elif self.playState == self.PS_STATIC_READY or self.playState == self.PS_STATIC_PLAYING or self.playState == self.PS_STANDBY:
        self.pixelLeftStart = list(map(lambda x: self.colorMap[0] if x[0] == 0 and x[1] == 0 and x[2] == 0 else self.colorMap[packet.leftColor], self.pixelLeftStart))
        self.pixelRightStart = list(map(lambda x: self.colorMap[0] if x[0] == 0 and x[1] == 0 and x[2] == 0 else self.colorMap[packet.rightColor], self.pixelRightStart))
        self.staticLeftSequenceCursor = 0
        self.staticRightSequenceCursor = 0
        self.playState = self.PS_STATIC_READY
    
   
        