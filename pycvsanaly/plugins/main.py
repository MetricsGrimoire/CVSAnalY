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

import getopt

from pycvsanaly.libcvsanaly.CVSAnaly import CVSAnaly
from pycvsanaly.libcvsanaly.Database import *
from pycvsanaly.plugins import create_plugin, scan_plugins

def usage ():
    print "Usage: cvsanaly-plugins [options] <plugin> [plugin-options]"
    print """
Run the given plugin. 

Options:

  -h, --help         Print this usage message.
  -V, --version      Show version

Database:

      --db-driver    Output database driver [sqlite|mysql|postgres] (sqlite)
  -u, --db-user      Database user name (operator)
  -p, --db-password  Database user password
  -d, --db-database  Database name (cvsanaly)
  -H, --db-hostname  Name of the host where database server is running (localhost)

Available plugins:
"""
    for plugin in scan_plugins ():
        print plugin

    print """
Type cvsanaly-plugins <plugin> --help for help on a specific plugin
"""
        
def main (argv):
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hVu:p:d:H:"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help", "version", "db-user=", "db-password=", "db-hostname=", "db-database=", "db-driver="]

        # Default options
    user = 'operator'
    passwd = None
    hostname = 'localhost'
    database = 'cvsanaly'
    branch = None
    driver = 'sqlite'

    try:
        opts, args = getopt.getopt (argv, short_opts, long_opts)
    except getopt.GetoptError, e:
        print e
        return 1

    for opt, value in opts:
        if opt in ("-h", "--help", "-help"):
            usage ()
            return 0
        elif opt in ("-V", "--version"):
            print version
            return 0
        elif opt in ("-u", "--db-user"):
            user = value
        elif opt in ("-p", "--db-password"):
            passwd = value
        elif opt in ("-H", "--db-hostname"):
            hostname = value
        elif opt in ("-d", "--db-database"):
            database = value
        elif opt in ("--db-driver"):
            driver = value

    if len (args) <= 0:
        print "Plugin name not provided"
        return 1

    plugin = create_plugin (args[0], args[1:])

    db = get_database (driver, database, user, passwd, hostname)
    db.connect ()
    
    ca = CVSAnaly (db)
    plugin.run (ca)

    db.close ()
    
	
