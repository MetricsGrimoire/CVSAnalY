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

from repositoryhandler.backends import create_repository, create_repository_from_path
from repositoryhandler.backends.watchers import *

from Repository import *
from utils import get_file_type

class ContentHandler:

    def __init__ (self):
        pass
    
    def commit (self, commit):
        pass

    def commiter (self, commiter):
        pass

    def file (self, file):
        pass

def create_parser (uri):
    def logfile_is_cvs (logfile):
        retval = False

        try:
            f = open (logfile, 'r')
        except IOError, e:
            print e
            return False
        
        patt = re.compile ("^RCS file:(.*)$")
        
        line = f.readline ()
        while line:
            if patt.match (line) is not None:
                retval = True
                break
            line = f.readline ()

        f.close ()

        return retval

    def logfile_is_svn (logfile):
        retval = False

        try:
            f = open (logfile, 'r')
        except IOError, e:
            print e
            return False

        patt = re.compile ("^r(.*) \| (.*) \| (.*) \| (.*)$")

        line = f.readline ()
        while line:
            if patt.match (line) is not None:
                retval = True
                break
            line = f.readline ()

        f.close ()

        return retval
    
    if os.path.isfile (uri):
        if logfile_is_cvs (uri):
            p = CVSParser ()
            p.set_logfile (uri)

            return p

        if logfile_is_svn (uri):
            p = SVNParser ()
            p.set_logfile (uri)

            return p
    
    match = re.compile ("^.*://.*$").match (uri)
    if match is None:
        # Local uri
        # FIXME: file:// is a local uri
        repo = create_repository_from_path (uri)
    else:
        # Remote uri (Only supported by SVN)
        repo = create_repository ('svn', uri)

    if repo.get_type () == 'cvs':
        p = CVSParser ()
    elif repo.get_type () == 'svn':
        p = SVNParser ()
    else:
        print "Error: Unsupported repository type: %s" % (repo.get_type ())
        return None

    p.set_uri (uri);
    p.set_repository (repo)

    return p

class Parser:

    def __init__ (self):
        self.handler = ContentHandler ()
        self.repo = None
        self.logfile = None
#        self.commits = []
#        self.commiters = []
#        self.files = []

    def set_content_handler (self, handler):
        self.handler = handler

    def set_uri (self, uri):
        self.uri = uri
        
    def set_logfile (self, logfile):
        self.repo = None
        self.logfile = logfile

    def set_repository (self, repo):
        self.logfile = None
        self.repo = repo

#    def get_commits (self):
#        return self.commits

#    def get_commiters (self):
#        return self.commiters

#    def get_files (self):
#        return self.files

    def parse_line (self):
        raise NotImplementedError

    def run (self):
        def new_line (data, user_data = None):
            self.parse_line (data.strip ('\n'))

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

class CVSParser (Parser):

    def __init__ (self):
        Parser.__init__ (self)

        self.patterns = {}
        self.patterns['file'] = re.compile ("^RCS file: (.*)$")
        self.patterns['revision'] = re.compile ("^revision ([\d\.]*)$")
        self.patterns['info'] = re.compile ("^date: (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d:\d\d:\d\d)(.*);  author: (.*);  state: (.*);(  lines: \+(\d*) -(\d*))?")
        self.patterns['separator'] = re.compile ("^[=]+$")

        # Parser context
        self.file = None
        self.commits = []

    def parse_line (self, line):
        if line is None or line == '':
            return

        # File separator
        if self.patterns['separator'].match (line):
            # TODO: LOCs
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
            f.type = get_file_type (f.path)
            self.file = f

            return

        # Revision
        match = self.patterns['revision'].match (line)
        if match:
            commit = Commit ()
            commit.revision = match.group (1)
            self.commits.append (commit)

            return

        # Commit info (date, author, etc.)
        match = self.patterns['info'].match (line)
        if match:
            commit = self.commits[-1]
            commit.commiter = match.group (6)
            self.handler.commiter (commit.commiter)
            commit.date = match.group (1) + "-" + match.group (2) + "-" + match.group (3) + " " + match.group (4)
            act = match.group (7)
            if act == 'dead':
                action = DELETE
            else:
                action = MODIFY
            # FIXME: is it possible to know when file was added? revision 1.1.1.1 or something?

            self.file.cdate = commit.date
            commit.files.append ((action, self.file))

            # FIXME: plus, minus
            # FIXME: do we really need intrunk, cvs_flag and external?, WTF are they?

            return
            
class SVNParser (Parser):

    (
        COMMIT,
        FILES,
        MESSAGE
    ) = range (3)
    
    def __init__ (self):
        Parser.__init__ (self)
        
        self.patterns = {}
        self.patterns['commit'] = re.compile ("^r(\d*) \| (.*) \| (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d:\d\d:\d\d) ([+-]\d\d\d\d) \(.*\) \| (.*) line")
        self.patterns['file'] = re.compile ("^[ ]+([MAD]) (.*)$")
        self.patterns['separator'] = re.compile ("^[-]+$")
        
        # Parser context
        self.state = SVNParser.COMMIT
        self.commit = None
        
    def parse_line (self, line):
        if line is None or line == '':
            return

        # Separator
        if self.patterns['separator'].match (line):
            if self.state == SVNParser.COMMIT:
                return
            elif self.state == SVNParser.MESSAGE:
                self.handler.commit (self.commit)
                self.state = SVNParser.COMMIT
            else:
                # FIXME: parser exception
                print "Error parsing svn log, unexpected separator"
                
            return

        # Commit
        match = self.patterns['commit'].match (line)
        if match and self.state == SVNParser.COMMIT:
            commit = Commit ()
            commit.revision = match.group (1)
            commit.commiter = match.group (2)
            commit.date = match.group (3) + "-" + match.group (4) + "-" + match.group (5) + " " + match.group (6)
            self.commit = commit
            #self.handler.commit (commit)
            self.handler.commiter (commit.commiter)
            #self.commits.append (commit)
            #self.commiters.append (commit.commiter)
            
            return
        elif match and self.state != SVNParser.COMMIT:
            # FIXME: parser exception
            print "Error parsing svn log, unexpected line %s" % (line)
            return

        # File
        match = self.patterns['file'].match (line)
        if match:
            f = File ()
            act = match.group (1)
            f.path = match.group (2)
            f.type = get_file_type (f.path)
            f.cdate = self.commit.date

            if act == 'A':
                action = ADD
            elif act == 'D':
                action = DELETE
            elif act == 'M':
                action = MODIFY
            
            self.commit.files.append ((action, f))
            #self.files.append (f)
            self.handler.file (f)
            
            if self.state == SVNParser.COMMIT:
                self.state = SVNParser.FILES
            elif self.state != SVNParser.FILES:
                # FIXME: parser exception
                print "Error parsing svn log, unexpected line %s" % (line)
                return

            return

        # Message or other lines
        if self.state == SVNParser.FILES or self.state == SVNParser.MESSAGE:
            self.state = SVNParser.MESSAGE
            self.commit.message += line + '\n'
            
if __name__ == '__main__':
    # CVS Parser
    #p = create_parser ('/home/carlos/src/gnome/svn/poppler/')
    #p.run ()

    class StdoutContentHandler (ContentHandler):
        def commit (self, commit):
            print "Commit"
            print "rev: %s, commiter: %s, date: %s" % (commit.revision, commit.commiter, commit.date)
            print "files: ",
            for action, file in commit.files:
                print file.path
            print "Message"
            print commit.message

    # CVS Parser from log file
    p = create_parser ('/home/carlos/tmp/poppler.log')
    handler = StdoutContentHandler ()
    p.set_content_handler (handler)
    p.run ()

    # SVN Parser
#    p = create_parser ('.')
#    handler = StdoutContentHandler ()
#    p.set_content_handler (handler)
#    p.run ()
    
    # SVN Parser from logfile
#    p = create_parser ('/home/carlos/tmp/cvsanaly.log')
#    handler = StdoutContentHandler ()
#    p.set_content_handler (handler)
#    p.run ()

#    # SVN PArser from URI
#    p = create_parser ('http://svn.gnome.org/svn/gnome-common')
#    p.run ()
