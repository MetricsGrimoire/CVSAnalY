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

from pycvsanaly.plugins import get_plugin, scan_plugins

from tables import *

# Some stuff about the project
version = "1.0.1"
author = "(C) 2004,2007 %s <%s>" % ("Libresoft", "cvsanaly@libresoft.es")
name = "cvsanaly %s - Libresoft Group http://www.libresoft.es" % (version)
credits = "\n%s \n%s\n" % (name, author)

plugins = scan_plugins ()

def usage ():
    print credits
    print "Usage: cvsanaly [options]"
    print """
Run inside the checked out svn or cvs directory to analyze

Options:

  --help            Print this usage message.
  --version         Show version

  --branch          Branch to be analyzed (default is trunk)
  --log-file        Parse a given log file instead of get it from repository
  --repodir         Set the repository dir (default is '.')
  --driver          Output driver mysql or stdout (default is stdout)

Database:

  --user            Username for connect to database (default is operator)
  --password        Password for connect to database (default is operator)
  --database        Database which contains data previously analyzed (default is cvsanaly)
  --hostname        Name of the host with a database server running (default is localhost)

Plugins:

  --info            Retreives information from given plugin
  --run-plugin      Execute plugin
  --scan            Scan for plugins
"""

    for p in plugins:
        get_plugin (p).usage ()

def main():


    # Short (one letter) options. Those requiring argument followed by :
    short_opts = ""
    #short_opts = "h:t:b:r:l:n:p:d:s:i:r"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help","version","user=", "password=", "hostname=", "database=","branch=","log-file=","repodir=","driver=","info=","run-plugin=","scan"]

    for p in plugins:
        long_opts.extend (get_plugin (p).get_options ())

    # Default options
    user = 'operator'
    passwd = 'operator'
    hostname = 'localhost'
    database = 'cvsanaly'
    logfile = ''
    branch = ''
    driver = 'stdout'
    directory = '.'
    plugin = None
    plugin_opts = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        usage ()
        sys.exit(1)

    for opt, value in opts:
        if opt in ("-h", "--help", "-help"):
            usage()
            sys.exit(0)
        elif opt in ("--version"):
            print version
            sys.exit(0)
        elif opt in ("--username"):
            user = value
        elif opt in ("--password"):
            passwd = value
        elif opt in ("--hostname"):
            hostname = value
        elif opt in ("--log-file"):
            logfile = value
        elif opt in ("--database"):
            database = value
        elif opt in ("--driver"):
            driver = value
        elif opt in ("--branch"):
            branch = value
        elif opt in ("--repodir"):
            directory = value
        elif opt in ("--info"):
            p = get_plugin (value)
            p.info ()
            sys.exit(0)
        elif opt in ("--run-plugin"):
            plugin = value
        elif opt in ("--scan"):
            if len (plugins) == 0:
                print "No plugins available"
                sys.exit(0)

            for p in plugins:
                get_plugin (p).info ()
                print "--------------------"

            sys.exit(0)
        else:
            if plugin is not None:
                plugin_opts.append ((opt, value))

    # Connect to the database
    conection = driver + "://" + user + ":" + passwd + "@" + hostname + "/" + database
    db = dbmodule.Database(conection)

    if plugin is not None:
        # Run plugins if needed
        p = get_plugin (plugin, db, plugin_opts)
        p.run ()
    else:
        # CVS/SVN interactive
        repos = rpmodule.RepositoryFactory.create (directory)

        # Create database and tables
        db.create_database()
        db.create_table('files',files)
        db.create_table('commiters',commiters)
        db.create_table('log',log)
        db.create_table('modules', modules)

        # And finally we analyze log
        repos.log (db, directory, logfile)

    db.close()
