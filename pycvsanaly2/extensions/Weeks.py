# Copyright (C) 2012 LibreSoft
# Copyright (C) 2012 Bitergia
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
#       Jesus M. Gonzalez-Barahona <jgb@gsyc.es>
#       Alvaro del Castillo <acs@bitergia.com>

"""Produces a table with the list of weeks for the life of the repository

Very simple code just to produce, for convenience, a table with one
week per row, starting with the week of the first commit, and ending
with the week of the last commit found in the repository.

This table can be used to select "solid" sets of weeks. GROUP BY would
not produce entries for weeks with no results in the select (eg., weeks
with no commits at all). But in many cases, you need a row with some
parameter for all the weeks, including a 0 when no activity is found. That
can be easily done using this auxiliary table.
"""

from datetime import datetime

from pycvsanaly2.extensions import Extension, register_extension
from pycvsanaly2.extensions.DBTable import DBTable


class WeeksTable(DBTable):
    """Class for managing the weeks table

    Each record in the table has two fields:
      - id: an integer with a week identifier (year * 12 + week)
      - year: an integer with the numeral of the year (eg. 2012)
      - week: an integer with the numeral of the week
      - date: a date for the beginning of the week, eg. 2012-01-01
         for Jan 2012
    """

    # SQL string for creating the table, specialized for SQLite
    _sql_create_table_sqlite = "CREATE TABLE weeks (" + \
                               "id integer primary key," + \
                               "year integer," + \
                               "week integer," + \
                               "date datetime" + \
                               ")"

    # SQL string for creating the table, specialized for MySQL
    _sql_create_table_mysql = "CREATE TABLE weeks (" + \
                              "id INTEGER PRIMARY KEY," + \
                              "year INTEGER," + \
                              "week INTEGER," + \
                              "date DATETIME" + \
                              ") ENGINE=MyISAM" + \
                              " CHARACTER SET=utf8"

    # SQL string for getting the max id in table
    _sql_max_id = "SELECT max(id) FROM weeks"

    # SQL string for inserting a row in table
    _sql_row_insert = "INSERT INTO weeks " + \
                      "(id, year, week, date) VALUES (%s, %s, %s, %s)"

    # SQL string for selecting all rows to fill self.table
    # (rows already in table), corresponding to repository_id
    # Should return a unique identifier which will be key in self.table
    # In this case, this is the commit id (for commits in repository_id)
    _sql_select_rows = "SELECT id FROM weeks # %s"


class Weeks(Extension):
    """Extension to produce a table the list of weeks.

    Includes a list with the list of weeks for the life of the repository,
    with no holes in it (all weeks, have they commits or not, from first
    to last date in repository.
    """

    def run(self, repo, uri, db):
        """ Extract first and last commits
            from scmlog and create the weeks table.
        """

        cnn = db.connect()
        # Cursor for reading from the database
        cursor = cnn.cursor()
        # Cursor for writing to the database
        write_cursor = cnn.cursor()

        cursor.execute("DROP TABLE IF EXISTS weeks")

        cursor.execute("SELECT MIN(date) FROM scmlog")
        minDate = cursor.fetchone()[0]
        cursor.execute("SELECT MAX(date) FROM scmlog")
        maxDate = cursor.fetchone()[0]

        theWeeksTable = WeeksTable(db, cnn, repo)

        # The ISO year consists of 52 or 53 full weeks
        weeks_year_real = 52.1775
        weeks_year = int(weeks_year_real) + 1

        minDateWeek = minDate.date().isocalendar()[1]
        maxDateWeek = maxDate.date().isocalendar()[1]

        firstWeek = minDate.year * int(weeks_year) + minDateWeek
        lastWeek = maxDate.year * int(weeks_year) + maxDateWeek

        for period in range(firstWeek, lastWeek + 1):
            week = (period - 1) % weeks_year + 1
            year = (period - 1) // weeks_year
            # When used with the strptime() method, %U and %W are only used in
            # calculations when the day of the week and the year are specified.
            date_time = datetime.strptime(
                str(year) + " " + str(week) + " 0", "%Y %U %w"
            )
            if (date_time.year > year):
                continue
            date = date_time.strftime("%y-%m-%d")
            theWeeksTable.add_pending_row((period, year, week, date))
        theWeeksTable.insert_rows(write_cursor)
        cnn.commit()
        write_cursor.close()
        cursor.close()
        cnn.close()

# Register in the CVSAnalY extension system
register_extension("Weeks", Weeks)
