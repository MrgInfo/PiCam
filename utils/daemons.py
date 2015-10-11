#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In one of my project I need to program in Python 3 daemon. Maybe my code will be useful to someone.
Executive part of the method is 'run' by just overloaded ..
"""

import traceback
import time

from optparse import OptionParser

import sys
from daemon import runner

__all__ = ['DaemonBase', 'init']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


class DaemonBase:
    """
    Base class for creating well behaving daemons.
    """

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/PiCam/{}.log'.format(self.__class__.__name__)
        self.stderr_path = '/var/log/PiCam/{}.err'.format(self.__class__.__name__)
        # noinspection SpellCheckingInspection
        self.pidfile_path = '/var/run/{}.pid'.format(self.__class__.__name__)
        # noinspection SpellCheckingInspection
        self.pidfile_timeout = 5

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
    try:
        a_daemon.run()
    except KeyboardInterrupt:
        pass


def _background(a_daemon: DaemonBase):
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
        print(traceback.format_exc(), file=sys.stderr)


class TwinkleDaemon(DaemonBase):
    """
    Example.
    """

    def run(self):
        while True:
            time.sleep(1)
            print('Twinkle')


if __name__ == '__main__':
    daemon = TwinkleDaemon()
    init(daemon)