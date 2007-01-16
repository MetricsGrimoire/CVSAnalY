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
# Authors : Alvaro Navarro <anavarro@gsyc.escet.urjc.es>

"""
Main funcion of cvsanaly. Fun starts here!

@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro@gsyc.escet.urjc.es
"""

import sys
import os
import time
import string
import stat
import getopt

import database as dbmodule
import repository as rpmodule
import plugins as plugmodule

from tables import *

# Some stuff about the project
author = "(C) 2004,2007 %s <%s>" % ("Libresoft", "cvsanaly@libresoft.es")
name = "cvsanaly %s - Libresoft Group http://www.libresoft.es" % ("1.0-BETA4")
credits = "\n%s \n%s\n" % (name,author)


def usage ():
    print credits
    print "Usage: %s [options]" % (sys.argv[0])
    print """
Run inside the checked out svn or cvs directory to analyze

Options:

  --help            Print this usage message.

  --type            Type of repository, cvs or svn (default is cvs)
  --branch          Branch to be analyzed (default is trunk)
  --revision        Start analysis from given revision
  --log-file        Parse a given log file instead of get it from repository
  --path            Set an alternative path for cvs/svn binary
  --driver          Output driver mysql or stdout (default is stdout)

Database:

  --user            Username for connect to database
  --password        Password for connect to database
  --database        Database which contains data previously analyzed
  --hostname        Name of the host with a database server running

Plugins:

  --scan            Scan for plugins
  --info            Retreives information from given plugin
  --with-plugin     Execute list of plugin
"""

def main():


    # Short (one letter) options. Those requiring argument followed by :
    #short_opts = "h:t:b:r:l:n:p:d:s:i:r"
    short_opts = ""
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = [ "help", "database=", "type=", "branch=", "revision=", "log-file=", "path=", "driver=", "scan", "info=", "run-plugins="]

    # Prefix directory. cvs/svn binaries should be installed under this path
    prefixpath = '/usr/bin/'

    # Default options
    user = ''
    passwd = ''
    hostname = ''
    database = 'cvsanaly'
    logfile = ''
    branch = ''
    revision = ''
    type = 'cvs'
    driver = 'stdout'
    directory = '.'

    p = plugmodule.Loader ()

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    for opt, value in opts:
        if opt in ("-h", "--help", "-help"):
            usage()
            sys.exit(0)
        elif opt in ("-l", "--log-file"):
            logfile = value
        elif opt in ("-t", "--type"):
            type = 'svn'
        elif opt in ("-b", "--database"):
            database = value
        elif opt in ("-r", "--repo-type"):
            type = value
        elif opt in ("-d", "--driver"):
            driver = value
        elif opt in ("-b", "--branch"):
            branch = value
        elif opt in ("-p", "--path"):
            binarypath = value
        elif opt in ("-s", "--scan"):
            p.scan ()
            sys.exit(0)
        elif opt in ("-i", "--info"):
            p.get_information (value)
            sys.exit(0)
        elif opt in ("-r", "--run-plugins"):
            print "not implemented"
        else:
            print ('Unknown option ', opt)
            usage()

    # Connect to the database
    conection = driver + "://" + user + ":" + passwd + "@" + hostname + "/" + database
    db = dbmodule.Database(conection)

    # CVS/SVN interactive
    repos = rpmodule.RepositoryFactory.create (type, directory)

    # Create database and tables
    db.create_database()
    db.create_table('files',files)
    db.create_table('commiters',commiters)
    db.create_table('log',log)
    db.create_table('modules', modules)
    db.create_table('commiters_module',commiters_module)

    # And finally we analyze log
    repos.log (db, directory, prefixpath, logfile)

    db.close()

