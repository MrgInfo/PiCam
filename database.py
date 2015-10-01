#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manage database.
"""

import pymysql

__all__ = ['Database']
__author__ = "wavezone"
__email__ = "wavezone@mrginfo.com"
__license__ = "GPL"
__version__ = "1.0"


class Database:
    """
    Wrapper class for database.
    """

    host = 'localhost'
    user = 'pi'
    db = 'motion'

    def __init__(self):
        self.connection = pymysql.connect(host=self.host, user=self.user, db=self.db)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def dml(self, query: str):
        """
        Run data manipulation.
        """
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except pymysql.Error:
            self.connection.rollback()

    def query(self, query: str):
        """
        Query database.
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()


if __name__ == '__main__':
    database = Database()
    for row in database.query("SELECT * FROM events"):
        print(row)
