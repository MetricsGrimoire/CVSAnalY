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

import os
import re
import datetime

import repositoryhandler
from repositoryhandler.backends.watchers import DIFF
from subprocess import Popen, PIPE

from FindProgram import find_program

from Parser import Parser
from Repository import Commit, Action, File
from utils import printout, printdbg

class SVNParser (Parser):

    (
        COMMIT,
        FILES,
        MESSAGE
    ) = range (3)

    patterns = {}
    patterns['commit'] = re.compile ("^r(\d*) \| (.*) \| (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d):(\d\d):(\d\d) ([+-]\d\d\d\d) \(.*\) \| (.*) line")
    patterns['file'] = re.compile ("^[ ]+([MADR]) (.*)$")
    patterns['file-moved'] = re.compile ("^[ ]+([MADR]) (.*) \(from (.*):([0-9]+)\)$")
    patterns['separator'] = re.compile ("^[-]+$")
    patterns['diffstat'] = re.compile ("^ \d+ files changed(, (\d+) insertions\(\+\))?(, (\d+) deletions\(\-\))?$")
    
    def __init__ (self):
        Parser.__init__ (self)

        self.diffstat = None
        
        # Parser context
        self.state = SVNParser.COMMIT
        self.commit = None

    def __get_added_removed_lines (self, revision):
        global _diff

        if self.diffstat is None:
            self.diffstat = find_program ('diffstat')

        _diff = ""
        def diff_line (data, user_data):
            global _diff
            _diff += data

        revs = []
        revs.append ("%d" % (revision - 1))
        revs.append ("%d" % (revision))
        env = os.environ.copy ().update ({'LC_ALL' : 'C'})
        pipe = Popen (self.diffstat, shell=False, stdin=PIPE, stdout=PIPE, close_fds=True, env=env)
        wid = self.repo.add_watch (DIFF, diff_line)
        try:
            self.repo.diff (self.repo.get_uri (), revs = revs)
        except repositoryhandler.Command.CommandError, e:
            printerr ("Error running svn diff command: %s", (str (e)))
            self.repo.remove_watch (DIFF, wid)
            return None

        out = pipe.communicate (_diff)[0]
        self.repo.remove_watch (DIFF, wid)

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

    def __convert_commit_actions (self, commit):
        # We detect here files that have been moved or
        # copied. Files moved are converted into a
        # single action of type 'V'. For copied files
        # we just change its actions type from 'A' to 'C'

        def find_action (actions, type, path):
            for action in actions:
                if action.type == type and action.f1.path == path:
                    return action
            
            return None

        remove_actions = []
        
        for action in commit.actions:
            if action.f2 is not None:
                # Move or copy action
                if action.type == 'A':
                    del_action = find_action (commit.actions, 'D', action.f2.path)
                    if del_action is not None and del_action not in remove_actions:
                        # FIXME: See http://research.libresoft.es/cgi-bin/trac.cgi/wiki/Tools/CvsanalyRevamped#Filesmovedandcopiedinthesamerevision
                        printdbg ("SVN Parser: File %s has been renamed to %s", (action.f2.path, action.f1.path))
                        action.type = 'V'
                        remove_actions.append (del_action)
                    else:
                        action.type = 'C'
                        printdbg ("SVN Parser: File %s has been copied to %s", (action.f2.path, action.f1.path))
                elif action.type == 'R':
                    # TODO
                    printdbg ("SVN Parser: File %s replaced to %s", (action.f2.path, action.f1.path))
                    pass

        for action in remove_actions:
            printdbg ("SVN Parser: Removing action %s %s", (action.type, action.f1.path))
            commit.actions.remove (action)
        
    def parse_line (self, line):
        if line is None or line == '':
            return
        
        # Separator
        if self.patterns['separator'].match (line):
            if self.state == SVNParser.COMMIT:
                return
            elif self.state == SVNParser.MESSAGE or self.state == SVNParser.FILES:
                # We can go directly from FILES to COMMIT
                # when there is an empty log message
                self.__convert_commit_actions (self.commit)
                self.handler.commit (self.commit)
                self.state = SVNParser.COMMIT
            else:
                printout ("Warning (%d): parsing svn log, unexpected separator", (self.n_line))
                
            return

        # Commit
        match = self.patterns['commit'].match (line)
        if match and self.state == SVNParser.COMMIT:
            commit = Commit ()
            commit.revision = match.group (1)
            commit.committer = match.group (2)
            commit.date = datetime.datetime (int (match.group (3)), int (match.group (4)), int (match.group (5)),
                                             int (match.group (6)), int (match.group (7)), int (match.group (8)))
            if self.config.lines:
                commit.lines = self.__get_added_removed_lines (int (commit.revision))
                
            self.commit = commit
            self.handler.committer (commit.committer)
            
            return
        elif match and self.state != SVNParser.COMMIT:
            printout ("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))
            return

        # File moved/copied/replaced
        match = self.patterns['file-moved'].match (line)
        if match:
            f1 = File ()
            f1.path = match.group (2)

            f2 = File ()
            f2.path = match.group (3)
            
            action = Action ()
            action.type = match.group (1)
            action.f1 = f1
            action.f2 = f2

            self.commit.actions.append (action)
            self.handler.file (f1)

            if self.state == SVNParser.COMMIT:
                self.state = SVNParser.FILES
            elif self.state != SVNParser.FILES:
                printout ("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))
                return

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
            
            if self.state == SVNParser.COMMIT:
                self.state = SVNParser.FILES
            elif self.state != SVNParser.FILES:
                printout ("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))
                return

            return
        
        # Message or other lines
        if self.state == SVNParser.FILES or self.state == SVNParser.MESSAGE:
            self.state = SVNParser.MESSAGE
            self.commit.message += line + '\n'
