#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### BEGIN INIT INFO
# Provides:          upload
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Dropbox upload daemon
### END INIT INFO
"""
Dropbox upload daemon.
"""

import os.path
from operator import itemgetter
from os import listdir
from time import strptime

import dropbox

import settings
from bad_daemon import DaemonBase, init
from database import Database

__all__ = []
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


class UploadDaemon(DaemonBase):
    """
    Dropbox upload daemon.
    """

    max_size = 1024 ** 3 // 2

    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory
        self.secret_file = os.path.join(self.directory, 'secret.txt')
        if os.path.exists(self.secret_file):
            with open(self.secret_file, 'r+') as file:
                self.access_token = file.read()
        else:
            # noinspection SpellCheckingInspection
            flow = dropbox.client.DropboxOAuth2FlowNoRedirect('m9cijknmu1po39d', 'bi8dlhif9215qg3')
            authorize_url = flow.start()
            print('1. Go to: {}'.format(authorize_url))
            print('2. Click "Allow" (you might have to log in first).')
            print('3. Copy the authorization code.')
            code = input("Enter the authorization code here: ").strip()
            self.access_token, user_id = flow.finish(code)
            with open(self.secret_file, 'w+') as file:
                file.write(self.access_token)

    def run(self):
        """
        Upload logic.
        """
        self.logger.info("Uploading from {} to Dropbox.".format(self.directory))
        try:
            # noinspection PyDeprecation
            client = dropbox.client.DropboxClient(self.access_token)
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
                            db.dml("UPDATE events SET url = '{}' WHERE file = '{}'".format(share['url'], filename))
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
    my_daemon = UploadDaemon(settings.working_dir())
    init(my_daemon)
