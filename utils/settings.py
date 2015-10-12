#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Basic settings.
"""

from os.path import exists

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

__all__ = ['working_dir']

DEFAULT_DIR = '/var/local/PiCam'


def working_dir() -> str:
    """
    The working directory.
    """
    new_dir = DEFAULT_DIR
    while not exists(new_dir):
        new_dir = input("Please provide a working directory: ").strip()
    return new_dir


if __name__ == '__main__':
    print(working_dir())
