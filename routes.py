# -*- coding: utf-8 -*-

"""Routes and views for the bottle application.
"""

from bottle import route, view

from utils.database import Database

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"


# noinspection SpellCheckingInspection
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


# noinspection SpellCheckingInspection
@route('/view')
@view('view')
def view():
    return {
        'streams': [
            {'name': "Szuterén", 'url': 'http://wavepi.gotdns.org:8080/cam.mjpg'},
            {'name': "Teázó", 'url': 'http://nikipi.gotdns.org:8080/cam.mjpg'}
        ]
    }
