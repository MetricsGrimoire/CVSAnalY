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
# This extension calculates the metrics for files at different points in time.

from pycvsanaly2.extensions import Extension, register_extension
from pycvsanaly2.utils import uri_to_filename
from pycvsanaly2.extensions.DBTable import DBTable


class TableMetricsEvo(DBTable):
    """Class for managing the metrics_evo table.

    This table is used for storing the evolution over time
    of the considered metrics"""

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = "CREATE TABLE metrics_evo (" + \
                               "id integer primary key," + \
                               "branch_id integer," + \
                               "date datetime," + \
                               "loc integer," + \
                               "sloc integer," + \
                               "files integer" + \
                               ")"

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = "CREATE TABLE metrics_evo (" + \
                              "id INTEGER PRIMARY KEY," + \
                              "branch_id INTEGER," + \
                              "date DATETIME," + \
                              "loc INTEGER," + \
                              "sloc INTEGER," + \
                              "files INTEGER" + \
                              ") CHARACTER SET=utf8"

    # SQL string for getting the max id in table
    _sql_max_id = "SELECT max(id) FROM metrics_evo"

    # SQL string for inserting a row in table
    _sql_row_insert = "INSERT INTO metrics_evo " + \
                      "(id, branch_id, date, loc, sloc, files) VALUES (%s,%s,%s,%s,%s,%s)"

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    # In this case, this is the commit id (for commits in repository_id)
    _sql_select_rows = "SELECT id FROM metrics_evo # %s"


class TableMonths(DBTable):
    """Class having one month per row.

    This table is used for joining for some queries"""

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = "CREATE TABLE months (" + \
                               "id integer primary key," + \
                               "date datetime" + \
                               ")"

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = "CREATE TABLE months (" + \
                              "id INTEGER PRIMARY KEY," + \
                              "date DATETIME" + \
                              ") CHARACTER SET=utf8"

    # SQL string for getting the max id in table
    _sql_max_id = "SELECT max(id) FROM months"

    # SQL string for inserting a row in table
    _sql_row_insert = "INSERT INTO months " + \
                      "(id, date) VALUES (%s, %s)"

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    # In this case, this is the commit id (for commits in repository_id)
    _sql_select_rows = "SELECT id FROM months # %s"


class MetricsEvo(Extension):
    """Extension to calculate the metrics for files at different points in time."""

    deps = ['Metrics']

    def _get_repo_id(self, repo, uri):
        """Get repository id from repositories table"""

        path = uri_to_filename(uri)
        if path is not None:
            repo_uri = repo.get_uri_for_path(path)
        else:
            repo_uri = uri
        self.cursor.execute("SELECT id FROM repositories WHERE uri = '%s'" % repo_uri)
        return (self.cursor.fetchone()[0])

    def _metrics_period(self, branch, date):
        """Gets the sum of metrics for all files present in the repo.

        Uses a query to learn which files are present in the repository
        at a certain date, for a given branch. Returns metrics learned.

        Uses self.cursor for reading from the database
        """

        # Next SELECT is not that complex.
        # Get all file, commit, type from actions, for a
        # given branch, that are prior to the given date.
        # Then, group them by file, and get the max commit for each group.
        # That is the most recent commit for each file prior to the date.
        # Then, for each of those file, max commit, get
        # only those that are not delete actions (which would mean
        # the file is no longer in the repo for the date)
        # get the metrics for each of those files, and sum them
        query = """
            SELECT SUM(m.loc), SUM(m.sloc), COUNT(m.loc)
            FROM
             (SELECT maxcommits.file_id, max_commit, type
              FROM
               (SELECT file_id, MAX(commit_id) max_commit
                FROM
                 (SELECT a.file_id, a.commit_id, a.type
                  FROM actions a, scmlog s
                  WHERE a.commit_id = s.id AND
                    a.branch_id=%s AND
                    s.date < "%s"
                 ) actdate
                GROUP BY file_id
               ) maxcommits, actions a
              WHERE maxcommits.file_id = a.file_id AND
                maxcommits.max_commit = a.commit_id AND
                type <> 'D'
             ) c, metrics m
            WHERE c.file_id = m.file_id AND
              c.max_commit = m.commit_id"""
        self.cursor.execute(query % (branch, date))
        (loc, sloc, files) = self.cursor.fetchone()
        if loc is None:
            loc = 0
        if sloc is None:
            sloc = 0
        return (loc, sloc, files)

    def run(self, repo, uri, db):
        """Fill in the annual_metrics table.

        For each file in the repository, and for each year since the repository
        started, find the most recent metrics calculated for that file, but not
        older than the end of the year. Do that for all the branches
        """

        cnn = db.connect()
        # Cursor for reading from the database
        self.cursor = cnn.cursor()
        # Cursor for writing to the database
        write_cursor = cnn.cursor()
        repo_id = self._get_repo_id(repo, uri)

        self.cursor.execute("SELECT MIN(date) FROM scmlog")
        minDate = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT MAX(date) FROM scmlog")
        maxDate = self.cursor.fetchone()[0]

        # First month is 0, last month is lastMonth
        lastMonth = (maxDate.year - minDate.year) * 12 + maxDate.month - minDate.month
        self.cursor.execute("SELECT id FROM branches")
        branches = [row[0] for row in self.cursor.fetchall()]

        # Fill in months, with months considered
        theTableMonths = TableMonths(db, cnn, repo_id)
        for period in range(0, lastMonth):
            month = (minDate.month + period) % 12 + 1
            year = minDate.year + (period + minDate.month) // 12
            date = str(year) + "-" + str(month) + "-01"
            theTableMonths.add_pending_row(
                (None, date))
        theTableMonths.insert_rows(write_cursor)

        # Fill in metrics_evo, with the metrics for monthly snapshots
        theTableMetricsEvo = TableMetricsEvo(db, cnn, repo_id)
        for branch in branches:
            for period in range(0, lastMonth):
                month = (minDate.month + period) % 12 + 1
                year = minDate.year + (period + minDate.month) // 12
                date = str(year) + "-" + str(month) + "-01"
                (loc, sloc, files) = self._metrics_period(branch, date)
                theTableMetricsEvo.add_pending_row(
                    (None, branch, date, loc, sloc, files))
            theTableMetricsEvo.insert_rows(write_cursor)
        cnn.commit()
        write_cursor.close()
        self.cursor.close()
        cnn.close()


register_extension("MetricsEvo", MetricsEvo)
