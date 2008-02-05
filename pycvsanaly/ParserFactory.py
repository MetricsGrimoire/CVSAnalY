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

from repositoryhandler.backends import create_repository, create_repository_from_path

from CVSParser import CVSParser
from SVNParser import SVNParser
from GitParser import GitParser

def create_parser_from_logfile (uri):
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

    def log_file_is_git (logfile):
        retval = False

        try:
            f = open (logfile, 'r')
        except IOError, e:
            print e
            return False

        patt = re.compile ("^commit (.*)$")

        line = f.readline ()
        while line:
            if patt.match (line) is not None:
                retval = True
                break
            line = f.readline ()

        f.close ()

        return retval
    
    if os.path.isfile (uri):
        if logfile_is_svn (uri):
            p = SVNParser ()
        elif logfile_is_cvs (uri):
            p = CVSParser ()
        elif log_file_is_git (uri):
            p = GitParser ()

        assert p is not None
        
        p.set_logfile (uri)

        return p

    print "Error: path %s doesn't look like a valid log file" % (uri)
    return None

def create_parser_from_repository (repo):
    if repo.get_type () == 'cvs':
        p = CVSParser ()
    elif repo.get_type () == 'svn':
        p = SVNParser ()
    elif repo.get_type () == 'git':
        p = GitParser ()
    else:
        print "Error: Unsupported repository type: %s" % (repo.get_type ())
        return None

    p.set_repository (repo)

    return p
