import sqlite3
import contextlib
import logging
import datetime
from entities.webutils import WebUtils


class Context(object):

    def __init__(self):
        self.wu = WebUtils()

    def logging(self, type, message):
        with open("brick/log/log_{}.csv".format(type), "a") as myfile:
            myfile.write("{}\n".format(message))

    def query(self, statement):
        with contextlib.closing(sqlite3.connect('brick/data/bricks.db')) as conn:  # auto-closes
            with conn:  # auto-commits
                with contextlib.closing(conn.cursor()) as cursor:  # auto-closes
                    try:
                        cursor.execute(statement)
                        self.logging('db', '{},{}'.format(datetime.datetime.now(),statement))
                        return cursor.fetchall()
                    except Exception as e:
                        logging.error('            [!] Error running query [{}]: {}'.format(statement, e))
                        return None
