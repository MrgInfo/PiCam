#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Simple mjpg stream http server for the Raspberry Pi Camera
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from os import makedirs
from os.path import exists, join
from daemon import runner
import io
import time
import picamera
import logging
import logging.handlers

__all__ = ['CamHandler']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"

LOG_DIR = '/var/log/python'


class CamHandler(BaseHTTPRequestHandler):
    """
    Camera HTTP stream.
    """

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--boundary')
            self.end_headers()
            stream = io.BytesIO()
            with picamera.PiCamera() as camera:
                camera.resolution = (2592, 1944)
                # camera.framerate = 24
                camera.brightness = 70
                time.sleep(2)  # Camera warm-up time
                for _ in camera.capture_continuous(stream, 'jpeg'):
                    self.wfile.write(b'--boundary')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(stream.getvalue()))
                    self.end_headers()
                    self.wfile.write(stream.getvalue())
                    stream.seek(0)
                    stream.truncate()
                    time.sleep(.2)
                    if self.request or self.wfile.closed:
                        return
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # noinspection SpellCheckingInspection
            html = '''
<!DOCTYPE html>
<html lang="en-US">
    <meta charset="UTF-8">
    <title>PiCam</title>
    <style type="text/css">
html {width:100%; height:100%; background:#E9967A}
img {position:absolute; top:50%; left:50%; width:1024px; height:768px; margin-top:-384px; margin-left:-512px}
    </style>
    <body>
        <img src="/cam.mjpg" />
    </body>
</html>
'''
            self.wfile.write(html.encode('utf-8'))


class CameraDaemon:
    """
    Camera daemon.
    """

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        # noinspection SpellCheckingInspection
        self.pidfile_path = '/var/run/{}.pid'.format(self.__class__.__name__)
        # noinspection SpellCheckingInspection
        self.pidfile_timeout = 5
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

    def run(self):
        server = HTTPServer(('', 8080), CamHandler)
        with server.socket as socket:
            self.logger.info("Serving on {}".format(socket.getsockname()))
            try:
                server.serve_forever()
            finally:
                self.logger.info("No longer serving.")


def _interactive(camera_daemon: CameraDaemon):
    print("Starting server, use <Ctrl-C> to stop.")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    camera_daemon.logger.addHandler(stream_handler)
    try:
        camera_daemon.run()
    except KeyboardInterrupt:
        pass


def _background(camera_daemon: CameraDaemon):
    if not exists(LOG_DIR):
        makedirs(LOG_DIR)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        join(LOG_DIR, '{}.log'.format(camera_daemon.logger.name)),
        when='midnight',
        backupCount=10)
    file_handler.setLevel(logging.INFO)
    # noinspection SpellCheckingInspection
    file_handler.setFormatter(
        logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))
    camera_daemon.logger.addHandler(file_handler)
    daemon_runner = runner.DaemonRunner(camera_daemon)
    daemon_runner.do_action()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--interactive", action="store_true", help="run in interactive console mode")
    (options, args) = parser.parse_args()
    daemon = CameraDaemon()
    if options.interactive:
        _interactive(daemon)
    else:
        _background(daemon)
