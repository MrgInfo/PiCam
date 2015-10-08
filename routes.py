# -*- coding: utf-8 -*-
"""
Routes and views for the bottle application.
"""

from bottle import route, view

from utils.database import Database

__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


@route('/')
@route('/home')
@view('index')
def home():
    with Database() as database:
        events = [
            {'time': time, 'camera': 'Szuterén', 'size': size, 'url': url}
            for (file, time, size, url)
            in database.query("SELECT file, time, size, url FROM events")
        ]
        return {'events': events}


@route('/view')
@view('view')
def view():
    return {
        'streams': [
            {'name': "Szuterén", 'url': 'http://wavepi.gotdns.org:8080/cam.mjpg'},
            {'name': "Teázó", 'url': 'http://nikipi.gotdns.org:8080/cam.mjpg'}
        ]
    }
