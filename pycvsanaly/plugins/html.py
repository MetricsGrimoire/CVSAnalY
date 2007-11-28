# Copyright (C) 2007 LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from pycvsanaly.plugins import CVSAnalyPlugin, register_plugin


class SimpleHTML (CVSAnalyPlugin):
    '''Create a simple HTML report'''

    def __init__ (self, opts = []):
        CVSAnalyPlugin.__init__ (self)

    def __committers_commits (self):
        retval = "<table border=\"0\">\n"

        committers = self.ca.n_commits_per_committer ()
        n_commits = self.ca.n_commits ()
        i = 1
        for committer, commits in committers:
            perc = (commits * 100) / float (n_commits)

            retval += "<tr>\n"
            retval += "\t<td>%d</td>\n" % (i)
            retval += "\t<td>%s</td>\n" % (committer)
            retval += "\t<td>%d</td>\n" % (commits)
            retval += "\t<td>%.2f</td>\n" % (perc)
            retval += "</tr>\n"

            i += 1

        retval += "</table>\n"

        return retval

    def __committers_paths (self):
        retval = "<table border=\"0\">\n"

        committers = self.ca.n_paths_per_committer ()
        n_paths = self.ca.n_paths (True)
        i = 1
        for committer, paths in committers:
            perc = (paths * 100) / float (n_paths)

            retval += "<tr>\n"
            retval += "\t<td>%d</td>\n" % (i)
            retval += "\t<td>%s</td>\n" % (committer)
            retval += "\t<td>%d</td>\n" % (paths)
            retval += "\t<td>%.2f</td>\n" % (perc)
            retval += "</tr>\n"
            
            i += 1

        retval += "</table>\n"

        return retval
        
        
    def run (self, ca):
        self.ca = ca
        
        self.out = open ("./index.html", "w")

        table = self.__committers_commits ()
        self.out.write (table.encode ('utf-8'))

        table = self.__committers_paths ()
        self.out.write (table.encode ('utf-8'))

        self.out.close ()

register_plugin ('html', SimpleHTML)
