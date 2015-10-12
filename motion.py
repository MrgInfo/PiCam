#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### BEGIN INIT INFO
# Provides:          motion
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Detecting motion
### END INIT INFO

"""Daemon for detecting motion.
"""

import datetime
import os
import time
import platform
from fractions import Fraction

import picamera
import picamera.array

from utils import settings
from utils.daemons import DaemonBase, init
from utils.database import Database

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds


class MotionCapture:
    """Detect motion on PiCam and capture short video."""

    threshold = 10  # How Much pixel changes
    sensitivity = 100  # How many pixels change
    nightISO = 800
    nightShutSpeed = 6 * SECONDS2MICRO  # seconds times conversion to microseconds constant
    testWidth = 100
    testHeight = 75
    frequency = 5  # passive time between two detections
    short_duration = 15  # capture short video duration is seconds
    long_duration = 120  # capture long video duration in seconds

    def __init__(self, image_dir: str, is_day: bool = True):
        self.last_video = 0
        self.state = ''
        self.image_width = 1920
        self.image_height = 1080
        self.imageVFlip = False  # Flip image Vertically
        self.imageHFlip = False  # Flip image Horizontally
        self.image_dir = image_dir
        self.is_day = is_day

    def __get_file_name(self):
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        now = datetime.datetime.now()
        return os.path.join(self.image_dir, "{:%Y%m%d-%H%M%S}.h264".format(now))

    def __capture(self, duration: int):
        try:
            filename = self.__get_file_name()
            with picamera.PiCamera() as camera:
                time.sleep(2)
                camera.resolution = (self.image_width, self.image_height)
                # noinspection SpellCheckingInspection
                camera.vflip = self.imageVFlip
                # noinspection SpellCheckingInspection
                camera.hflip = self.imageHFlip
                if self.is_day:
                    camera.exposure_mode = 'auto'
                    camera.awb_mode = 'auto'
                else:
                    # Night time low light settings have long exposure times
                    # Settings for Low Light Conditions
                    # Set a frame rate of 1/6 fps, then set shutter
                    # speed to 6s and ISO to approx 800 per nightISO variable
                    camera.framerate = Fraction(1, 6)
                    camera.shutter_speed = self.nightShutSpeed
                    camera.exposure_mode = 'off'
                    camera.iso = self.nightISO
                    # Give the camera a good long time to measure AWB
                    # (you may wish to use fixed AWB instead)
                    time.sleep(10)
                camera.start_recording(filename)
                camera.wait_recording(duration)
                camera.stop_recording()
            return filename
        except picamera.exc.PiCameraMMALError:
            return None

    def __smart_capture(self):
        elapsed = time.clock() - self.last_video
        if self.state == 'long' and elapsed < 30 * 60:
            return None
        elif self.state == 'short' and elapsed < 5 * 60:
            filename = self.__capture(self.long_duration)
            self.last_video = time.clock()
            self.state = 'long'
            return filename
        else:
            filename = self.__capture(self.short_duration)
            self.last_video = time.clock()
            self.state = 'short'
            return filename

    def __take_motion(self):
        try:
            with picamera.PiCamera() as camera:
                time.sleep(2)
                camera.resolution = (self.testWidth, self.testHeight)
                with picamera.array.PiRGBArray(camera) as stream:
                    if self.is_day:
                        camera.exposure_mode = 'auto'
                        camera.awb_mode = 'auto'
                    else:
                        # Take Low Light image
                        # Set a framerate of 1/6 fps, then set shutter
                        # speed to 6s and ISO to 800
                        camera.framerate = Fraction(1, 6)
                        camera.shutter_speed = self.nightShutSpeed
                        camera.exposure_mode = 'off'
                        camera.iso = self.nightISO
                        # Give the camera a good long time to measure AWB
                        # (you may wish to use fixed AWB instead)
                        time.sleep(10)
                    camera.capture(stream, format='rgb')
                    return stream.array
        except picamera.exc.PiCameraMMALError:
            return None

    def __iter__(self):
        return self

    def __next__(self):
        try:
            data1 = self.__take_motion()
            while True:
                data2 = self.__take_motion()
                if (data1 is not None) and (data2 is not None):
                    diff_count = 0
                    for w in range(0, self.testWidth):
                        for h in range(0, self.testHeight):
                            # Conversion to int is required to avoid unsigned short overflow.
                            diff = abs(int(data1[h][w][1]) - int(data2[h][w][1]))
                            if diff > self.threshold:
                                diff_count += 1
                        if diff_count > self.sensitivity:
                            break
                    if diff_count > self.sensitivity:
                        video_file = self.__smart_capture()
                        if video_file:
                            print("Created video file {}.".format(video_file))
                            return video_file, diff_count
                data1 = data2
                time.sleep(self.frequency)
        except KeyboardInterrupt:
            raise StopIteration()


class MotionDaemon(DaemonBase):
    """Daemon for detecting motion."""

    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory

    def run(self):
        """Capture logic."""
        print("Detecting curious motion.")
        with Database() as db:
            try:
                motion = MotionCapture(self.directory)
                for (file, diff) in motion:
                    size = os.path.getsize(file)
                    insert = """
                    INSERT INTO events(
                        file,
                        location,
                        size,
                        diff_cnt,
                        time)
                    VALUES (
                        '{}',
                        '{}',
                        {},
                        {},
                        current_timestamp)
                    """.format(file, platform.node(), size, diff)
                    db.dml(insert)
            finally:
                print("No longer detecting motion.")


if __name__ == '__main__':
    my_daemon = MotionDaemon(settings.working_dir())
    init(my_daemon)
