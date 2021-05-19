import logging
import mysql.connector as mysql
from entities.webutils import WebUtils


class Context(object):

    def __init__(self):
        self.wu = WebUtils()

    def logging(self, type, message):
        with open("brickv2/log/log_{}.csv".format(type), "a") as myfile:
            myfile.write("{}\n".format(message))

    def execute(self, statement):
        return self.query(statement, False)

    def query(self, statement, return_data=True):
        try:
            db = mysql.connect(
                host="au2.fcomet.com",
                user="allinson_brick",
                passwd="brick^913971",
                database="allinson_brick",
                port='3306'
            )
            cursor = db.cursor()
            cursor.execute(statement)
            if return_data:
                return cursor.fetchall()
            else:
                db.commit()
                return None
        except Exception as e:
            logging.error('{}'.format(e))



        # with contextlib.closing(sqlite3.connect('brick/data/bricks.db')) as conn:  # auto-closes
        #     with conn:  # auto-commits
        #         with contextlib.closing(conn.cursor()) as cursor:  # auto-closes
        #             try:
        #                 cursor.execute(statement)
        #                 self.logging('db', '{},{}'.format(datetime.datetime.now(),statement))
        #                 return cursor.fetchall()
        #             except Exception as e:
        #                 logging.error('            [!] Error running query [{}]: {}'.format(statement, e))
        #                 return None
