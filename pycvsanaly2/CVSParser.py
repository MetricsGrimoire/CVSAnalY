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
from ContentHandler import ContentHandler
from Repository import Commit, Action, Person


class CVSParser(Parser):
    CONTENT_ORDER = ContentHandler.ORDER_FILE

    patterns = {}
    patterns['file'] = re.compile("^RCS file: (.*)$")
    patterns['revision'] = re.compile("^revision ([\d\.]*)$")
    patterns['info'] = \
        re.compile(
            "^date: (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d):(\d\d):(\d\d)(.*);  author: (.*);  state: ([^;]*);(  lines: \+(\d+) -(\d+);?)?")
    patterns['branches'] = re.compile("^branches:  ([\d\.]*);$")
    patterns['branch'] = re.compile("^[ \b\t]+(.*): (([0-9]+\.)+)0\.([0-9]+)$")
    patterns['tag'] = re.compile("^[ \b\t]+(.*): (([0-9]+\.)+([0-9]+))$")
    patterns['rev-separator'] = re.compile("^[-]+$")
    patterns['file-separator'] = re.compile("^[=]+$")

    def __init__(self):
        Parser.__init__(self)

        self.root_path = ""
        self.lines = {}

        # Parser context
        self.file = None
        self.file_added_on_branch = None
        self.commit = None
        self.branches = None
        self.tags = None
        self.rev_separator = None
        self.file_separator = None

    def set_repository(self, repo, uri):
        Parser.set_repository(self, repo, uri)

        uri = repo.get_uri()
        s = uri.rfind(':')
        if s >= 0:
            self.root_path = uri[s + 1:]
        else:
            self.root_path = uri

    def _handle_commit(self):
        if self.commit is not None:
            # Remove trailing \n from commit message
            self.commit.message = self.commit.message[:-1]

            self.handler.commit(self.commit)
            self.commit = None

    def flush(self):
        self._handle_commit()
        if self.file is not None:
            self.handler.file(self.file)
            self.file_added_on_branch = None
            self.file = None

    def get_added_removed_lines(self):
        return self.lines

    def _parse_line(self, line):
        if not line:
            if self.commit is None:
                return

            if self.rev_separator is not None:
                self.rev_separator += '\n'
            elif self.file_separator is not None:
                self.file_separator += '\n'
            elif self.commit.message is not None:
                self.commit.message += '\n'

            return

        # Revision Separator
        if self.patterns['rev-separator'].match(line):
            # Ignore separators so that we don't
            # include it in the commit message
            if self.rev_separator is None:
                self.rev_separator = line
            else:
                self.rev_separator += line + '\n'

            return

        # File Separator
        if self.patterns['file-separator'].match(line):
            # Ignore separators so that we don't
            # include it in the commit message
            if self.file_separator is None:
                self.file_separator = line
            else:
                self.file_separator += line + '\n'

            return

            # File
        match = self.patterns['file'].match(line)
        if match:
            self.flush()

            path = match.group(1)
            path = path[len(self.root_path):]
            path = path[:path.rfind(',')]

            self.file = path

            self.branches = {}
            self.tags = {}
            self.commit = None
            self.file_separator = None

            return

        # Branch
        match = self.patterns['branch'].match(line)
        if match:
            self.branches[match.group(2) + match.group(4)] = match.group(1)

            return

        # Tag (Keep this always after Branch pattern)
        match = self.patterns['tag'].match(line)
        if match:
            revision = match.group(2)

            # We are ignoring 1.1.1.1 revisions,
            # so in case there's a tag pointing to that
            # revision we have to redirect it to 1.1 revision
            if revision == '1.1.1.1':
                revision = '1.1'

            self.tags.setdefault(revision, []).append(match.group(1))

            return

        # Revision
        match = self.patterns['revision'].match(line)
        if match and self.rev_separator is not None:
            self._handle_commit()

            revision = match.group(1)

            commit = Commit()
            # composed rev: revision + | + file path
            # to make sure revision is unique
            commit.composed_rev = True
            commit.revision = "%s|%s" % (revision, self.file)
            commit.tags = self.tags.get(revision, None)
            self.commit = commit

            self.rev_separator = None

            return

        # Commit info (date, author, etc.)
        match = self.patterns['info'].match(line)
        if match and self.commit is not None:
            commit = self.commit

            revision = commit.revision.split('|')[0]
            if revision == '1.1.1.1':
                self.commit = None
                return

            commit.committer = Person()
            commit.committer.name = match.group(8)
            self.handler.committer(commit.committer)

            commit.date = datetime.datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)),
                                            int(match.group(4)), int(match.group(5)), int(match.group(6)))

            if match.group(10) is not None:
                self.lines[commit.revision] = (int(match.group(11)), int(match.group(12)))
            else:
                self.lines[commit.revision] = (0, 0)

            action = Action()
            act = match.group(9)
            if act == 'dead':
                action.type = 'D'
                self.file = self.file.replace('/Attic', '')
                commit.revision = commit.revision.replace('/Attic', '')
            elif revision == '1.1':
                action.type = 'A'
            else:
                action.type = 'M'
            action.f1 = self.file

            # Branch
            try:
                last_dot = revision.rfind('.')
                prefix = revision[:last_dot]
                branch = self.branches[prefix]
                if self.file_added_on_branch and \
                        self.file_added_on_branch == prefix and \
                        revision[last_dot + 1:] == '1':
                    action.type = 'A'
                    self.file_added_on_branch = None

            except KeyError:
                branch = 'trunk'

            commit.branch = branch

            commit.actions.append(action)

            return

        # Branches
        match = self.patterns['branches'].match(line)
        if match:
            if self.commit is None:
                return

            action = self.commit.actions[0]
            revision = self.commit.revision.split('|')[0]
            if action.type == 'D' and revision == '1.1':
                # File added on a branch
                self.file_added_on_branch = match.group(1)

                # Discard this commit
                self.commit = None

            return

        # Message.
        if self.commit is not None:
            if self.rev_separator is not None:
                # Previous separator was probably a
                # false positive
                self.commit.message += self.rev_separator + '\n'
                self.rev_separator = None
            if self.file_separator is not None:
                # Previous separator was probably a
                # false positive
                self.commit.message += self.file_separator + '\n'
                self.file_separator = None
            self.commit.message += line + '\n'
