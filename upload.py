#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Dropbox upload daemon.
    """

from fnmatch import fnmatch
from operator import itemgetter
from os import listdir, path, mknod, stat
from time import strptime, sleep, time
from dropbox.client import DropboxClient, DropboxOAuth2FlowNoRedirect
from dropbox.rest import ErrorResponse
from urllib3.exceptions import MaxRetryError
from utils import settings
from utils.daemons import DaemonBase, init
from utils.database import DatabaseConnection

__author__ = "wavezone"
__copyright__ = "Copyright 2016, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"


class UploadDaemon(DaemonBase):
    """ Dropbox upload daemon.
        """

    first_time = False
    max_size = 2 * (1024 ** 3)
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
            self.first_time = True

    @staticmethod
    def _get(client: DropboxClient) -> list:
        """ Get files from Dropbox.
            """
        try:
            metadata = client.metadata('/')
        except (MaxRetryError, ErrorResponse):
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

    def _upload(self, client: DropboxClient):
        """ Upload new files from directory.
            """
        for filename in listdir(self.directory):
            if fnmatch(filename, '*.upl'):
                continue
            local_name = '/' + filename
            full_name = path.join(self.directory, filename)
            upl_name = "{}.upl".format(full_name)
            now = time()
            if path.isfile(upl_name) and stat(full_name).st_mtime < now - 5 * 60:
                with open(full_name, 'rb') as file_stream:
                    try:
                        client.put_file(local_name, file_stream)
                        share = client.share(local_name)
                    except (MaxRetryError, ErrorResponse):
                        continue
                with DatabaseConnection() as db:
                    update = """
                    UPDATE events
                       SET url = '{}',
                           uploaded = current_timestamp
                     WHERE file = '{}'
                    """.format(share['url'], full_name)
                    db.dml(update)
                try:
                    mknod(upl_name)
                except FileExistsError:
                    pass
                print("{} was uploaded to Dropbox.".format(filename))

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
            except (MaxRetryError, ErrorResponse):
                pass

    def run(self):
        """ Upload logic.
            """
        if self.first_time:
            return
        print("Uploading from {} to Dropbox.".format(self.directory))
        try:
            # noinspection PyDeprecation
            client = DropboxClient(self.access_token)
            while True:
                self._upload(client)
                files = self._get(client)
                if files is not None:
                    self._rotate(client, files)
                sleep(2 * 60)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            print()
            print("No longer uploading from {} to Dropbox.".format(self.directory))


if __name__ == '__main__':
    my_daemon = UploadDaemon(settings.config.working_dir)
    init(my_daemon)
