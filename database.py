# -*- coding: utf-8 -*-
"""
Manage database.
"""

import MySQLdb

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
        self.connection = MySQLdb.connect(host=self.host, user=self.user, db=self.db)
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
        except MySQLdb.Error:
            self.connection.rollback()

    def query(self, query: str):
        """
        Query database.
        """
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query)
        return cursor.fetchall()
