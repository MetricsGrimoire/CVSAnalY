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

from Parser import Parser
from Repository import Commit, Action, Person

class GitParser (Parser):

    class GitCommit:

        def __init__ (self, commit, parents):
            self.commit = commit
            self.parents = parents

        def is_my_child (self, git_commit):
            return git_commit.parents and self.commit.revision in git_commit.parents
    
    patterns = {}
    patterns['commit'] = re.compile ("^commit[ \t]+([^ ]+)( ([^\(]+))?( \((.*)\))?$")
    patterns['author'] = re.compile ("^Author:[ \t]+(.*)[ \t]+<(.*)>$")
    patterns['committer'] = re.compile ("^Commit:[ \t]+(.*)[ \t]+<(.*)>$")
    patterns['date'] = re.compile ("^CommitDate: (.* [0-9]+ [0-9]+:[0-9]+:[0-9]+ [0-9][0-9][0-9][0-9]) ([+-][0-9][0-9][0-9][0-9])$")
    patterns['file'] = re.compile ("^([MAD])[ \t]+(.*)$")
    patterns['file-moved'] = re.compile ("^([RC])[0-9]+[ \t]+(.*)[ \t]+(.*)$")
    patterns['branch'] = re.compile ("refs/remotes/origin/([^,]*)")
    patterns['local-branch'] = re.compile ("refs/heads/([^,]*)")
    patterns['tag'] = re.compile ("tag: refs/tags/([^,]*)")
    patterns['stash'] = re.compile ("refs/stash")
    patterns['ignore'] = [re.compile ("^AuthorDate: .*$"), re.compile ("^Merge: .*$")]

    def __init__ (self):
        Parser.__init__ (self)

        # Parser context
        self.commit = None
        self.branch_stack = None
        self.branches = []

    def flush (self):
        if self.branches:
            self._unpack_branch_stack ()

    def _unpack_branch_stack (self):
        branch, stack = self.branches.pop (0)
        # Ignore local and stash branches
        if branch[1] != "remote":
            return
        
        for commit in stack:
            commit.commit.branch = branch[0]
            self.handler.commit (commit.commit)

    def _parse_line (self, line):
        if line is None or line == '':
            return

        # Ignore
        for patt in self.patterns['ignore']:
            if patt.match (line):
                return
        
        # Commit
        match = self.patterns['commit'].match (line)
        if match:
            self.commit = Commit ()
            self.commit.revision = match.group (1)

            parents = match.group (3)
            if parents:
                parents = parents.split ()
            git_commit = self.GitCommit (self.commit, parents)
            
            decorate = match.group (5)
            branch = None
            if decorate:
                # Remote branch
                m = re.search (self.patterns['branch'], decorate)
                if m:
                    branch = (m.group (1), "remote")
                else:
                    # Local Branch
                    m = re.search (self.patterns['local-branch'], decorate)
                    if m:
                        branch = (m.group (1), "local")
                        # If local branch was merged we just ignore this decoration
                        if self.branch_stack and git_commit.is_my_child (self.branch_stack[-1]):
                            branch = None
                    else:
                        # Stash
                        m = re.search (self.patterns['stash'], decorate)
                        if m:
                            branch = ("stash", "stash")
                # Tag
                m = re.search (self.patterns['tag'], decorate)
                if m:
                    self.commit.tags = [m.group (1)]

            if len (self.branches) >= 2:
                # If current commit is the start point of a new branch
                # we have to look at all the current branches since
                # we haven't inserted the new branch yet.
                # If not, look at all other branches excluding the current one
                if branch is not None:
                    branches = [b for b in self.branches]
                else:
                    branches = self.branches[1:]

                for b, stack in branches:
                    if git_commit.is_my_child (stack[-1]):
                        self._unpack_branch_stack ()
                        self.branch_stack = stack

            if branch is not None:
                self.branch_stack = []
                # Insert master always at the end
                if branch == ('master', 'remote'):
                    self.branches.append ((branch, self.branch_stack))
                else:
                    self.branches.insert (0, (branch, self.branch_stack))
            self.branch_stack.append (git_commit)

            return

        # Committer
        match = self.patterns['committer'].match (line)
        if match:
            self.commit.committer = Person ()
            self.commit.committer.name = match.group (1)
            self.commit.committer.email = match.group (2)
            self.handler.committer (self.commit.committer)

            return

        # Author
        match = self.patterns['author'].match (line)
        if match:
            self.commit.author = Person ()
            self.commit.author.name = match.group (1)
            self.commit.author.email = match.group (2)
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
            action = Action ()
            action.type = match.group (1)
            action.f1 = match.group (2)

            self.commit.actions.append (action)
            self.handler.file (action.f1)
        
            return

        # File moved/copied
        match = self.patterns['file-moved'].match (line)
        if match:
            action = Action ()
            type = match.group (1)
            if type == 'R':
                action.type = 'V'
            else:
                action.type = type
            action.f1 = match.group (3)
            action.f2 = match.group (2)
            action.rev = self.commit.revision

            self.commit.actions.append (action)
            self.handler.file (action.f1)

            return

        # Message
        self.commit.message += line + '\n'

        assert True, "Not match for line %s" % (line)
