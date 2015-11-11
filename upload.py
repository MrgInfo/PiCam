#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### BEGIN INIT INFO
# Provides:          upload
# Required-Start:    $local_fs $remote_fs $network $syslog $named
# Required-Stop:     $local_fs $remote_fs $network $syslog $named
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Dropbox upload daemon
### END INIT INFO

""" Dropbox upload daemon.
    """

from operator import itemgetter
from os import listdir, path
from time import strptime, sleep
from urllib3.exceptions import MaxRetryError

from dropbox.client import DropboxClient, DropboxOAuth2FlowNoRedirect
import urllib3

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
    """ Dropbox upload daemon.
        """

    max_size = 1024 ** 3 // 2
    access_token = settings.config.access_token

    def __init__(self, directory: str):
        """ Constructor.
            """
        super().__init__()
        self.directory = directory
        if self.access_token is None or self.access_token == '':
            # noinspection SpellCheckingInspection
            flow = DropboxOAuth2FlowNoRedirect('m9cijknmu1po39d', 'bi8dlhif9215qg3')
            authorize_url = flow.start()
            print("OAuth 2 authorization process")
            print("1. Go to: {}".format(authorize_url))
            print("2. Click Allow (you might have to log in first).")
            print("3. Copy the authorization code.")
            code = input("4. Enter the authorization code here: ").strip()
            self.access_token, user_id = flow.finish(code)
            settings.config.access_token = self.access_token

    @staticmethod
    def _get(client: DropboxClient) -> list:
        """ Get files from Dropbox.
            """
        try:
            metadata = client.metadata('/')
        except MaxRetryError:
            return None
        return [
            {
                'file': m['path'],
                'modified': strptime(m['modified'], '%a, %d %b %Y %H:%M:%S %z'),
                'size': m['bytes']
            }
            for m in metadata['contents']
            if not m['is_dir']
        ]

    def _upload(self, client: DropboxClient, files: list):
        """ Upload new files from directory.
            """
        for filename in listdir(self.directory):
            local_name = '/' + filename
            found = False
            for f in files:
                if f['file'] == local_name:
                    found = True
                    break
            if not found:
                with open(path.join(self.directory, filename), 'rb') as file_stream:
                    try:
                        client.put_file(local_name, file_stream)
                        share = client.share(local_name)
                    except MaxRetryError:
                        continue
                print("%s was uploaded to Dropbox." % filename)
                with Database() as db:
                    update = """
                    UPDATE events
                       SET url = '{}',
                           uploaded = current_timestamp
                     WHERE file = '{}'
                    """.format(share['url'], filename)
                    db.dml(update)

    def _rotate(self, client: DropboxClient, files: list):
        """  Rotate Dropbox in order to save storage.
            """
        total_size = sum(item['size'] for item in files)
        files_history = sorted(files, key=itemgetter('modified'))
        for file in files_history:
            if total_size < self.max_size:
                break
            try:
                client.file_delete(file['file'])
                print("{} was deleted from Dropbox.".format(file['file']))
                total_size -= file['size']
            except urllib3.exceptions.MaxRetryError:
                pass

    def run(self):
        """ Upload logic.
            """
        print("Uploading from {} to Dropbox.".format(self.directory))
        try:
            # noinspection PyDeprecation
            client = DropboxClient(self.access_token)
            while True:
                files = self._get(client)
                if files is None or files is []:
                    sleep(5 * 60)
                else:
                    self._upload(client, files)
                    self._rotate(client, files)
        finally:
            print("No longer uploading from {} to Dropbox.".format(self.directory))


if __name__ == '__main__':
    my_daemon = UploadDaemon(settings.config.working_dir)
    init(my_daemon)
