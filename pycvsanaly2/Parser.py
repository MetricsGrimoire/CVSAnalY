# Copyright (C) 2006 Libresoft
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

from ContentHandler import ContentHandler


class Parser:
    CONTENT_ORDER = ContentHandler.ORDER_REVISION

    def __init__(self):
        self.handler = ContentHandler()
        self.repo_uri = None

        self.n_line = 0

    def set_content_handler(self, handler):
        self.handler = handler

    def set_repository(self, repo, uri):
        self.repo_uri = uri

    def flush(self):
        pass

    def _parse_line(self):
        raise NotImplementedError

    def feed(self, data):
        if self.n_line == 0:
            self.handler.begin(self.CONTENT_ORDER)

            if self.repo_uri is not None:
                self.handler.repository(self.repo_uri)

        for line in data.splitlines():
            self.n_line += 1
            self._parse_line(line)

    def end(self):
        if self.n_line <= 0:
            return
        self.flush()
        self.handler.end()


if __name__ == '__main__':
    import sys
    import os
    from repositoryhandler.backends import create_repository, create_repository_from_path
    from ParserFactory import create_parser_from_logfile, create_parser_from_repository
    from Log import LogReader
    from Repository import *
    from utils import *

    class StdoutContentHandler(ContentHandler):
        def commit(self, commit):
            print "Commit"
            print "rev: %s, committer: %s <%s>, date: %s" % (
                commit.revision, commit.committer.name, commit.committer.email, commit.date)
            if commit.author is not None:
                print "Author: %s <%s>" % (commit.author.name, commit.author.email)
            if commit.tags is not None:
                print "Tags: %s" % (str(commit.tags))
            print "files: ",
            for action in commit.actions:
                print "%s %s " % (action.type, action.f1),
                if action.f2 is not None:
                    print "(%s: %s) on branch %s" % (action.f2, action.rev, commit.branch or action.branch_f1)
                else:
                    print "on branch %s" % (commit.branch or action.branch_f1)
            print "Message"
            print commit.message

    def new_line(line, user_data=None):
        user_data.feed(line)

    reader = LogReader()

    if os.path.isfile(sys.argv[1]):
        # Parser from logfile
        p = create_parser_from_logfile(sys.argv[1])
        reader.set_logfile(sys.argv[1])
    else:
        path = uri_to_filename(sys.argv[1])
        if path is not None:
            repo = create_repository_from_path(path)
        else:
            repo = create_repository('svn', sys.argv[1])
            path = sys.argv[1]
        p = create_parser_from_repository(repo)
        reader.set_repo(repo, path)

    p.set_content_handler(StdoutContentHandler())
    reader.start(new_line, p)
    p.end()
