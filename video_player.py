#!/usr/bin/env python3
#
# omxplayer-sync
#
# Copyright 2016, Simon Josi
# Simon Josi me(at)yokto(dot)net
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of the GNU
# General Public License version 3 as published by
# the Free Software Foundation.
#

import re
import os
import sys
import math
import socket
import signal
import dbus
import json
import getpass
import itertools
import collections
import serial
from time import sleep, time
from subprocess import Popen
try:
    from subprocess import DEVNULL
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

SYNC_TOLERANCE = .05
SYNC_GRACE_TIME = 5
SYNC_JUMP_AHEAD = 3

OMXPLAYER = 'omxplayer'
OMXPLAYER_DBUS_ADDR='/tmp/omxplayerdbus.%s' % getpass.getuser()
PORT = 1666

#
# D-Bus player interface
#
class PlayerInterface():
    def _get_dbus_interface(self):
        try:
            bus = dbus.bus.BusConnection(
                open(OMXPLAYER_DBUS_ADDR).readlines()[0].rstrip())
            proxy = bus.get_object(
                'org.mpris.MediaPlayer2.omxplayer',
                '/org/mpris/MediaPlayer2',
                introspect=False)
            self.methods = dbus.Interface(
                proxy, 'org.mpris.MediaPlayer2.Player')
            self.properties = dbus.Interface(
                proxy, 'org.freedesktop.DBus.Properties')
            return True
        except Exception as e:
            print("WARNING: dbus connection could not be established")
            print(e)
            sleep(5)
            return False

    def initialize(self):
        sleep(10) # wait for omxplayer to appear on dbus
        return self._get_dbus_interface()

    def playPause(self):
        try:
            self.methods.Action(16)
            return True
        except Exception as e:
            print('Error playing / pausing video: {}'.format(e))
            return False

    def setPosition(self, seconds):
        try:
            self.methods.SetPosition(
                dbus.ObjectPath('/not/used'),
                dbus.Int64(seconds * 1000000))
        except Exception as e:
            print(e)
            return False

        return True

    def Position(self):
        try:
            return self.properties.Get(
                'org.mpris.MediaPlayer2.Player',
                'Position')
        except Exception as e:
            print('Error getting position: {}'.format(e))
            return False



class Logger:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.prefix = ""

    def set_prefix(self, prefix):
        self.prefix = prefix

    def info(self, message):
        print(f"[INFO] {self.prefix} {message}")

    def debug(self, message):
        if not self.verbose:
            return
        print(f"[DEBUG] {self.prefix} {message}")

    def warning(self, message):
        print(f"[WARNING] {self.prefix} {message}")

    def error(self, message):
        print(f"[ERROR] {self.prefix} {message}")

#
# OMXPlayer-Sync main class
#
class OMXPlayerSync():
    def __init__(self, is_conductor):
        self.serial = self.init_serial()
        self.controller = PlayerInterface()
        self.omxplayer_options = []
        self.filename = ''
        self.is_conductor = is_conductor
        self.position_local = 0.0
        self.position_local_oldage = 0.0
        self.position_local_oldage_count = 0
        self.position_conductor = 0.0
        self.filename_conductor = ''
        self.process = None
        self.logger = Logger(verbose = True)

        signal.signal(signal.SIGINT, self.kill_omxplayer_and_exit)

    def run(self):
        os.system("sudo fbi -a -noverbose -T 1 -t 1 /home/geoff/headphones_code/logo.png")
        
        self.omxplayer_options.append("--loop")
        self.omxplayer_options.append("-o %s" % "both")
        self.omxplayer_options.append('--no-keys')
        self.omxplayer_options.append('--no-osd')

        while True:
            if (self.filename):
                self.play_file(self.filename)
            elif not self.is_conductor:
                self.read_position_conductor()
                self.filename = self.filename_conductor
                
    
    def set_filename(self, filename):
        self.filename = filename

    def play_file(self, filename):
        if not os.path.isfile(filename):
            print("WARNING: %s file not found" % filename)
            return
        self._running = True
        self.position_local = 0.0
        self.position_local_oldage = 0.0
        self.position_local_oldage_count = 0

        last_frame_local, current_frame_local = 0, 0
        if not self.is_conductor:
            last_frame_conductor, current_frame_conductor = 0, 0

        if self.is_conductor:
            self.send_position_local()
        
        self.process = Popen([OMXPLAYER] \
            + list(itertools.chain(*map(lambda x: x.split(' '), self.omxplayer_options))) \
            + [self.filename],
            preexec_fn=os.setsid, stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)
        print(f"Process is {self.process}") 

        self.controller.initialize()

        if not self.read_position_local():
            print("WARNING: omxplayer did not start. Try to test with `omxplayer -s OPTIONS`")
            self.kill_omxplayer_and_exit()

        if not self.is_conductor:
            wait_for_sync = False
            wait_after_sync = False
            deviations = collections.deque(maxlen=10)

        while self._running:
            if not self.is_conductor:
                self.read_position_conductor()
                if wait_for_sync:
                    sync_timer = time()

            if not self.read_position_local():
                break

            if self.hangup_detected():
                break

            current_frame_local = math.modf(self.position_local)[0]*100/4
            if not self.is_conductor:
                current_frame_conductor = math.modf(self.position_conductor)[0]*100/4

            if self.is_conductor:
                self.send_position_local()
                sys.stdout.write("local: %.2f %.0f\n" %
                    (self.position_local, current_frame_local))

            if not self.is_conductor:
                if self.filename != self.filename_conductor:
                    self.filename = self.filename_conductor
                    break

                deviation = self.position_conductor - self.position_local
                deviations.append(deviation)
                median_deviation = self.median(list(deviations))

                self.logger.debug("local: %.2f %.0f conductor: %.2f %.0f deviation: %.2f median_deviation: %.2f filename: %s\n" % (
                    self.position_local,
                    current_frame_local,
                    self.position_conductor,
                    current_frame_conductor,
                    deviation,
                    median_deviation,
                    self.filename))

                if wait_for_sync:
                    while True:
                        if abs(deviation) - (time() - sync_timer) < 0:
                            self.logger.debug("we are sync, play...")
                            if not self.controller.playPause():
                                break

                            wait_for_sync = False
                            wait_after_sync = time()
                            break
                    continue

                if wait_after_sync:                
                    if (time() - wait_after_sync) > SYNC_GRACE_TIME:
                         wait_after_sync = False

                    continue

                if abs(median_deviation) > SYNC_TOLERANCE \
                and self.position_local > SYNC_GRACE_TIME \
                and self.position_conductor > SYNC_GRACE_TIME:
                    self.logger.debug("jump to %.2f" % (self.position_conductor + SYNC_JUMP_AHEAD))
                    self.logger.debug("enter pause...")
                    if not self.controller.playPause():
                        break
                    if not self.controller.setPosition(self.position_conductor + SYNC_JUMP_AHEAD):
                        break

                    wait_for_sync = True
                    wait_after_sync = time()

            if self.is_conductor:
                sleep(1)

        self.kill_omxplayer()
    
    def play_pause(self):
        self.controller.playPause()
        if self.is_conductor:
            self.send_command('play_pause')

    def stop(self):
        self._running = False
        self.filename = None
        if self.is_conductor:
            sleep(0.2)
            self.send_position_local()
            sleep(0.2)
        # if self.is_conductor:
        #     self.send_command('stop')
        # else:
        #     self.filename_conductor = None

    def send_command(self, command): 
        data = {
	     "command": command,
        }
        message = json.dumps(data).encode("utf-8")
        sleep(0.2)
        self.serial.write(message)
        sleep(0.2)
        self.logger.debug(f"Writing command: {message}")

    def read_position_local(self):
        position_local = self.controller.Position()
        if position_local:
            self.position_local = float(position_local)/1000000
        else:
            return False

        return True

    def hangup_detected(self):
        self.position_local_oldage_count += 1
        if self.position_local_oldage_count == 200:
            if self.position_local_oldage == self.position_local:
                return True

            self.position_local_oldage = self.position_local
            self.position_local_oldage_count = 0

        return False

    def init_serial(self):
        ser = serial.Serial("/dev/ttyS0", 115200)
        return ser

    def kill_omxplayer(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except Exception as e:
                # os.system('sudo killall omxplayer.bin')
                print('Failed to kill omxplayer: {}'.format(e))
                pass
            try:
                self.process.wait()
            except:
                pass

    def kill_omxplayer_and_exit(self, *args):
        self.logger.debug('Killing and exiting')
        self.kill_omxplayer()
        sys.exit(0)

    #
    # conductor specific
    #

    def send_position_local(self):
        data = {
	     "video_file": self.filename,
	     "pos": self.position_local
        }
        message = json.dumps(data).encode("utf-8")
        # message = ("%s%%%s" % (str(self.position_local),  self.filename)).encode('utf-8')
        self.serial.write(message)
        self.logger.debug(f"Writing status: {message}")

    #
    # follower specific
    #
    def read_position_conductor(self):
        try:
            data = self.serial.read()
            sleep(0.03)
            if (self.serial.inWaiting() > 0):
                data += self.serial.read(self.serial.inWaiting())
            # decoded = data[0].decode('utf-8').split('%', 1)
            decoded = data.decode("utf-8")
            # self.logger.debug(f"Data read from conductor: {decoded}")
            obj = json.loads(decoded)
            self.logger.debug(f"Json read from conductor: {obj}")
            if "command" in obj:
                if obj["command"] == 'play_pause':
                    self.controller.playPause()
                # elif obj["command"] == 'stop':
                #     self.stop()
            else:
                self.position_conductor = float(obj["pos"])
                self.filename_conductor = obj["video_file"]
        except Exception as e:
            self.logger.error(e)
            pass

    def median(self, lst):
        quotient, remainder = divmod(len(lst), 2)
        if remainder:
            return sorted(lst)[quotient]
        return float(sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.0)

# if __name__ == '__main__':
#     OMXPlayerSync().run()
