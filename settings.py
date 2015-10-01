#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic settings.
"""

from os.path import exists, join
from os import makedirs
import sys
import logging
import logging.handlers

__all__ = ['working_dir', 'create_logger']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"

DEFAULT_DIR = '/var/local/motion'
LOG_DIR = '/var/log/python'


def working_dir() -> str:
    """T
    he working directory.
    """
    if len(sys.argv) > 1 and exists(sys.argv[1]):
        new_dir = sys.argv[1]
    else:
        new_dir = DEFAULT_DIR
    while not exists(new_dir):
        new_dir = input("Please provide a working directory: ")
    return new_dir


def create_logger(obj: object) -> logging.Logger:
    """
    Creates default file rotationg logger.
    """
    logger = logging.getLogger(obj.__class__.__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if not exists(LOG_DIR):
        makedirs(LOG_DIR)
    logfile = join(LOG_DIR, obj.__class__.__name__ + '.log')
    file_handler = logging.handlers.TimedRotatingFileHandler(logfile, when='midnight', backupCount=10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


if __name__ == '__main__':
    print(working_dir())
