#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Basic settings.
"""

from configparser import ConfigParser
from os import path

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

__all__ = ['Settings', 'config']


class Settings:
    """ PiCam config settings.
        """

    config_file = path.join(path.dirname(__file__), '..', 'PiCam.cfg')
    config = ConfigParser()

    @property
    def host(self):
        """ MySQL database network name.
            """
        return self.config.get('Database', 'Host', fallback='localhost')

    @property
    def user(self):
        """ MySQL database user.
            """
        return self.config.get('Database', 'User', fallback='picam')

    @property
    def password(self):
        """ MySQL database password.
            """
        return self.config.get('Database', 'Password', fallback='')

    @property
    def working_dir(self):
        """ The working directory.
            """
        return self.config.get('Main', 'WorkingDir', fallback='/var/local/PiCam')

    @property
    def access_token(self):
        """ Dropbox authorization code.
            """
        return self.config.get('Dropbox', 'Access', fallback=None)

    @access_token.setter
    def access_token(self, val):
        self.config.set('Dropbox', 'Access', val)
        self.save()

    def load(self):
        """ Load settings from file.
            """
        if path.exists(self.config_file):
            self.config.read(self.config_file)

    def save(self):
        """ Save settings to file.
            """
        with open(self.config_file, 'w') as fs:
            self.config.write(fs)

    def __str__(self):
        """ Show sections.
            """
        return str(self.config.sections())

config = Settings()
config.load()

if __name__ == '__main__':
    print(config)
