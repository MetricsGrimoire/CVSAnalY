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
from pycvsanaly.libcvsanaly.utils import Gnuplot

class Evolution (CVSAnalyPlugin):
    '''Creates evolution analysis graphs'''

    def __init__ (self, opts = []):
        CVSAnalyPlugin.__init__ (self)

    def __commits (self):
        gp = Gnuplot ()
        gp.set_terminal ('svg')
        gp.set_output ("/tmp/evolution/commits.svg")

        i = 0
        for intval in self.intval:
            gp.append_data ((i, self.ca.n_commits (intval)))
            i += 1
            
        gp.add_plot (1, 2)
        gp.plot ()

    def __commits_per_committer (self):
        commits = {}
        for intval in self.intval:
            for committer, n_commits in self.ca.n_commits_per_committer (intval):
                if not commits.has_key (committer):
                    commits[committer] = []
                commits[committer].append (n_commits)

        gp = Gnuplot ()
        gp.set_terminal ('svg')
        gp.set_output ("/tmp/evolution/commits_committer.svg")
        
        for committer in commits.keys ():
            gp2 = Gnuplot ()
            gp2.set_terminal ('svg')
            gp2.set_output ("/tmp/evolution/commits_committer-%s.svg" % (committer.encode ('utf-8')))
            i = 0
            for n_commits in commits[committer]:
                gp.append_data ((i, n_commits))
                gp2.append_data ((i, n_commits))
                i += 1
            gp.add_plot (1, 2, committer)
            gp2.add_plot (1, 2, committer)
            gp2.plot ()
            
        gp.plot ()
        
    def run (self, ca):
        self.ca = ca

        self.intval = self.ca.repository_interval_time ()

        self.__commits ()
        self.__commits_per_committer ()

register_plugin ('evolution', Evolution)
    
