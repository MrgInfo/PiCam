# -*- coding: utf-8 -*-

"""Routes and views for the bottle application.
"""

from bottle import route, view
from urllib3 import PoolManager, Timeout, exceptions

from utils.database import Database

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

# noinspection SpellCheckingInspection
STREAMS = [
    {'name': "Szuterén", 'url': 'http://wavepi.gotdns.org:8080'},
    {'name': "Teázó", 'url': 'http://nikipi.gotdns.org:8080'}]


def _check_url(url: str) -> bool:
    timeout = Timeout(connect=1.0, read=1.0)
    with PoolManager(timeout=timeout) as http:
        response = None
        try:
            response = http.request('GET', url)
            return response.status == 200
        except exceptions.MaxRetryError:
            return False
        finally:
            if response is not None:
                response.release_conn()


def _streams():
    return [stream for stream in STREAMS if _check_url(stream['url'])]


@route('/')
@route('/home')
@view('index')
def home():
    """Events."""
    with Database() as database:
        events = [
            {'time': time, 'camera': location, 'size': size, 'url': url}
            for (file, location, time, size, url)
            in database.query("""
                SELECT file,
                       location,
                       time,
                       size,
                       url
                  FROM events
            """)
        ]
        return {'events': events}


@route('/view')
@view('view')
def view():
    """Video stream."""
    return {'streams': _streams()}
