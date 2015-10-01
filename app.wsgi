# -*- coding: utf-8 -*-
"""
The aim of mod_wsgi is to implement a simple to use Apache module which can host any Python application which supports
the Python WSGI interface. The module would be suitable for use in hosting high performance production web sites, as
well as your average self managed personal sites running on web hosting services.
"""

import os
import sys

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(__file__))
sys.path = [os.path.dirname(__file__)] + sys.path

import bottle
# noinspection PyUnresolvedReferences
import routes

application = bottle.default_app()
