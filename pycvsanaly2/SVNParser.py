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
#       Alvaro Navarro <anavarro@gsyc.escet.urjc.es>
#       Gregorio Robles <grex@gsyc.escet.urjc.es>
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import re
import datetime

from Parser import Parser
from Repository import Commit, Action, Person
from utils import printout, printdbg


class SVNParser(Parser):
    (
        COMMIT,
        FILES,
        MESSAGE
    ) = range(3)

    patterns = {}
    patterns['commit'] = re.compile(
        "^r(\d*) \| (.*) \| (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d):(\d\d):(\d\d) ([+-]\d\d\d\d) \(.*\) \| (.*) line")
    patterns['paths'] = re.compile("^Changed paths:$")
    patterns['file'] = re.compile("^[ ]+([MADR]) (.*)$")
    patterns['file-moved'] = re.compile("^[ ]+([MADR]) (.*) \(from (.*):([0-9]+)\)$")
    patterns['separator'] = re.compile("^------------------------------------------------------------------------$")
    patterns['invalid'] = re.compile("^r(\d*) \| \(no author\) \| \(no date\) \| 1 line$")

    def __init__(self):
        Parser.__init__(self)

        self.root_path = ''

        # Parser context
        self.state = SVNParser.COMMIT
        self.commit = None
        self.msg_lines = 0

    def set_repository(self, repo, uri):
        Parser.set_repository(self, repo, uri)

        self.root_path = uri.replace(repo.get_uri(), '')

    def __convert_commit_actions(self, commit):
        # We detect here files that have been moved or
        # copied. Files moved are converted into a
        # single action of type 'V'. For copied files
        # we just change its actions type from 'A' to 'C'

        def find_action(actions, type, path):
            for action in actions:
                if action.type == type and action.f1 == path:
                    return action

            return None

        remove_actions = []

        for action in commit.actions:
            if action.f2 is not None:
                # Move or copy action
                if action.type == 'A':
                    del_action = find_action(commit.actions, 'D', action.f2)
                    if del_action is not None and del_action not in remove_actions:
                        # FIXME: See http://research.libresoft.es/cgi-bin/trac.cgi/wiki/Tools/CvsanalyRevamped#Filesmovedandcopiedinthesamerevision
                        printdbg("SVN Parser: File %s has been renamed to %s", (action.f2, action.f1))
                        action.type = 'V'
                        remove_actions.append(del_action)
                    else:
                        action.type = 'C'
                        printdbg("SVN Parser: File %s has been copied to %s", (action.f2, action.f1))

                        # Try to guess if it was a tag
                        # Yes, with svn we are always guessing :-/
                        tag = self.__guess_tag_from_path(action.f1)
                        if tag is not None:
                            if commit.tags is None:
                                commit.tags = []

                            commit.tags.append(tag)

                elif action.type == 'R':
                    # TODO
                    printdbg("SVN Parser: File %s replaced to %s", (action.f2, action.f1))
                    pass

        for action in remove_actions:
            printdbg("SVN Parser: Removing action %s %s", (action.type, action.f1))
            commit.actions.remove(action)

    def __guess_branch_from_path(self, path):
        path = path[len(self.root_path):]

        if path.startswith("/branches"):
            try:
                branch = path.split('/')[2]
            except:
                branch = 'trunk'
        else:
            branch = 'trunk'

        return branch

    def __guess_tag_from_path(self, path):
        path = path[len(self.root_path):]

        if not path.startswith("/tags"):
            return None

        try:
            tag = path.split('/')[2]
        except:
            return None

        return tag

    def __append_message_line(self, line=None):
        if self.msg_lines <= 0:
            printout("Warning (%d): parsing svn log, unexpected line in message: %s", (self.n_line, line))
            self.msg_lines = 0
            return

        if line is not None:
            self.commit.message += line

        self.commit.message += '\n'
        self.msg_lines -= 1

    def _parse_line(self, line):
        if not line:
            if self.commit is not None and self.state == SVNParser.COMMIT or self.state == SVNParser.FILES:
                self.state = SVNParser.MESSAGE
            elif self.state == SVNParser.MESSAGE:
                self.__append_message_line()

            return

        # Message
        if self.state == SVNParser.MESSAGE and self.msg_lines > 0:
            self.__append_message_line(line)

            return

        # Invalid commit. Some svn repos like asterisk have commits like this:
        # r176840 | (no author) | (no date) | 1 line
        # without any canged path, so I think we can just ignore them
        if self.patterns['invalid'].match(line):
            printdbg("SVN Parser: skipping invalid commit: %s", (line,))
            self.state = SVNParser.COMMIT
            self.commit = None
            return

        # Separator
        if self.patterns['separator'].match(line):
            if self.commit is None or self.state == SVNParser.COMMIT:
                return
            elif self.state == SVNParser.MESSAGE or self.state == SVNParser.FILES:
                # We can go directly from FILES to COMMIT
                # when there is an empty log message
                if self.msg_lines > 0:
                    printout("Warning (%d): parsing svn log, missing lines in commit message!", (self.n_line,))

                self.__convert_commit_actions(self.commit)
                self.handler.commit(self.commit)
                self.state = SVNParser.COMMIT
                self.commit = None
                self.msg_lines = 0
            else:
                printout("Warning (%d): parsing svn log, unexpected separator", (self.n_line,))

            return

        # Commit
        match = self.patterns['commit'].match(line)
        if match and self.state == SVNParser.COMMIT:
            commit = Commit()
            commit.revision = match.group(1)

            commit.committer = Person()
            commit.committer.name = match.group(2)

            commit.date = datetime.datetime(int(match.group(3)), int(match.group(4)), int(match.group(5)),
                                            int(match.group(6)), int(match.group(7)), int(match.group(8)))
            self.msg_lines = int(match.group(10))
            self.commit = commit
            self.handler.committer(commit.committer)

            return
        elif match and self.state == SVNParser.MESSAGE:
            # It seems a piece of a log message has been copied as
            # part of the commit message
            self.commit.message += line + '\n'
            return
        elif match and self.state != SVNParser.COMMIT:
            printout("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))
            return

        # Files
        if self.state == SVNParser.COMMIT:
            if self.patterns['paths'].match(line):
                self.state = SVNParser.FILES
            else:
                printout("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))

            return

        # File moved/copied/replaced
        match = self.patterns['file-moved'].match(line)
        if match:
            if self.state != SVNParser.FILES:
                printout("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))
                return

            action = Action()
            action.type = match.group(1)
            action.f1 = match.group(2)
            action.f2 = match.group(3)
            action.rev = match.group(4)

            action.branch_f1 = self.__guess_branch_from_path(action.f1)
            action.branch_f2 = self.__guess_branch_from_path(action.f2)

            self.commit.actions.append(action)
            self.handler.file(action.f1)

            return

        # File
        match = self.patterns['file'].match(line)
        if match:
            if self.state != SVNParser.FILES:
                printout("Warning (%d): parsing svn log, unexpected line %s", (self.n_line, line))
                return

            path = match.group(2)

            if path != '/':
                # path == '/' is probably a properties change in /
                # not interesting for us, ignoring

                action = Action()
                action.type = match.group(1)
                action.f1 = path

                action.branch_f1 = self.__guess_branch_from_path(path)

                self.commit.actions.append(action)
                self.handler.file(path)

            return
