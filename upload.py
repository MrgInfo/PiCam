#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dropbox upload daemon.
"""

from time import strptime
from operator import itemgetter
from os import listdir
import os.path
import logging

from dropbox.client import DropboxClient

from bad_daemon import Daemon, console
from database import Database
import settings

__all__ = ['UploadDaemon']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"

OAUTH2_ACCESS_TOKEN = '3PJXWNTgRu8AAAAAAAASjHyifGwz-SPExoBgYAT2b7sO16Eo0RmqjvDIA5uValcG'


class UploadDaemon(Daemon):
    """
    Dropbox upload daemon.
    """

    max_size = 1024 ** 3 // 2

    def __init__(self, directory: str):
        super().__init__('/var/run/upload.pid')
        self.directory = directory

    def run(self):
        self.logger.info("Uploading from %s to Dropbox." % self.directory)
        try:
            # noinspection PyDeprecation
            client = DropboxClient(OAUTH2_ACCESS_TOKEN)
            while True:
                # Get files from Dropbox:
                metadata = client.metadata('/')
                files = [{'file': m['path'], 'modified': strptime(m['modified'], '%a, %d %b %Y %H:%M:%S %z'),
                          'size': m['bytes']} for m in metadata['contents'] if not m['is_dir']]
                # Upload new files from directory:
                for filename in listdir(self.directory):
                    local_name = '/' + filename
                    found = False
                    for f in files:
                        if f['file'] == local_name:
                            found = True
                            break
                    if not found:
                        with open(os.path.join(self.directory, filename), 'rb') as file_stream:
                            client.put_file(local_name, file_stream)
                            share = client.share(local_name)
                        self.logger.debug("%s was uploaded to Dropbox." % filename)
                        with Database() as db:
                            db.dml("UPDATE events SET url = '%s' WHERE file = '%s'" % (share['url'], filename))
                # Rotate Dropbox in order to save storage:
                total_size = sum(item['size'] for item in files)
                files_history = sorted(files, key=itemgetter('modified'))
                for file in files_history:
                    if total_size < self.max_size:
                        break
                    client.file_delete(file['file'])
                    self.logger.debug("%s was deleted from Dropbox." % file['file'])
                    total_size -= file['size']
        finally:
            self.logger.info("No longer uploading from %s to Dropbox." % self.directory)


if __name__ == '__main__':
    daemon = UploadDaemon(settings.working_dir())
    if os.path.dirname(os.path.realpath(__file__)).startswith('/usr/local'):
        console(daemon)
    else:
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        daemon.logger.addHandler(stream)
        daemon.run()
