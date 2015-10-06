#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Simple mjpg stream http server for the Raspberry Pi Camera
"""

import io
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

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
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--boundary')
        self.end_headers()
        stream = io.BytesIO()
        with picamera.PiCamera() as camera:
            camera.resolution = (1280, 720)
            camera.framerate = 30
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
                if not self.request \
                        or self.wfile.closed:
                    return

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
        if self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
            self._jpeg()
        elif self.path.endswith('.mjpg'):
            self._mjpg()
        else:
            self._html()


class CameraDaemon(DaemonBase):
    """
    Camera daemon.
    """

    def run(self):
        """
        HTTP streaming logic.
        """
        server = HTTPServer(('', 8080), CamHandler)
        with server.socket as socket:
            self.logger.info("Serving on {}".format(socket.getsockname()))
            try:
                server.serve_forever()
            finally:
                self.logger.info("No longer serving.")


if __name__ == '__main__':
    my_daemon = CameraDaemon()
    init(my_daemon)
