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

from tables import *
import intermediate_tables as intmodule
import modrequest as mdmodule

# Some stuff about the project
author = "(C) 2004,2006 %s <%s>" % ("Libresoft", "cvsanaly@libresoft.es")
name = "cvsanaly %s - Libresoft Group http://www.libresoft.es" % ("1.0-BETA2")
credits = "\n%s \n%s\n" % (name,author)


def usage():
    print "Usage: %s [options]" % (sys.argv[0])
    print """
Run inside the checked out svn or cvs directory to analyze

Options:

  -h, --help         Print this usage message.

  -u, --user         User name for accesing the database
  -p, --passwd       User password for accessing the database (default empty)
  -d, --database     Database (schema) name

  -h, --hostname     Host running the database server (default is localhost)
  -l, --log-file     Log file name
  -r, --repo-type    Type of repository (cvs|svn), default is svn
  -i, --driver       Output driver (mysql|stdout), default is mysql
"""

def main():

    print credits

    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hu:p:d:h:l:r:i:"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = [ "help", "user=", "passwd=", "database=", "hostname=", "log-file=", "repo-type", "driver"]

    # Default options
    passwd = ''
    hostname = 'localhost'
    logfile = ''
    type = 'svn'
    driver = 'mysql'

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError:
        usage()
        sys.exit(1)

#    if len(args) < 3:
#        usage()
#        sys.exit(0)

    # Config args come from args
#    user = args[0]
#    passwd = args[1]
#    database = args[2]
#    hostname = args[3]

    for opt, value in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-u", "--user"):
            user = value
        elif opt in ("-p", "--passwd"):
            passwd = value
        elif opt in ("-d", "--database"):
            database = value
        elif opt in ("-h", "--hostname"):
            hostname = value
        elif opt in ("-l", "--log-file"):
            logfile = value
        elif opt in ("-r", "--repo-type"):
            type = value
        elif opt in ("-i", "--driver"):
            driver = value

    # Connect to the database
#    if passwd == "":
#        conection = driver + "://" + user + "@" + hostname + "/" + database
#    else:
    conection = driver + "://" + user + ":" + passwd + "@" + hostname + "/" + database
#    print conection
        
    db = dbmodule.Database(conection)

    # Create database and tables
    db.create_database()
    db.create_table('files',files)
    db.create_table('commiters',commiters)
    db.create_table('log',log)
    db.create_table('modules', modules)
    db.create_table('commiters_module',commiters_module)
    db.create_table('comments',comments)
    db.create_table('cvsanal_fileTypes',cvsanal_fileTypes)
    db.create_table('cvsanal_temp_commiters',cvsanal_temp_commiters)
    db.create_table('cvsanal_temp_modules',cvsanal_temp_modules)
    db.create_table('cvsanal_temp_inequality',cvsanal_temp_inequality)
    db.create_table('cvsanal_modrequest',cvsanal_modrequest)

    # CVS/SVN interactive
    repos = rpmodule.RepositoryFactory.create(type)
    repos.log(db, logfile)

    db.close()

    # This should go in a new cvsanaly-web script
    #intmodule.intermediate_table_commitersmodules(db)
    #intmodule.intermediate_table_commiters(db)
    #intmodule.intermediate_table_fileTypes(db)
    #intmodule.intermediate_table_modules(db)
    #mdmodule.modrequest(db)

