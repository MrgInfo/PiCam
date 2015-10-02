#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight Motion Detection using python picamera libraries
based on code from raspberry pi forum by user utpalc
modified by Claude Pageau for this working example
original code on github https://github.com/pageauc/picamera-motion
"""

from fractions import Fraction
import os
import datetime
import time
import logging
import picamera
import picamera.array
import settings

__all__ = ['MotionCapture']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"

SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds


class MotionCapture:
    """
    Detect motion on PiCam and capture short video.
    """

    threshold = 10  # How Much pixel changes
    sensitivity = 100  # How many pixels change
    nightISO = 800
    nightShutSpeed = 6 * SECONDS2MICRO  # seconds times conversion to microseconds constant
    testWidth = 100
    testHeight = 75
    frequency = 5 # passive time between two detections
    short_duration = 15 # capture short video duration is seconds
    long_duration = 120 # capture long video duration in seconds

    def __init__(self, image_dir: str, is_day: bool = True, logger: logging.Logger = None):
        self.last_video = 0
        self.state = ''
        self.image_width = 1920
        self.image_height = 1080
        self.imageVFlip = False  # Flip image Vertically
        self.imageHFlip = False  # Flip image Horizontally
        self.image_dir = image_dir
        self.is_day = is_day
        if logger is None:
            self.logger = settings.create_logger(self)
        else:
            self.logger = logger

    def __get_file_name(self):
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        now = datetime.datetime.now()
        return os.path.join(self.image_dir, "{:%Y%m%d-%H%M%S}.h264".format(now))

    def __capture(self, duration: int):
        filename = self.__get_file_name()
        with picamera.PiCamera() as camera:
            time.sleep(2)
            camera.resolution = (self.image_width, self.image_height)
            camera.vflip = self.imageVFlip
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

    def __iter__(self):
        return self

    def __next__(self):
        try:
            data1 = self.__take_motion()
            while True:
                data2 = self.__take_motion()
                diff_count = 0
                for w in range(0, self.testWidth):
                    for h in range(0, self.testHeight):
                        # Conversion to int is required to avoid unsigned short overflow.
                        diff = abs(int(data1[h][w][1]) - int(data2[h][w][1]))
                        if diff > self.threshold:
                            diff_count += 1
                    if diff_count > self.sensitivity:
                        break
                self.logger.debug("diff_count = {}".format(diff_count))
                if diff_count > self.sensitivity:
                    video_file = self.__smart_capture()
                    if video_file:
                        self.logger.info("Created video file {}.".format(video_file))
                        return video_file, diff_count
                data1 = data2
                time.sleep(self.frequency)
        except KeyboardInterrupt:
            raise StopIteration()


if __name__ == '__main__':
    motion = MotionCapture(settings.working_dir())
    for file in motion:
        print("Captured video {}.".format(file))
