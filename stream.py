#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A Simple mjpg stream http server for the Raspberry Pi Camera
"""

import io
import time
import picamera
from http.server import BaseHTTPRequestHandler, HTTPServer

__all__ = ['CamHandler']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


class CamHandler(BaseHTTPRequestHandler):
    """
    Camera stream.
    """

    def __init__(self, request, client_address, srv):
        super().__init__(request, client_address, srv)
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1280, 720)
        self.camera.framerate = 24
        self.camera.brightness = 70

    def __del__(self):
        self.camera.close()
        self.server.socket.close()

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(200, 'OK')
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            stream = io.BytesIO()
            try:
                for _ in self.camera.capture_continuous(stream, 'jpeg'):
                    self.wfile.write(b'--jpgboundary')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(stream.getvalue()))
                    self.end_headers()
                    self.wfile.write(stream.getvalue())
                    stream.seek(0)
                    stream.truncate()
                    time.sleep(.5)
                    if self.request or self.wfile.closed:
                        return
            except (KeyboardInterrupt, SystemExit):
                pass
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>PiCam</title>
        <style>
            html {overflow: hidden; height: 100%}
            body {overflow: auto; width: 100%; margin: 0 auto; padding: 0 20px}
        </style>
    </head>
    <body>
        <img src="/cam.mjpg"/>
    </body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))


if __name__ == '__main__':
    with HTTPServer(('', 8080), CamHandler) as server:
        print("Serving on %s" % server.sockets[0].getsockname())
        print("Press Ctrl-C to exit...")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
