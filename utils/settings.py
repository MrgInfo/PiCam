#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Basic settings.
    """

from configparser import ConfigParser
from os import path, mkdir

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
    def host(self) -> str:
        """ MySQL database network name.
            """
        return self.config.get('Database', 'Host', fallback='localhost')

    @property
    def user(self) -> str:
        """ MySQL database user.
            """
        return self.config.get('Database', 'User', fallback='picam')

    @property
    def password(self) -> str:
        """ MySQL database password.
            """
        return self.config.get('Database', 'Password', fallback='')

    @property
    def working_dir(self) -> str:
        """ The working directory.
            """
        directory = self.config.get('Main', 'WorkingDir', fallback='/var/local/PiCam')
        if not path.exists(directory):
            mkdir(directory)
        return directory

    @property
    def access_token(self) -> str:
        """ Dropbox OAuth 2 authorization token.
            """
        return self.config.get('Dropbox', 'Access', fallback=None)

    @access_token.setter
    def access_token(self, val: str):
        """ Dropbox OAuth 2 authorization token.
            """
        self.config.set('Dropbox', 'Access', val)
        self.save()

    def defaults(self):
        """ Default settings.
            """
        self.config.add_section('Main')
        self.config.set('Main', 'WorkingDir', '/var/local/PiCam')
        self.config.add_section('Database')
        self.config.set('Database', 'Host', 'localhost')
        self.config.set('Database', 'User', 'picam')
        self.config.set('Database', 'Password', '')
        self.config.add_section('Dropbox')
        self.config.set('Dropbox', 'Access', '')

    def load(self):
        """ Load settings from file.
            """
        if path.exists(self.config_file):
            self.config.read(self.config_file)
            return True
        return False

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
found = config.load()


if __name__ == '__main__':
    if not found:
        config.defaults()
        config.save()
    print(config)
