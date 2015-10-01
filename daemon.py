#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In one of my project I need to program in Python 3 daemon. Maybe my code will be useful to someone.
Executive part of the method is 'run' by just overloaded ..
"""

import sys
import os
import time
import atexit
from signal import SIGTERM

import settings

__all__ = ['Daemon', 'console']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"

LOG_DIR = '/var/log/python'


class Daemon(object):
    """
    Subclass Daemon class and override the run() method.
    """

    def __init__(self, pid_file: str, stdin: str = '/dev/null', stdout: str = '/dev/null', stderr: str = '/dev/null'):
        self.pid_file = pid_file
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.logger = settings.create_logger(self)

    def __daemonize(self):
        # Daemonize, do double-fork magic.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent.
                sys.exit(0)
        except OSError as e:
            message = "Fork #1 failed: {}\n".format(e)
            sys.stderr.write(message)
            sys.exit(1)

        # Decouple from parent environment.
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent.
                sys.exit(0)
        except OSError as e:
            message = "Fork #2 failed: {}\n".format(e)
            sys.stderr.write(message)
            sys.exit(1)

        self.logger.info('Daemon going to background, PID: {}'.format(os.getpid()))

        # Redirect standard file descriptors.
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Write pid file.
        pid = str(os.getpid())
        open(self.pid_file, 'w+').write("{}\n".format(pid))

        # Register a function to clean up.
        atexit.register(self.__delete_pid)

    def __delete_pid(self):
        os.remove(self.pid_file)

    def start(self):
        """
        Start daemon.
        """
        # Check pid file to see if the daemon already runs.
        try:
            pf = open(self.pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "Pid file {} already exist. Daemon already running?\n".format(self.pid_file)
            sys.stderr.write(message)
            sys.exit(1)

        # Start daemon.
        self.__daemonize()
        # noinspection PyBroadException
        try:
            self.run()
        except Exception:
            self.logger.error("Fatal error in daemon logic!", exc_info=True)

    def status(self):
        """
        Get status of daemon.
        """
        try:
            pf = open(self.pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            message = "There is not PID file. Daemon already running?\n"
            sys.stderr.write(message)
            sys.exit(1)

        try:
            proc_file = open("/proc/{}/status".format(pid), 'r')
            proc_file.close()
            message = "There is a process with the PID {}\n".format(pid)
            sys.stdout.write(message)
        except IOError:
            message = "There is not a process with the PID {}\n".format(self.pid_file)
            sys.stdout.write(message)

    def stop(self):
        """
        Stop the daemon.
        """
        # Get the pid from pid file.
        try:
            pf = open(self.pid_file, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            message = str(e) + "\nDaemon not running?\n"
            sys.stderr.write(message)
            sys.exit(1)

        # Try killing daemon process.
        try:
            os.kill(pid, SIGTERM)
            time.sleep(1)
        except OSError as e:
            print(str(e))
            sys.exit(1)

        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
        except IOError as e:
            message = str(e) + "\nCan not remove pid file {}".format(self.pid_file)
            sys.stderr.write(message)
            sys.exit(1)

    def restart(self):
        """
        Restart daemon.
        """
        self.stop()
        time.sleep(1)
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by start() or restart().

        Example:

        class MyDaemon(Daemon):
            def run(self):
                while True:
                    time.sleep(1)
        """


def console(daemon: Daemon):
    """
    Start a daemon from console.
    """
    if daemon is None:
        return
    if len(sys.argv) == 2:
        daemon.logger.info('{} {}'.format(sys.argv[0], sys.argv[1]))
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print("Unknown command!")
            sys.exit(2)
        sys.exit(0)
    else:
        daemon.logger.warning('show cmd daemon usage')
        print("Usage: {} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)


class MyDaemon(Daemon):
    """
    Example.
    """

    def run(self):
        while True:
            time.sleep(1)


if __name__ == '__main__':
    daemon = MyDaemon('/var/run/daemon.pid')
    console(daemon)
