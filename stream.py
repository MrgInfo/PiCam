#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Simple mjpg stream http server for the Raspberry Pi Camera
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from os import makedirs
from os.path import exists, join
import io
import time
import picamera
import daemon
import daemon.pidfile
import signal
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
    Camera stream.
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
        img {display:block; width:1204px; height:768px; vertical-align:middle}
        .frame {background-color:#E9967A; text-align:center; width:100%; height:100%}
        .frame img {margin:auto}
    </style>
    <body>
        <div class="frame">
            <img src="/cam.mjpg" />
        </div>
    </body>
</html>
'''
            self.wfile.write(html.encode('utf-8'))


logger = logging.getLogger(CamHandler.__class__.__name__)
logger.setLevel(logging.DEBUG)


# noinspection PyUnusedLocal
def _sig_handler(signum, frame):
    pass


def _run():
    server = HTTPServer(('', 8080), CamHandler)
    with server.socket as socket:
        logger.info("Serving on {}".format(socket.getsockname()))
        try:
            server.serve_forever()
        finally:
            logger.info("No longer serving.")


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--interactive", dest="interactive", help="Run in interactive console mode.")
    (options, args) = parser.parse_args()
    if options.interactive:
        print("Starting server, use <Ctrl-C> to stop.")
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
        try:
            _run()
        except KeyboardInterrupt:
            pass
    else:
        if not exists(LOG_DIR):
            makedirs(LOG_DIR)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            join(LOG_DIR, '{}.log'.format(logger.name)),
            when='midnight',
            backupCount=10)
        file_handler.setLevel(logging.INFO)
        # noinspection SpellCheckingInspection
        file_handler.setFormatter(
            logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(file_handler)
        context = daemon.DaemonContext(
            pidfile=daemon.pidfile.TimeoutPIDLockFile('/var/run/cam.pid', -1),
            signal_map={signal.SIGTERM: _sig_handler}
        )
        with context:
            _run()
