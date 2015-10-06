#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Simple mjpg stream http server for the Raspberry Pi Camera
"""

import datetime
import io
import re
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import picamera

from bad_daemon import DaemonBase, init

__all__ = []
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


class CamHandler(BaseHTTPRequestHandler):
    """
    Camera HTTP stream.
    """

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

    def do_GET(self):
        try:
            if self.path is None:
                return
            path = re.sub('[^.a-zA-Z0-9]', "", str(self.path))
            if path == "" or path[:1] == ".":
                return
            if path.endswith('.jpg') or path.endswith('.jpeg'):
                self._jpeg()
                return
            # noinspection SpellCheckingInspection
            if path.endswith('.mjpg') or path.endswith('.mjpeg'):
                self._mjpg()
                return
            self._html()
        except IOError:
            self.send_error(404, "File Not Found: {}".format(self.path))


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """
    Handle requests in a separate thread.
    """


class CameraDaemon(DaemonBase):
    """
    Camera daemon.
    """

    def run(self):
        """
        HTTP streaming logic.
        """
        server = ThreadedHTTPServer(('', 8080), CamHandler)
        with server.socket as socket:
            self.logger.info("Serving on {}".format(socket.getsockname()))
            try:
                server.serve_forever()
            finally:
                self.logger.info("No longer serving.")


if __name__ == '__main__':
    my_daemon = CameraDaemon()
    init(my_daemon)
