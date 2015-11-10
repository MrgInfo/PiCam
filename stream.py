#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### BEGIN INIT INFO
# Provides:          stream
# Required-Start:    $local_fs $remote_fs $network $syslog $named
# Required-Stop:     $local_fs $remote_fs $network $syslog $named
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: HTTP video stream
### END INIT INFO

"""A Simple mjpg stream http server for the Raspberry Pi Camera
"""

import datetime
import io
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from picamera.exc import PiCameraError
from websocket_server import ThreadingMixIn
import picamera

from utils.daemons import DaemonBase, init

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"


class CamHandler(BaseHTTPRequestHandler):
    """Camera HTTP stream."""

    def _jpeg(self):
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            camera.resolution = (2592, 1944)
            camera.brightness = 70
            camera.capture(stream, 'jpeg')
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Content-length', len(stream.getvalue()))
        self.end_headers()
        self.wfile.write(stream.getvalue())

    def _mjpg(self):
        self.send_response(200)
        self.send_header('Pragma:', 'no-cache')
        self.send_header('Cache-Control:', 'no-cache')
        self.send_header('Content-Encoding:', 'identify')
        # noinspection SpellCheckingInspection
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        self.end_headers()
        data = io.BytesIO()
        with picamera.PiCamera() as camera:
            camera.resolution = (1280, 720)
            camera.framerate = 30
            now = datetime.datetime.now()
            camera.annotate_text = "{:%Y-%m-%d %H:%M:%S}".format(now)
            time.sleep(2)  # Camera warm-up time
            try:
                for _ in camera.capture_continuous(data, 'jpeg'):
                    stream = data.getvalue()
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(stream))
                    self.end_headers()
                    self.wfile.write(stream)
                    # noinspection SpellCheckingInspection
                    self.wfile.write(b'--jpgboundary')
                    self.send_response(200)
                    if self.wfile.closed:
                        return
                    data.seek(0)
                    data.truncate()
                    now = datetime.datetime.now()
                    camera.annotate_text = "{:%Y-%m-%d %H:%M:%S}".format(now)
                    time.sleep(.2)
            except IOError as e:
                # noinspection SpellCheckingInspection
                if hasattr(e, 'errno') and e.errno == 32:
                    self.rfile.close()
                    return
                else:
                    raise e

    def _html(self):
        # noinspection SpellCheckingInspection
        html = '''<!DOCTYPE html>
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
</html>'''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def _error(self):
        self.send_error(404, "File Not Found: {}".format(self.path))

    def do_GET(self):
        try:
            if self.path is not None:
                path = re.sub('[^.a-zA-Z0-9]', "", str(self.path))
            else:
                path = ''
            # noinspection SpellCheckingInspection
            if path.endswith('.jpg')\
                    or path.endswith('.jpeg'):
                self._jpeg()
            elif path.endswith('.mjpg')\
                    or path.endswith('.mjpeg'):
                self._mjpg()
            elif path.endswith('.htm')\
                    or path.endswith('.html'):
                self._html()
            else:
                self._ok()
        except (IOError, PiCameraError):
            self._error()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    daemon_threads = True


class CameraDaemon(DaemonBase):
    """Camera daemon."""

    def run(self):
        """HTTP streaming logic."""
        server = ThreadedHTTPServer(('', 8080), CamHandler)
        with server.socket as socket:
            try:
                print("Serving on {}".format(socket.getsockname()))
                server.serve_forever()
            except KeyboardInterrupt:
                print("No longer serving.")
                server.shutdown()


if __name__ == '__main__':
    my_daemon = CameraDaemon()
    init(my_daemon)
