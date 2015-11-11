#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" This script runs the application using a development server.
    """

import os
import sys
# noinspection PyUnresolvedReferences
import routes
import bottle

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

if ('--debug' in sys.argv[1:]) or ('SERVER_DEBUG' in os.environ):
    # Debug mode will enable more verbose output in the console window.
    # It must be set at the beginning of the script.
    bottle.debug(True)

if __name__ == '__main__':
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static').replace('\\', '/')
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555


    @bottle.route('/static/<file_path:path>')
    def server_static(file_path):
        """ Handler for static files, used with the development server.
            When running under a production server such as IIS or Apache,
            the server should be configured to serve the static files.

            :param file_path: File URL.
            """
        return bottle.static_file(file_path, root=STATIC_ROOT)


    # Starts a local test server.
    bottle.run(server='wsgiref', host=HOST, port=PORT)
