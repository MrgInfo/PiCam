# -*- coding: utf-8 -*-
"""
Routes and views for the bottle application.
"""

from bottle import route, view

__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


@route('/')
@route('/home')
@view('index')
def home():
    return dict()


@route('/view')
@view('view')
def view():
    return dict()
