import sqlite3 as lite
import sys
import logging
from datetime import datetime
from job import Job

class SQLiteHelper(object):
    con = None

    def __init__(self, db_name):
        self.db_name = db_name

    def execute(self, query, all, data=None):
        try:
            con = lite.connect(self.db_name)
            cursor = con.cursor()
        except lite.Error, e:
            logging.error("Error {0}:".format(e.args[0]))
        try:
            results = None
            cursor_execute = None
            if data is not None:
                cursor_execute = cursor.execute(query, data)
            else:
                cursor_execute = cursor.execute(query)

            if all:
                results = cursor_execute.fetchall()
            else:
                results = cursor_execute.fetchone()
            con.commit()
            return results
            con.close()
        except lite.Error, e:
            logging.error("Error {0}:".format(e.args[0]))
        except Exception, e:
            logging.error("Error running query: {0} ".format(query))
            logging.error(e)
        finally:
            con.close()

    def fetchall(self, query, data=None):
        if data is not None:
            return self.execute(query, True, data=data)
        else:
            return self.execute(query, True)

    def fetch(self, query, data=None):
        if data is not None:
            return self.execute(query, False, data=data)
        else:
            return self.execute(query, False)
