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

import os
import re
import time
import datetime

from subprocess import *
from FindProgram import find_program
from Parser import Parser
from Repository import *

class GitParser (Parser):

    patterns = {}
    patterns['commit'] = re.compile ("^commit[ \t]+(.*)$")
    patterns['author'] = re.compile ("^Author:[ \t]+(.*)[ \t]+<(.*)>$")
    patterns['committer'] = re.compile ("^Commit:[ \t]+(.*)[ \t]+<(.*)>$")
    patterns['date'] = re.compile ("^CommitDate: (.* [0-9]+ [0-9]+:[0-9]+:[0-9]+ [0-9][0-9][0-9][0-9]) ([+-][0-9][0-9][0-9][0-9])$")
    patterns['file'] = re.compile ("^([MAD])[ \t]+(.*)$")
    patterns['file-moved'] = re.compile ("^([RC])[0-9]+[ \t]+(.*)[ \t]+(.*)$")
    patterns['ignore'] = [re.compile ("^AuthorDate: .*$")]
    patterns['diffstat'] = re.compile ("^ \d+ files changed(, (\d+) insertions\(\+\))?(, (\d+) deletions\(\-\))?$")

    def __init__ (self):
        Parser.__init__ (self)

        self.git = None
        
        # Parser context
        self.commit = None

    def __get_added_removed_lines (self, revision):
        if self.git is None:
            self.git = find_program ('git')
            
        cmd = [self.git, 'show', '--shortstat', revision]
        env = os.environ.copy ().update ({'LC_ALL' : 'C'})
        pipe = Popen (cmd, shell=False, stdin=PIPE, stdout=PIPE, close_fds=True, env=env, cwd=self.uri)
        out = pipe.communicate ()[0]

        lines = out.split ('\n')
        lines.reverse ()
        for line in lines:
            m = self.patterns['diffstat'].match (line)
            if m is None:
                continue

            added = removed = 0
            if m.group (1) is not None:
                added = int (m.group (2))

            if m.group (3) is not None:
                removed = int (m.group (4))

            return (added, removed)
            
        return None        

    def flush (self):
        if self.commit is None:
            return
        
        self.handler.commit (self.commit)
        self.commit = None

    def parse_line (self, line):
        if line is None or line == '':
            return

        # Ignore
        for patt in self.patterns['ignore']:
            if patt.match (line):
                return
        
        # Commit
        match = self.patterns['commit'].match (line)
        if match:
            self.flush ()
            self.commit = Commit ()
            self.commit.revision = match.group (1)
            if self.config.lines:
                self.commit.lines = self.__get_added_removed_lines (self.commit.revision)

            return

        # Committer
        match = self.patterns['committer'].match (line)
        if match:
            self.commit.committer = match.group (1)
            self.handler.committer (self.commit.committer)

            return

        # Author
        match = self.patterns['author'].match (line)
        if match:
            self.commit.author = match.group (1)
            self.handler.author (self.commit.author)

            return

        # Date
        match = self.patterns['date'].match (line)
        if match:
            self.commit.date = datetime.datetime (* (time.strptime (match.group (1).strip (" "), "%a %b %d %H:%M:%S %Y")[0:6]))
            # datetime.datetime.strptime not supported by Python2.4
            #self.commit.date = datetime.datetime.strptime (match.group (1).strip (" "), "%a %b %d %H:%M:%S %Y")
            
            return

        # File
        match = self.patterns['file'].match (line)
        if match:
            f = File ()
            f.path = match.group (2)

            action = Action ()
            action.type = match.group (1)
            action.f1 = f

            self.commit.actions.append (action)
            self.handler.file (f)
        
            return

        # File moved/copied
        match = self.patterns['file-moved'].match (line)
        if match:
            f1 = File ()
            f1.path = match.group (3)

            f2 = File ()
            f2.path = match.group (2)

            action = Action ()
            type = match.group (1)
            if type == 'R':
                action.type = 'V'
            else:
                action.type = type
            action.f1 = f1
            action.f2 = f2

            self.commit.actions.append (action)
            self.handler.file (f1)

            return

        # Message
        self.commit.message += line + '\n'

        assert True, "Not match for line %s" % (line)
