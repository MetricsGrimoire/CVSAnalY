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

from repositoryhandler.backends.watchers import *

from ContentHandler import ContentHandler
from Config import Config

class Parser:

    def __init__ (self):
        self.handler = ContentHandler ()
        self.config = Config ()
        self.repo = None
        self.logfile = None
        self.uri = None

    def set_content_handler (self, handler):
        self.handler = handler

    def set_uri (self, uri):
        self.uri = uri
        
    def set_logfile (self, logfile):
        self.logfile = logfile

    def set_repository (self, repo):
        self.repo = repo

    def flush (self):
        pass
        
    def parse_line (self):
        raise NotImplementedError

    def run (self):
        self.handler.begin ()
        
        def new_line (data, user_data = None):
            self.parse_line (data.strip ('\n'))

        if self.repo is not None:
            self.handler.repository (self.repo.get_uri ())
            
        if self.logfile is not None:
            try:
                f = open (self.logfile, 'r')
            except IOError, e:
                print e
                return
            line = f.readline ()
            while line:
                new_line (line)
                line = f.readline ()

            f.close ()
        else:
            self.repo.add_watch (LOG, new_line)
            self.repo.log (self.uri)

        self.flush ()

        self.handler.end ()

if __name__ == '__main__':
    import sys
    from ParserFactory import create_parser_from_logfile
    from Repository import *
    from utils import *
    
    class StdoutContentHandler (ContentHandler):
        def commit (self, commit):
            print "Commit"
            print "rev: %s, committer: %s, date: %s" % (commit.revision, commit.committer, commit.date)
            if commit.author is not None:
                print "Author: %s" % (commit.author)
            if commit.lines is not None:
                print "Lines: %d+, %d-" % (commit.lines[0], commit.lines[1])
            print "files: ",
            for action in commit.actions:
                print "%s %s " % (action.type, action.f1.path),
                if action.f2 is not None:
                    print "(%s)" % (action.f2.path)
                else:
                    print 
            print "Message"
            print commit.message

    # SVN Parser from logfile
    p = create_parser_from_logfile (sys.argv[1])
    p.set_content_handler (StdoutContentHandler ())
    p.run ()

