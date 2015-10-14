#!/usr/bin/env python3
# -*- coding: utf-8 -*-
### BEGIN INIT INFO
# Provides:          upload
# Required-Start:    $network $remote_fs
# Required-Stop:     $network $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Dropbox upload daemon
### END INIT INFO

"""Dropbox upload daemon.
"""

from operator import itemgetter
from os import listdir
from time import strptime, sleep
import urllib3
import os.path

import dropbox

from utils import settings
from utils.daemons import DaemonBase, init
from utils.database import Database

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"


class UploadDaemon(DaemonBase):
    """Dropbox upload daemon."""

    max_size = 1024 ** 3 // 2
    access_token = settings.config.access_token

    def __init__(self, directory: str):
        super().__init__()
        self.directory = directory
        if self.access_token is None:
            # noinspection SpellCheckingInspection
            flow = dropbox.client.DropboxOAuth2FlowNoRedirect('m9cijknmu1po39d', 'bi8dlhif9215qg3')
            authorize_url = flow.start()
            print('1. Go to: {}'.format(authorize_url))
            print('2. Click "Allow" (you might have to log in first).')
            print('3. Copy the authorization code.')
            code = input("Enter the authorization code here: ").strip()
            self.access_token, user_id = flow.finish(code)
            settings.config.access_token = self.access_token
            settings.config.save()

    def run(self):
        """Upload logic."""
        print("Uploading from {} to Dropbox.".format(self.directory))
        try:
            # noinspection PyDeprecation
            client = dropbox.client.DropboxClient(self.access_token)
            while True:
                # Get files from Dropbox:
                try:
                    metadata = client.metadata('/')
                except urllib3.exceptions.MaxRetryError:
                    sleep(10)
                    continue
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
                        print("%s was uploaded to Dropbox." % filename)
                        with Database() as db:
                            update = """
                            UPDATE events
                               SET url = '{}',
                                   uploaded = current_timestamp
                             WHERE file = '{}'
                            """.format(share['url'], filename)
                            db.dml(update)
                # Rotate Dropbox in order to save storage:
                total_size = sum(item['size'] for item in files)
                files_history = sorted(files, key=itemgetter('modified'))
                for file in files_history:
                    if total_size < self.max_size:
                        break
                    client.file_delete(file['file'])
                    print("%s was deleted from Dropbox." % file['file'])
                    total_size -= file['size']
        finally:
            print("No longer uploading from %s to Dropbox." % self.directory)


if __name__ == '__main__':
    my_daemon = UploadDaemon(settings.config.working_dir)
    init(my_daemon)
