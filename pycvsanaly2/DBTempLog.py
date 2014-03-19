# Copyright (C) 2008 LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from ContentHandler import ContentHandler
from Database import SqliteDatabase, MysqlDatabase, TableAlreadyExists, statement, ICursor
from Repository import Commit
from AsyncQueue import AsyncQueue

import threading
from cStringIO import StringIO
from cPickle import dump, load


class DBTempLog:
    INTERVAL_SIZE = 100

    def __init__(self, db):
        self.db = db

        self._need_clear = False

        try:
            self.__create_table()
        except TableAlreadyExists:
            # FIXME: we can use this to recover from a crash
            self._need_clear = True
            self.__drop_table()
            self.__create_table()

        self.queue = AsyncQueue(50)
        self.writer_thread = threading.Thread(target=self.__writer,
                                              args=(self.queue,))
        self.writer_thread.setDaemon(True)
        self.writer_thread.start()

    def __create_table(self):
        cnn = self.db.connect()
        cursor = cnn.cursor()

        if isinstance(self.db, SqliteDatabase):
            import sqlite3

            try:
                cursor.execute("CREATE TABLE _temp_log (" +
                               "id integer primary key autoincrement," +
                               "rev varchar," +
                               "date datetime," +
                               "object blob" +
                               ")")
            except sqlite3.OperationalError:
                cursor.close()
                raise TableAlreadyExists
            except:
                raise
        elif isinstance(self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute("CREATE TABLE _temp_log (" +
                               "id INT AUTO_INCREMENT PRIMARY KEY," +
                               "rev mediumtext," +
                               "date datetime," +
                               "object LONGBLOB" +
                               ") CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    cursor.close()
                    raise TableAlreadyExists
                raise
            except:
                raise

        cnn.commit()
        cursor.close()
        cnn.close()

        self._need_clear = True

    def __drop_table(self):
        if not self._need_clear:
            return

        cnn = self.db.connect()
        cursor = cnn.cursor()
        cursor.execute("DROP TABLE _temp_log")
        cnn.commit()
        cursor.close()
        cnn.close()

        self._need_clear = False

    def __writer(self, queue):
        cnn = self.db.connect()
        cursor = cnn.cursor()

        commits = []
        n_commits = 0
        while True:
            commit = queue.get()

            if not isinstance(commit, Commit):
                queue.done()
                break

            io = StringIO()
            dump(commit, io, -1)
            obj = io.getvalue()
            io.close()

            commits.append((commit.revision, commit.date, self.db.to_binary(obj)))
            n_commits += 1
            del commit

            if n_commits == 50:
                cursor.executemany(
                    statement("INSERT into _temp_log (rev, date, object) values (?, ?, ?)", self.db.place_holder),
                    commits)
                cnn.commit()
                del commits
                commits = []
                n_commits = 0

            queue.done()

        if commits:
            cursor.executemany(
                statement("INSERT into _temp_log (rev, date, object) values (?, ?, ?)", self.db.place_holder), commits)
            cnn.commit()
            del commits

        cursor.close()
        cnn.close()

    def insert(self, commit):
        self.queue.put(commit)

    def foreach(self, cb, order=None):
        self.flush()

        cnn = self.db.connect()

        if order is None or order == ContentHandler.ORDER_REVISION:
            query = "SELECT object from _temp_log order by id desc"
        else:
            query = "SELECT object from _temp_log order by date asc"

        # We need to split the query to save memory
        icursor = ICursor(cnn.cursor(), self.INTERVAL_SIZE)
        icursor.execute(statement(query, self.db.place_holder))
        rs = icursor.fetchmany()
        while rs:
            for t in rs:
                obj = t[0]
                io = StringIO(obj)
                commit = load(io)
                io.close()
                cb(commit)

            rs = icursor.fetchmany()

        icursor.close()
        cnn.close()

    def flush(self):
        self.queue.join()
        if self.writer_thread.isAlive():
            # Tell the thread to exit
            # The value doesn't really matter
            self.queue.put("END")
            self.writer_thread.join()

    def clear(self):
        self.__drop_table()

    def __del__(self):
        self.flush()
        self.clear()
