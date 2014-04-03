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
#       Jesus M. Gonzalez-Barahona <jgb@gsyc.es>

"""Computes lines added, lines removed for every file in every commit.

Produces two tables:

- commits_lines: Lines added, removed for each commit. Should be like the
   the one produced by the CommitsLOC extension (and therefore, this
   extenstion supercedes it)

- commits_files_lines: Lines added, removed for each commit of each file.

Currently only works for git repositories.
"""

import re

import sqlite3
import _mysql_exceptions

from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists)
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.utils import printerr, uri_to_filename
from pycvsanaly2.FindProgram import find_program
from pycvsanaly2.Command import Command, CommandError


class DBTable:
    """Table class, for managing tables with certain common characteristics.

    Usually, a derived class will implement access to real tables
    in the database. This class provides the commno behavior.
    """

    def __init__(self, db, cnn, repo):
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

        cursor = cnn.cursor()
        try:
            # Try to create the table (self.table will be empty)
            self._create_table(cursor)
        except TableAlreadyExists:
            # If the table already exisits, fill in self.table with its data
            self._init_from_table(cursor)
        except Exception, e:
            raise ExtensionRunError(str(e))
        finally:
            cursor.close()

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

    def _create_table_sqlite(self, cursor):
        """Create the table for SQLite.

        Raises exception if the table already exists
        """

        try:
            cursor.execute(self._sql_create_table_sqlite)
            self.cnn.commit()
        except sqlite3.OperationalError:
            raise TableAlreadyExists

    def _create_table_mysql(self, cursor):
        """Create the table for MySQL.

        Raises exception if the table already exists
        """

        try:
            cursor.execute(self._sql_create_table_mysql)
            self.cnn.commit()
        except _mysql_exceptions.OperationalError, e:
            if e.args[0] == 1050:
                raise TableAlreadyExists
            else:
                raise

    def _create_table(self, cursor):
        """Create the table, and raise exception if it already exists.

        TableAlreadyExists is the exception that may be raised."""

        if isinstance(self.db, SqliteDatabase):
            self._create_table_sqlite(cursor)
        elif isinstance(self.db, MysqlDatabase):
            self._create_table_mysql(cursor)
        else:
            raise ExtensionRunError("Database type is not supported " +
                                    "by CommitsLOCDet extension")

    def _init_from_table(self, cursor):
        """Initialize self.table with all rows in commits_lines table."""

        # Find max id in commits_lines, and update counter
        cursor.execute(self._sql_max_id)
        id = cursor.fetchone()[0]
        if id is not None:
            self.counter = id + 1
        # Find all rows and init self.table with them
        cursor.execute(self._sql_select_rows % self.repo)
        self.table = cursor.fetchall()

    def in_table(self, element):
        """Is this element in self.table?"""

        if element in self.table:
            return True
        else:
            return False

    def add_pending_row(self, row):
        """Add row to list of rows pending to be inserted in the table.

        First element in row should be id. If it is None, it is set using
        self.counter. Otherwise, it is left as is."""

        id = row[0]
        if id is None:
            id = self.counter
            self.counter += 1
        self.pending.append((id,) + row[1:])

    def insert_rows(self, cursor):
        """Inserts a list of pending rows into table.

        It also empties the list of pending rows, after insertion."""

        if self.pending:
            cursor.executemany(self._sql_row_insert, self.pending)
            self.pending = []


class TableComLines(DBTable):
    """Class for managing the commits_lines table"""

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = "CREATE TABLE commits_lines (" + \
                               "id integer primary key," + \
                               "commit_id integer," + \
                               "added integer," + \
                               "removed integer" + \
                               ")"

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = "CREATE TABLE commits_lines (" + \
                              "id INT primary key," + \
                              "commit_id INT(11) NOT NULL," + \
                              "added int," + \
                              "removed int," + \
                              "FOREIGN KEY (commit_id) REFERENCES scmlog(id)" + \
                              ") ENGINE=MyISAM DEFAULT CHARACTER SET=utf8"

    # SQL string for getting the max id in table
    _sql_max_id = "SELECT max(id) FROM commits_lines"

    # SQL string for inserting a row in table
    _sql_row_insert = "INSERT INTO commits_lines " + \
                      "(id, commit_id, added, removed) VALUES (%s, %s, %s, %s)"

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    # In this case, this is the commit id (for commits in repository_id)
    _sql_select_rows = "SELECT c.commit_id FROM commits_lines c, scmlog s " + \
                       "WHERE c.commit_id = s.id AND s.repository_id = %s"


class TableComFilLines(DBTable):
    """Class for managing the commits_files_lines table"""

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = "CREATE TABLE commits_files_lines (" + \
                               "id integer primary key," + \
                               "commit integer," + \
                               "path varchar," + \
                               "added integer," + \
                               "removed integer" + \
                               ")"

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = "CREATE TABLE commits_files_lines (" + \
                              "id INTEGER PRIMARY KEY," + \
                              "commit INT(11) NOT NULL," + \
                              "path VARCHAR(255)," + \
                              "added INTEGER," + \
                              "removed INTEGER," + \
                              "FOREIGN KEY (commit) REFERENCES scmlog(id)" + \
                              ") ENGINE=MyISAM DEFAULT CHARACTER SET=utf8"

    # SQL string for getting the max id in table
    _sql_max_id = "SELECT max(id) FROM commits_files_lines"

    # SQL string for inserting a row in table
    _sql_row_insert = "INSERT INTO commits_files_lines " + \
                      "(id, commit, path, added, removed) VALUES (%s, %s, %s, %s, %s)"

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    # In this case, this is the pair commit id and path
    _sql_select_rows = "SELECT c.commit, c.path " + \
                       "FROM commits_files_lines c, scmlog s " + \
                       "WHERE c.commit = s.id AND s.repository_id = %s"


class LineCounter:
    """Generic line counter, root of the hierarchy.

    Will specialized in counters for specific kinds of repositories.
    """

    def __init__(self, repo, uri):
        self.repo = repo
        self.uri = uri

    def get_lines_for_revision(self, revision):
        raise NotImplementedError


class GitLineCounter(LineCounter):
    def __init__(self, repo, uri):
        LineCounter.__init__(self, repo, uri)

        self.commit_pattern = re.compile("^(\w+) ")
        self.file_pattern = re.compile("^(\d+)\s+(\d+)\s+([^\s].*)$")

        # Dictionary for storing added, removed pairs, keyed by commit.
        self.lines = {}
        # Dictionary for storing list of paths, keyed by commit.
        self.paths = {}
        # Dictionary for storing added, removed pairs, keyed by commit.
        # and path
        self.lines_files = {}

        # Run git command
        self.git = find_program('git')
        if self.git is None:
            raise ExtensionRunError("Error running CommitsLOCDet extension: " +
                                    "required git command cannot be found in path")
        cmd = [self.git, 'log',
               '--all', '--topo-order', '--numstat', '--pretty=oneline']
        c = Command(cmd, uri)
        try:
            c.run(parser_out_func=self.__parse_line)
        except CommandError, e:
            if e.error:
                printerr("Error running git log command: %s", (e.error,))
            raise ExtensionRunError("Error running " +
                                    "CommitsLOCDet extension: %s", str(e))

    def __parse_line(self, line):
        """Parse a line from the git log.

        Fills in the dictionaries self.lines and self.lines_files.

        Two kinds of patterns are matched to the lines in the git log:
        - self.commit_pattern.match. commit lines: commit hash, comment
        - self.file_pattern.match. file lines: added, removed, path
           In some cases, added, removed are not numbers, but "-".
           For now, those lines are silently removed.
        """

        match = self.commit_pattern.match(line)
        if match:
            self.commit = match.group(1)
            self.added = 0
            self.removed = 0
            self.paths[self.commit] = []
        else:
            match = self.file_pattern.match(line)
            if match:
                file_added = match.group(1)
                file_removed = match.group(2)
                file_name = match.group(3)
                self.paths[self.commit].append(file_name)
                self.lines_files[self.commit + ',' + file_name] = \
                    (file_added, file_removed)
                self.added += int(file_added)
                self.removed += int(file_removed)
                self.lines[self.commit] = (self.added, self.removed)

    def get_lines_for_commit(self, commit):
        """Get lines added, removed for a given commit."""

        return self.lines.get(commit, (0, 0))

    def get_paths_for_commit(self, commit):
        """Get lines added, removed for a given commit."""

        return self.paths.get(commit, [])

    def get_lines_for_commit_file(self, commit, path):
        """Get lines added, removed for a given commit & file path pair."""

        return self.lines_files.get(commit + ',' + path, (0, 0))


_counters = {
    'git': GitLineCounter
}


def create_line_counter_for_repository(repo, uri):
    """Creates and returns a counter for the kind of repository specified.

    Raises exception if repository is not supported.
    """

    try:
        counter = _counters[repo.get_type()]
    except KeyError:
        error = "Repository type %s is not supported " + \
                "by CommitsLOCDet extension"
        raise ExtensionRunError(error % (repo.get_type()))
    return counter(repo, uri)


class CommitsLOCDet(Extension):
    def _get_repo_id(self, repo, uri, cursor):
        """Get repository id from repositories table"""

        path = uri_to_filename(uri)
        if path is not None:
            repo_uri = repo.get_uri_for_path(path)
        else:
            repo_uri = uri
        cursor.execute("SELECT id FROM repositories WHERE uri = '%s'" %
                       repo_uri)
        return (cursor.fetchone()[0])

    def run(self, repo, uri, db):
        """Fill in the commits_lines table.

        Create a counter to find number of lines added and removed
        for each commit in repo,
        create an object to manage the commits_lines table,
        for each commit in repo, create an entry in commit_lines table
        (except for those that already were in the table).
        """

        cnn = db.connect()
        # Cursor for reading from the database
        cursor = cnn.cursor()
        # Cursor for writing to the database
        write_cursor = cnn.cursor()
        repo_id = self._get_repo_id(repo, uri, cursor)
        # Counter to find lines added, removed for each commit
        counter = create_line_counter_for_repository(repo, uri)
        # Object to manage the commits_lines table
        theTableComLines = TableComLines(db, cnn, repo_id)
        # Object to manage the commits_files_lines table
        theTableComFilLines = TableComFilLines(db, cnn, repo_id)

        cursor.execute("SELECT id, rev, composed_rev " +
                       "FROM scmlog WHERE repository_id = '%s'",
                       (repo_id,))
        rows_left = True
        while rows_left:
            rows = cursor.fetchmany()
            for id, revision, composed_rev in rows:
                if composed_rev:
                    commit = revision.split("|")[0]
                else:
                    commit = revision
                cadded = cremoved = 0
                if not theTableComLines.in_table(id):
                    (cadded, cremoved) = counter.get_lines_for_commit(commit)
                    theTableComLines.add_pending_row((None, id,
                                                      cadded, cremoved))
                tadded = tremoved = 0
                for path in counter.get_paths_for_commit(commit):
                    if not theTableComFilLines.in_table(str(id) + ',' + path):
                        (added, removed) = \
                            counter.get_lines_for_commit_file(commit, path)
                        theTableComFilLines.add_pending_row((None, id, path,
                                                             added, removed))
                        tadded += int(added)
                        tremoved += int(removed)
                # Sanity check
                if (cadded != tadded) or (cremoved != tremoved):
                    printerr("Sanity check failed: %d, %s, %d, %d, %d, %d" %
                             (id, commit, cadded, tadded, cremoved, tremoved))
                    printerr(counter.get_paths_for_commit(commit))
            theTableComLines.insert_rows(write_cursor)
            theTableComFilLines.insert_rows(write_cursor)
            if not rows:
                rows_left = False
        cnn.commit()
        write_cursor.close()
        cursor.close()
        cnn.close()


register_extension("CommitsLOCDet", CommitsLOCDet)
