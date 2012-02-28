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
# It assumes the Metrics extension was already run, and the tables it
# generated are available

from pycvsanaly2.extensions import Extension, register_extension
from pycvsanaly2.utils import uri_to_filename
import datetime

class MetricsEvo (Extension):
    """Extension to calculate the metrics for files at different points in time.

    It assumes the Metrics extension was already run, and the tables it
    generates are available
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
        """Fill in the annual_metrics table.

        For each file in the repository, and for each year since the repository
        started, find the most recent metrics calculated for that file, but not
        older than the end of the year
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
        for year in range (minDate.year, maxDate.year + 1):
            for month in range (1, 13):
                limit = str(year) + "-" + str(month) + "-01"
                query = """
                  SELECT SUM(m.sloc), SUM(m.loc) 
                  FROM
                   (SELECT maxcommits.file_id, max_commit, type
                    FROM
                     (SELECT file_id, MAX(commit_id) max_commit
                      FROM 
                       (SELECT a.file_id, a.commit_id, a.type 
                        FROM actions a, scmlog s
                        WHERE a.commit_id = s.id AND 
                          a.branch_id=1 AND 
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
                cursor.execute (query % limit)
                (sloc, loc) = cursor.fetchone()
                print "*** Year: " + str(year) + "-" + str(month) + \
                    "-01: " + str (sloc) + \
                    ", " + str(loc)

        #cnn.commit ()
        write_cursor.close ()
        cursor.close ()
        cnn.close ()

register_extension ("MetricsEvo", MetricsEvo)
