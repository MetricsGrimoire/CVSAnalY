import MySQLdb
import os


class MyDatabase:

    def __init__(self):

        self.user = ""
        self.password = ""
        self.host = ""
        self.name = ""

        self.cursor = None
        self.connection = None

    def connect(self):

        self.connection = MySQLdb.connect(host = self.host,
                                          user = self.user,
                                          passwd = self.password,
                                          db = self.name)

        self.cursor = self.connection.cursor()

    def getFilenameRevisionList(self, where = None):
        query = 'SELECT fileraw, revision, date(date_log), time(date_log) from log'

        if where:
            query += ' '+where+';'
        else:
            query += ';'

        self.cursor.execute(query)

    def insertFile(self, orig_filename,comp_filename, revision, rev_date, rev_time, sha1, nilsimsa, filedir):

        filepath = filedir + comp_filename

        query = 'INSERT INTO sourcefiles (filename,revision,rev_date,rev_time,sha1,nilsimsa,content) VALUES ('

        query += '"'+orig_filename+'", "'
        query += revision + '", "'
        query += str(rev_date) + '", "'
        query += str(rev_time) + '", "'
        query += sha1 + '", "'
        query += nilsimsa + '", '
        query += 'LOAD_FILE("'+filepath+'"));'

        self.cursor.execute(query)

