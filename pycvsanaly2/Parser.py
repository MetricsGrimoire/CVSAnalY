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
import threading
from AsyncQueue import AsyncQueue, TimeOut

from repositoryhandler.backends.watchers import LOG

from ContentHandler import ContentHandler
from Config import Config
from utils import printerr, printout

class Parser:

    class SaveLog:
        CHUNK_SIZE = 1024
        
        def __init__ (self, filename):
            self.fd = open (filename, "w")
            self.buffer = ""

        def add_line (self, line):
            self.buffer += line
            if len (self.buffer) >= self.CHUNK_SIZE:
                self.fd.write (self.buffer)
                self.buffer = ""

        def close (self):
            if self.buffer:
                self.fd.write (self.buffer)
            self.fd.close ()
    
    def __init__ (self):
        self.handler = ContentHandler ()
        self.config = Config ()
        self.repo = None
        self.logfile = None
        self.uri = None

        self.n_line = 0

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

    def _logreader (self, repo, queue):
        def new_line (data, user_data = None):
            queue.put (data)

        repo.add_watch (LOG, new_line)
        repo.log (self.uri)
        
    def run (self):
        self.handler.begin ()

        save_log = None
        if self.config.save_logfile is not None:
            try:
                save_log = Parser.SaveLog (self.config.save_logfile)
            except Exception, e:
                printout ("Warning: error creating file %s for saving log file: %s",
                          (self.config.save_logfile, str (e)))
                save_log = None
        
        def new_line (data, user_data = None):
            if save_log is not None:
                save_log.add_line (data)
                
            self.n_line += 1
            self.parse_line (data.strip ('\n'))

        if self.repo is not None:
            self.handler.repository (self.repo.get_uri ())
            
        if self.logfile is not None:
            try:
                f = open (self.logfile, 'r')
            except IOError, e:
                printerr (str (e))
                return
            
            line = f.readline ()
            while line:
                new_line (line)
                line = f.readline ()

            f.close ()
        else:
            queue = AsyncQueue ()
            logreader_thread = threading.Thread (target=self._logreader,
                                                 args=(self.repo, queue))
            logreader_thread.setDaemon (True)
            logreader_thread.start ()

            # Use the queue with mutexes while the
            # thread is alive
            while logreader_thread.isAlive ():
                try:
                    line = queue.get (1)
                except TimeOut:
                    continue
                new_line (line)

            # No threads now, we don't need locks
            while not queue.empty_unlocked ():
                line = queue.get_unlocked ()
                new_line (line)

        if save_log is not None:
            save_log.close ()
            
        self.flush ()

        self.handler.end ()

if __name__ == '__main__':
    import sys
    import os
    from repositoryhandler.backends import create_repository, create_repository_from_path
    from ParserFactory import create_parser_from_logfile, create_parser_from_repository
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
                    print "(%s) on branch %s" % (action.f2.path, action.branch)
                else:
                    print "on branch %s" % (action.branch)
            print "Message"
            print commit.message

    if os.path.isfile (sys.argv[1]):
        # Parser from logfile
        p = create_parser_from_logfile (sys.argv[1])
    else:
        path = uri_to_filename (sys.argv[1])
        if path is not None:
            repo = create_repository_from_path (path)
        else:
            repo = create_repository ('svn', sys.argv[1])
        p = create_parser_from_repository (repo)
        p.set_uri (path or sys.argv[1])

    p.config.lines = False
    p.set_content_handler (StdoutContentHandler ())
    p.run ()

