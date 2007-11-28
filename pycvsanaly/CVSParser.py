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
#       Alvaro Navarro <anavarro@gsyc.escet.urjc.es>
#       Gregorio Robles <grex@gsyc.escet.urjc.es>
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import re
import datetime

from Parser import Parser
from Repository import *

class CVSParser (Parser):

    patterns = {}
    patterns['file'] = re.compile ("^RCS file: (.*)$")
    patterns['revision'] = re.compile ("^revision ([\d\.]*)$")
    patterns['info'] = re.compile ("^date: (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d):(\d\d):(\d\d)(.*);  author: (.*);  state: (.*);(  lines: \+(\d*) -(\d*\
))?")
    patterns['separator'] = re.compile ("^[=]+$")
    
    def __init__ (self):
        Parser.__init__ (self)

        # Parser context
        self.file = None
        self.commits = []

    def parse_line (self, line):
        if line is None or line == '':
            return

        # File separator
        if self.patterns['separator'].match (line):
            self.handler.file (self.file)
            for commit in self.commits:
                self.handler.commit (commit)

            self.commits = []
        
        # File 
        match = self.patterns['file'].match (line)
        if match:
            path = match.group (1)
            path = path[:path.rfind (',')]
            
            f = File ()
            f.path = path
            self.file = f

            return

        # Revision
        match = self.patterns['revision'].match (line)
        if match:
            commit = Commit ()
            # composed rev: revision + | + file path
            # to make sure revision is unique
            commit.composed_rev = True
            commit.revision = "%s|%s" % (match.group (1), self.file.path)
            self.commits.append (commit)

            return

        # Commit info (date, author, etc.)
        match = self.patterns['info'].match (line)
        if match:
            commit = self.commits[-1]
            commit.committer = match.group (8)
            self.handler.committer (commit.committer)
            
            commit.date = datetime.datetime (int (match.group (1)), int (match.group (2)), int (match.group (3)),
                                             int (match.group (4)), int (match.group (5)), int (match.group (6)))

            action = Action ()
            act = match.group (9)
            if act == 'dead':
                action.type = 'D'
            else:
                action.type = 'M'
            action.f1 = self.file
            # FIXME: is it possible to know when file was added? revision 1.1.1.1 or something?

            commit.actions.append (action)

            # FIXME: plus, minus
            # FIXME: do we really need intrunk, cvs_flag and external?, WTF are they?

            return

        # TODO: message commit
        
