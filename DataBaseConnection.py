__author__ = 'SHostetter'
import getpass
import psycopg2

class DBconnection(object):
    def __init__(self, db_name):
        self.params = {
            'dbname': db_name,
            'user': 'FoodApp_User',
            'password': 'FoodApp_User',
            'host': 'localhost',
            'port': 5432
        }
        print "\n" * 100  # get pass off screen for IDLE run
        self.conn = self.conn = psycopg2.connect(**self.params)

    def dbConnect(self):
        self.conn = psycopg2.connect(**self.params)

    def dbClose(self):
        self.conn.close()