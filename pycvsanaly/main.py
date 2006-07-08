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
import parserconfig as parsermodule
import repository as rpmodule

from tables import *
import intermediate_tables as intmodule
import modrequest as mdmodule

# Some stuff about the project
author = "(C) 2004,2006 %s <%s>" % ("Libresoft", "cvsanaly@libresoft.es")
name = "cvsanaly %s - Libresoft Group http://www.libresoft.es" % ("1.0-BETA1")
credits = "\n%s \n%s\n" % (name,author)


def usage():
    print "Usage: %s username password database hostname" % (sys.argv[0])
    print """
Options:

  -h, --help               Print this usage message.

  -l, --log-file           Use the current log file            
  -d, --driver             Output driver [mysql|stdout]
  -w, --username           Database username
  -a, --password           User password 
  -d, --database           Database name
  -h, --hostname           Name of the host which runs database server
"""

def main():

    print credits

    short_opts = "hno:u:p:d:h:l:"
    long_opts = [ "help", "options", "driver=", "user=", "password=","database=","hostname=","log-file="]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    driver = "mysql"
    hostname = "localhost"

    if len(args) < 4:
        usage()
        sys.exit(0)

    # Config args come from args
    user = args[0]
    password = args[1]
    database = args[2]
    hostname = args[3]
    type = "cvs"
    logfile = ""

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-p", "--password"):
            password = a
        elif o in ("-d", "--database"):
            database = a
        elif o in ("-h", "--hostname"):
            hostname = a
        elif o in ("-l", "--log-file"):
            logfile = a

    conection = driver + "://" + user + ":" + password + "@" + hostname + "/" + database
    db = dbmodule.Database(conection)

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
    repos.log(db,logfile)

    # This should go in a new cvsanaly-web script
    intmodule.intermediate_table_commiters(db)
    intmodule.intermediate_table_fileTypes(db)
    intmodule.intermediate_table_modules(db)
    mdmodule.modrequest(db)

