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

from Parser import create_parser
from ContentHandlers import DBContentHandler

from tables import *

# Some stuff about the project
version = "1.0.1"
author = "(C) 2004,2007 %s <%s>" % ("Libresoft", "cvsanaly@libresoft.es")
name = "cvsanaly %s - Libresoft Group http://www.libresoft.es" % (version)
credits = "\n%s \n%s\n" % (name, author)

plugins = scan_plugins ()

def usage ():
    print credits
    print "Usage: cvsanaly [options] [URI1] [URI2] ... [URIn]"
    print """
Analyze the given set of URIs. An URI can be a checked out directory, 
a remote URL pointing to a repository or a repository log file. If 
URIs are omitted, the current working directory will be used as a 
checked out directory.

Options:

  -h, --help         Print this usage message.
  -V, --version      Show version

  -b, --branch       Repository branch to analyze (default is head/trunk)
  -l, --module-level The level of the source tree at which a directory is
                     considered as a module by cvsanaly. -1 means every
                     directory will be considered as a module (default is 0)

Database:

      --db-driver    Output database driver [stdout|mysql] (default is stdout)
  -u, --db-user      Database user name (default is operator)
  -p, --db-password  Database user password (default is operator)
  -d, --db-database  Database name (default is cvsanaly)
  -H, --db-hostname  Name of the host where database server is running (default is localhost)

Plugins:

  --plugin-info      Retreives information from given plugin
  --plugin-run       Execute plugin
  --plugin-scan      Scan for plugins
"""

    for p in plugins:
        get_plugin (p).usage ()

_database_created = False
def create_database (db):
    global _database_created
    if _database_created:
        return

    # Create database and tables
    db.create_database ()
    db.create_table ('files', files)
    db.create_table ('commiters', commiters)
    db.create_table ('log', log)
    db.create_table ('modules', modules)

    _database_created = True

def run (db, args, level = None):
    for uri in args:
        p = create_parser (uri)
        if p is None:
            continue
        
        create_database (db)
        print "Parsing log for %s" % (uri)
        handler = DBContentHandler (db)
        p.set_content_handler (handler)
        p.run ()

        #repo = rpmodule.RepositoryFactory.create (uri)
        #if repo is None:
        #    continue

#        print "Filling database for %s" % (uri)
#        create_database (db)
        #if level is not None:
        #    repo.set_level (level)
        #repo.log (db, p)

def main():
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hVb:l:u:p:d:H:"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help","version","branch=","module-level=""db-user=", "db-password=", "db-hostname=", "db-database=","db-driver=","plugin-info=","plugin-run=","plugin-scan"]
    # Deprecated options, added only for backward compatibility
    long_opts.extend (("user=", "password=", "hostname=", "database=", "driver=", "run-plugin=", "scan", "info="))

    for p in plugins:
        long_opts.extend (get_plugin (p).get_options ())

    # Default options
    user = 'operator'
    passwd = 'operator'
    hostname = 'localhost'
    database = 'cvsanaly'
    branch = ''
    driver = 'stdout'
    plugin_list = []
    plugin_opts = {}
    module_level = None

    try:
        opts, args = getopt.getopt (sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        sys.exit(1)

    for opt, value in opts:
        if opt in ("-h", "--help", "-help"):
            usage()
            sys.exit(0)
        elif opt in ("-V", "--version"):
            print version
            sys.exit(0)
        elif opt in ("-u", "--db-user", "--user"):
            user = value
        elif opt in ("-p", "--db-password", "--password"):
            passwd = value
        elif opt in ("-H", "--db-hostname", "--hostname"):
            hostname = value
        elif opt in ("-d", "--db-database", "--database"):
            database = value
        elif opt in ("--db-driver", "--driver"):
            driver = value
        elif opt in ("-b", "--branch"):
            branch = value
        elif opt in ("-l", "--module-level"):
            module_level = int (value)
        elif opt in ("--plugin-info", "--info"):
            p = get_plugin (value)
            p.info ()
            sys.exit(0)
        elif opt in ("--plugin-run", "--run-plugin"):
            plugin_list.append (value)
            plugin_opts[value] = []
        elif opt in ("--plugin-scan", "--scan"):
            if len (plugins) == 0:
                print "No plugins available"
                sys.exit(0)

            for p in plugins:
                get_plugin (p).info ()
                print "--------------------"

            sys.exit(0)
        else:
            try:
                plugin = plugin_list[-1]
            except IndexError:
                continue

            plugin_opts[plugin].append ((opt, value))

    if len (args) <= 0:
        args.append (os.getcwd ())

    # Connect to the database
    conection = driver + "://" + user + ":" + passwd + "@" + hostname + "/" + database
    db = dbmodule.Database(conection)

    if len (plugin_list) <= 0:
        run (db, args, module_level)
        db.close ()

        return
    
    # Run plugins
    try:
        db.executeSQLRaw ("SELECT commit_id from log where commit_id = 0")
    except:
        # If database doesn't exist, create and fill it now
        run (db, args, module_level)

    for plugin in plugin_list:
        p = get_plugin (plugin, db, plugin_opts[plugin])
        p.run ()

    db.close ()
