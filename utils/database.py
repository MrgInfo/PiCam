#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Manage database 'motion'.
    """

from pymysql.err import OperationalError, MySQLError
import pymysql

try:
    from utils import settings
except ImportError:
    # noinspection PyUnresolvedReferences
    import settings

__author__ = "wavezone"
__copyright__ = "Copyright 2015, MRG-Infó Bt."
__credits__ = ["Groma István (wavezone)"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Groma István"
__email__ = "wavezone@mrginfo.com"

__all__ = ['Database']


class Database:
    """ Wrapper class for database.
        """

    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host=settings.config.host,
                user=settings.config.user,
                password=settings.config.password,
                db='motion')
            self.cursor = self.connection.cursor()
        except MySQLError:
            self.connection = None
            self.cursor = None

    def __del__(self):
        if hasattr(self, 'connection') and (self.connection is not None):
            try:
                self.connection.close()
            except MySQLError:
                pass

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exception_type, exception_value, traceback):
        if hasattr(self, 'connection') and (self.connection is not None):
            try:
                self.connection.close()
            except MySQLError:
                pass

    def dml(self, query: str):
        """ Run data manipulation.

            :param query: SQL
            """
        if hasattr(self, 'cursor') and (self.cursor is not None)\
                and hasattr(self, 'connection') and (self.connection is not None):
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except OperationalError:
                pass
            except MySQLError:
                self.connection.rollback()

    def query(self, query: str):
        """ Query database.

            :param query: SQL
            """
        if hasattr(self, 'cursor') and (self.cursor is not None):
            try:
                cnt = self.cursor.execute(query)
                if cnt == 0:
                    return None
                else:
                    return self.cursor.fetchall()
            except MySQLError:
                pass


if __name__ == '__main__':
    database = Database()
    events = """
    SELECT *
      FROM events
    """
    for row in database.query(events):
        print(row)
