# -*- coding: utf-8 -*-

"""WSGI config for PiCam project.

The aim of mod_wsgi is to implement a simple to use Apache module which can host any Python application which supports
the Python WSGI interface. The module would be suitable for use in hosting high performance production web sites, as
well as your average self managed personal sites running on web hosting services.

apache2.conf:
    WSGIPythonPath /usr/local/PiCam

    <VirtualHost *:80>
        WSGIScriptAlias /        /usr/local/PiCam/wsgi.py
        Alias           /static/ /usr/local/PiCam/static/
    </VirtualHost>
"""

import bottle
# noinspection PyUnresolvedReferences
import routes

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

application = bottle.default_app()
