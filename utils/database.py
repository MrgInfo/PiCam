#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Manage database.
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

    host = 'localhost'
    user = 'pi'
    db = 'motion'

    def __init__(self):
        self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db)
        self.cursor = self.connection.cursor()

    def __del__(self):
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
        self.cursor.execute(query)
        return self.cursor.fetchall()


if __name__ == '__main__':
    database = Database()
    for row in database.query('SELECT * FROM events'):
        print(row)
