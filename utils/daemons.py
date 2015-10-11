#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In one of my project I need to program in Python 3 daemon. Maybe my code will be useful to someone.
Executive part of the method is 'run' by just overloaded ..
"""

import logging
import traceback
from cloghandler import ConcurrentRotatingFileHandler
import time

from optparse import OptionParser
from os import makedirs
from os.path import exists, join
from daemon import runner

__all__ = ['DaemonBase', 'init']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"

LOG_DIR = '/var/log/PiCam/'


class DaemonBase:
    """
    Base class for creating well behaving daemons.
    """

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/daemon.inf'
        self.stderr_path = '/var/log/daemon.err'
        # noinspection SpellCheckingInspection
        self.pidfile_path = '/var/run/{}.pid'.format(self.__class__.__name__)
        # noinspection SpellCheckingInspection
        self.pidfile_timeout = 5
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

    # noinspection PyMethodMayBeStatic
    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by start() or restart().

        Example:

        class MyDaemon(DaemonBase):
            def run(self):
                while True:
                    time.sleep(1)
        """


def _interactive(a_daemon: DaemonBase):
    print("Starting server, use <Ctrl-C> to stop.")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    a_daemon.logger.addHandler(stream_handler)
    try:
        a_daemon.run()
    except KeyboardInterrupt:
        pass


def _background(a_daemon: DaemonBase):
    if not exists(LOG_DIR):
        makedirs(LOG_DIR)
    name = join(LOG_DIR, '{}.log'.format(a_daemon.logger.name))
    file_handler = ConcurrentRotatingFileHandler(name, "a", 512 * 1024, 5)
    file_handler.setLevel(logging.INFO)
    # noinspection SpellCheckingInspection
    file_handler.setFormatter(
        logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))
    a_daemon.logger.addHandler(file_handler)
    daemon_runner = runner.DaemonRunner(a_daemon)
    daemon_runner.do_action()


def init(a_daemon: DaemonBase):
    """
    Initialize the Python program for running the particular daemon.
    """
    # noinspection PyBroadException
    try:
        parser = OptionParser()
        parser.add_option("-i", "--interactive", action="store_true", help="run in interactive console mode")
        (options, args) = parser.parse_args()
        if options.interactive:
            _interactive(a_daemon)
        else:
            _background(a_daemon)
    except Exception:
        print(traceback.format_exc())


class TwinkleDaemon(DaemonBase):
    """
    Example.
    """

    def run(self):
        while True:
            time.sleep(1)
            self.logger.info('Twinkle')


if __name__ == '__main__':
    daemon = TwinkleDaemon()
    init(daemon)
