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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import re
import time
import datetime

from Parser import Parser
from Repository import Commit, Action, Person

# TODO: Add debug messages
#       Branches stuff


class BzrParser(Parser):
    (
        UNKNOWN,
        COMMIT,
        MESSAGE,
        ADDED,
        MODIFIED,
        REMOVED,
        RENAMED
    ) = range(7)

    patterns = {}
    patterns['commit'] = re.compile("^revno:[ \t]+(.*)$")
    patterns['committer'] = re.compile("^committer:[ \t]+(.*)[ \t]+<(.*)>$")
    patterns['author'] = re.compile("^author:[ \t]+(.*)[ \t]+<(.*)>$")
    patterns['date'] = re.compile(
        "^timestamp:.* ([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9]+:[0-9]+:[0-9]+) ([+-][0-9][0-9][0-9][0-9])$")
    patterns['message'] = re.compile("^message:$")
    patterns['added'] = re.compile("^added:$")
    patterns['modified'] = re.compile("^modified:$")
    patterns['removed'] = re.compile("^removed:$")
    patterns['renamed'] = re.compile("^renamed:$")
    patterns['separator'] = re.compile("^-+$")
    patterns['ignore'] = re.compile("^[ \t]+-+$")

    def __init__(self):
        Parser.__init__(self)

        # Parser context
        self.state = BzrParser.COMMIT
        self.commit = None

    def flush(self):
        if self.commit is None:
            return

        self.handler.commit(self.commit)
        self.commit = None
        self.state = BzrParser.COMMIT

    def _parse_line(self, line):
        if line is None or line == '':
            return

        # Separator
        match = self.patterns['separator'].match(line)
        if match:
            self.flush()

            return

        # Ignore details about merges
        match = self.patterns['ignore'].match(line)
        if match:
            self.state = BzrParser.UNKNOWN

            return

        # Commit
        match = self.patterns['commit'].match(line)
        if match:
            self.flush()
            self.commit = Commit()
            self.commit.revision = match.group(1)

            self.state = BzrParser.COMMIT

            return

        # Committer
        match = self.patterns['committer'].match(line)
        if match:
            self.commit.committer = Person()
            self.commit.committer.name = match.group(1)
            self.commit.committer.email = match.group(2)
            self.handler.committer(self.commit.committer)

            return

        # Author
        match = self.patterns['author'].match(line)
        if match:
            self.commit.author = Person()
            self.commit.author.name = match.group(1)
            self.commit.author.email = match.group(2)
            self.handler.author(self.commit.author)

            return

            # Date
        match = self.patterns['date'].match(line)
        if match:
            self.commit.date = datetime.datetime(*(time.strptime(match.group(1).strip(" "), "%Y-%m-%d %H:%M:%S")[0:6]))
            # datetime.datetime.strptime not supported by Python2.4
            #self.commit.date = datetime.datetime.strptime (match.group (1).strip (" "), "%a %b %d %H:%M:%S %Y")

            return

        # Message
        match = self.patterns['message'].match(line)
        if match:
            self.state = BzrParser.MESSAGE

            return

        # Added files
        match = self.patterns['added'].match(line)
        if match:
            self.state = BzrParser.ADDED

            return

        # Modified files
        match = self.patterns['modified'].match(line)
        if match:
            self.state = BzrParser.MODIFIED

            return

        # Removed files
        match = self.patterns['removed'].match(line)
        if match:
            self.state = BzrParser.REMOVED

            return

        # Renamed files
        match = self.patterns['renamed'].match(line)
        if match:
            self.state = BzrParser.RENAMED

            return

        if self.state == BzrParser.MESSAGE:
            self.commit.message += line.lstrip() + '\n'
        elif self.state == BzrParser.ADDED or \
                self.state == BzrParser.MODIFIED or \
                self.state == BzrParser.REMOVED:
            action = Action()
            if self.state == BzrParser.ADDED:
                action.type = 'A'
            elif self.state == BzrParser.MODIFIED:
                action.type = 'M'
            elif self.state == BzrParser.REMOVED:
                action.type = 'D'
            action.f1 = line.strip()

            self.commit.actions.append(action)
            self.handler.file(action.f1)
        elif self.state == BzrParser.RENAMED:
            m = re.compile("^[ \t]+(.*) => (.*)$").match(line)
            if not m:
                return

            action = Action()
            action.type = 'V'
            action.f1 = m.group(2)
            action.f2 = m.group(1)

            self.commit.actions.append(action)
            self.handler.file(action.f1)
        else:
            self.state = BzrParser.UNKNOWN
