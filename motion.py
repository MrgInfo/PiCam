#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daemon for detecting motion.
"""

import os
import logging

from capture import MotionCapture
from daemon import Daemon, console
from database import Database
import settings

__all__ = ['MotionDaemon']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


class MotionDaemon(Daemon):
    """
    Daemon for detecting motion.
    """

    def __init__(self, directory: str):
        super().__init__('/var/run/motion.pid')
        self.directory = directory

    def run(self):
        self.logger.info("Detecting curious motion.")
        with Database() as db:
            try:
                motion = MotionCapture(self.directory, logger=self.logger)
                for (file, diff) in motion:
                    size = os.path.getsize(file)
                    db.dml("INSERT INTO events(file, size, diff_cnt) VALUES ('{}', {}, {})".format(file, size, diff))
            finally:
                self.logger.info("No longer detecting motion.")


if __name__ == '__main__':
    daemon = MotionDaemon(settings.working_dir())
    if os.path.dirname(os.path.realpath(__file__)).startswith('/usr/local'):
        console(daemon)
    else:
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        daemon.logger.addHandler(stream)
        daemon.run()
