#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Manage database.

CREATE DATABASE motion DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;

USE motion;
CREATE TABLE IF NOT EXISTS events (
  file varchar(200) COLLATE utf8_bin NOT NULL,
  size int(11) DEFAULT NULL,
  diff_cnt int(11) DEFAULT NULL,
  time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  url varchar(500) COLLATE utf8_bin DEFAULT NULL,
  uploaded timestamp NULL DEFAULT NULL,
  PRIMARY KEY (file)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE USER 'picam'@'localhost';
GRANT ALL ON motion.* TO 'picam'@'localhost';
"""

import pymysql

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

__all__ = ['Database']


class Database:
    """Wrapper class for database."""

    db = 'motion'
    user = 'picam'

    def __init__(self):
        self.connection = pymysql.connect(user=self.user, db=self.db)
        self.cursor = self.connection.cursor()

    def __del__(self):
        if(
            hasattr(self, 'connection') and
            (self.connection is not None) and
            hasattr(self.connection, 'socket') and
            (self.connection.socket is not None)
        ):
            self.connection.close()

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exception_type, exception_value, traceback):
        self.connection.close()

    def dml(self, query: str):
        """Run data manipulation."""
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except pymysql.Error:
            self.connection.rollback()

    def query(self, query: str):
        """Query database."""
        cnt = self.cursor.execute(query)
        if cnt == 0:
            return None
        else:
            return self.cursor.fetchall()


if __name__ == '__main__':
    database = Database()
    events = """
    SELECT *
      FROM events
    """
    for row in database.query(events):
        print(row)
