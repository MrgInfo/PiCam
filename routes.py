# -*- coding: utf-8 -*-
"""
Routes and views for the bottle application.
"""

from bottle import route, view
import datetime

__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


@route('/')
@route('/home')
@view('index')
def home():
    return {
        'events': [
            {'time': datetime.datetime(2015, 2, 15, 15, 20, 0), 'camera': 'Szuterén', 'size': 54321,
             'url': 'http://index.hu'},
            {'time': datetime.datetime(2015, 10, 9, 3, 59, 23), 'camera': 'Teázó', 'size': 12345,
             'url': 'http://origo.hu'},
        ]
    }


@route('/view')
@view('view')
def view():
    return {
        'streams': [
            {'name': "Szuterén", 'url': 'http://wavepi.gotdns.org:8080/cam.mjpg'},
            {'name': "Teázó", 'url': 'http://nikipi.gotdns.org:8080/cam.mjpg'}
        ]
    }
