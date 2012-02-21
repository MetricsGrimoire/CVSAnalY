# Copyright (C) 2012 LibreSoft
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
#       Jesus M. Gonzalez-Barahona  <jgb@gsyc.es>

# Description
# -----------
# This extension extracts words from commit messages, and does some
# analysis on them

import pysqlite2.dbapi2
import _mysql_exceptions

from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.utils import uri_to_filename
#from pycvsanaly2.extensions.CommitsLocDet import DBTable
from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase,
                                  TableAlreadyExists,
                                  statement, DBFile)

class DBTable:
    """Table class, for managing tables with certain common characteristics.

    Usually, a derived class will implement access to real tables
    in the database. This class provides the commno behavior.
    """

    def __init__ (self, db, cnn, repo):
        """Initialize the table.

        Initialization can be either by creating it or by getting rows
        from and already existing table.
        If the table already exists, rows are got from it, so that new rows
        are compared with them before inserting (we don't want to
        re-insert already inserted rows).
        If the table does not exists, create it.

        db: database holding the table.
        cnn: connection to that database
        repo: git repository
        """

        # Counter for unique row ids
        self.counter = 1
        # Rows already in table
        self.table = []
        # Rows still not inserted in the table table
        self.pending = []

        # Initialize variables related to the database
        self.db = db
        self.cnn = cnn
        self.repo = repo

        cursor = cnn.cursor ()
        try:
            # Try to create the table (self.table will be empty)
            self._create_table (cursor)
        except TableAlreadyExists:
            # If the table already exisits, fill in self.table with its data
            self._init_from_table (cursor)
        except Exception, e:
            raise ExtensionRunError (str (e))
        finally:
            cursor.close ()

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = ""

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = ""

    # SQL string for getting the max id in table
    _sql_max_id = ""

    # SQL string for inserting a row in table. Should be redefined by
    # derived classes
    _sql_row_insert = ""

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    _sql_select_rows = ""

    def _create_table_sqlite (self, cursor):
        """Create the table for SQLite.
        
        Raises exception if the table already exists
        """

        try:
            cursor.execute (self._sql_create_table_sqlite)
            self.cnn.commit ()
        except pysqlite2.dbapi2.OperationalError:
            raise TableAlreadyExists

    def _create_table_mysql (self, cursor):
        """Create the table for MySQL.

        Raises exception if the table already exists
        """

        try:
            cursor.execute (self._sql_create_table_mysql)
            self.cnn.commit ()
        except _mysql_exceptions.OperationalError, e:
            if e.args[0] == 1050:
                raise TableAlreadyExists
            else:
                raise

    def _create_table (self, cursor):
        """Create the table, and raise exception if it already exists.

        TableAlreadyExists is the exception that may be raised."""

        if isinstance (self.db, SqliteDatabase):
            self._create_table_sqlite(cursor)
        elif isinstance (self.db, MysqlDatabase):
            self._create_table_mysql(cursor)
        else:
            raise ExtensionRunError ("Database type is not supported " + 
                                     "by CommitsLOCDet extension")

    def _init_from_table (self, cursor):
        """Initialize self.table with all rows in commits_lines table."""

        # Find max id in commits_lines, and update counter
        cursor.execute (self._sql_max_id)
        id = cursor.fetchone ()[0]
        if id is not None:
            self.counter = id + 1
        # Find all rows and init self.table with them
        cursor.execute (self._sql_select_rows % self.repo)
        self.table = cursor.fetchall()

    def in_table (self, element):
        """Is this element in self.table?"""

        if element in self.table:
            return True
        else:
            return False

    def add_pending_row (self, row):
        """Add row to list of rows pending to be inserted in the table.

        First element in row should be id. If it is None, it is set using
        self.counter. Otherwise, it is left as is."""

        id = row[0]
        if id is None:
            id = self.counter
            self.counter += 1
        self.pending.append ((id,) + row[1:])

    def insert_rows (self, cursor):
        """Inserts a list of pending rows into table.

        It also empties the list of pending rows, after insertion."""

        if self.pending:
            cursor.executemany (self._sql_row_insert, self.pending)
            self.pending = []



class TableWords (DBTable):
    """Class for managing the words_freq table"""

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = "CREATE TABLE words_freq (" + \
        "id integer primary key," + \
        "period integer," + \
        "word varchar," + \
        "times integer" + \
        ")"

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = "CREATE TABLE words_freq (" + \
        "id INTEGER PRIMARY KEY," + \
        "period INTEGER," + \
        "word VARCHAR(80)," + \
        "times INTEGER" + \
        ") CHARACTER SET=utf8"

    # SQL string for getting the max id in table
    _sql_max_id = "SELECT max(id) FROM words_freq"

    # SQL string for inserting a row in table
    _sql_row_insert = "INSERT INTO words_freq " + \
        "(id, period, word, times) VALUES (%s, %s, %s, %s)"

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    # In this case, this is the commit id (for commits in repository_id)
    _sql_select_rows = "SELECT id FROM words_freq # %s"

class MessageWords (Extension):
    """Extension to do some analysis on commit messages.

    It works on the messages field of the scmlog table.
    """

    def _get_repo_id (self, repo, uri, cursor):
        """Get repository id from repositories table"""
    
        path = uri_to_filename (uri)
        if path is not None:
            repo_uri = repo.get_uri_for_path (path)
        else:
            repo_uri = uri
        cursor.execute ("SELECT id FROM repositories WHERE uri = '%s'" % 
                        repo_uri)
        return (cursor.fetchone ()[0])

    def run (self, repo, uri, db):
        """Extract commit message from scmlog table and do some analysis.
        """

        cnn = db.connect ()
        # Cursor for reading from the database
        cursor = cnn.cursor ()
        # Cursor for writing to the database
        write_cursor = cnn.cursor ()
        repo_id = self._get_repo_id (repo, uri, cursor)

        cursor.execute ("SELECT MIN(date) FROM scmlog")
        minDate = cursor.fetchone ()[0]
        cursor.execute ("SELECT MAX(date) FROM scmlog")
        maxDate = cursor.fetchone ()[0]

        theTableWords = TableWords(db, cnn, repo_id)

        # First month is 0, last month is lastMonth
        lastMonth = (maxDate.year - minDate.year) * 12 + \
            maxDate.month - minDate.month
        for period in range (0, lastMonth):
            wordsFreq = {}
            year = minDate.year + period // 12
            month = minDate.month + period % 12
            query = "SELECT log.message " + \
                "FROM scmlog log " + \
                "WHERE year(log.date) = %s " + \
                "AND month(log.date) = %s "
            cursor.execute (query % (year, month))
            rows = cursor.fetchall()
            print "*** Year, month: " + str(year) + ", " + str(month)
            for message in rows:
                words = message[0].lower().split ()
                print words
                for word in words:
                    if word in wordsFreq:
                        wordsFreq[word] += 1
                    else:
                        wordsFreq[word] = 1
            print wordsFreq
            for word in wordsFreq:
                theTableWords.add_pending_row ((None, period,
                                                word, wordsFreq[word]))
            theTableWords.insert_rows (write_cursor)
        #cnn.commit ()
        write_cursor.close ()
        cursor.close ()
        cnn.close ()

register_extension ("MessageWords", MessageWords)

