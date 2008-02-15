# Copyright (C) 2006 LibreSoft
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
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

"""
Main funcion of cvsanaly. Fun starts here!

@author:       Alvaro Navarro, Carlos Garcia Campos
@organization: LibreSoft
@copyright:    LibreSoft
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import os
import getopt

from repositoryhandler.backends import create_repository, create_repository_from_path
from ParserFactory import create_parser_from_logfile, create_parser_from_repository
from Database import create_database, TableAlreadyExists, DBRepository, statement
from DBContentHandler import DBContentHandler
from Config import Config
from utils import *

# Some stuff about the project
version = "2.0"
author = "(C) 2004,2008 %s <%s>" % ("LibreSoft", "libresoft-tools-devel@lists.morfeo-project.org")
name = "cvsanaly %s - LibreSoft Group http://www.libresoft.es" % (version)
credits = "%s \n%s\n" % (name, author)

def usage ():
    print credits
    print "Usage: cvsanaly [options] [URI]"
    print """
Analyze the given URI. An URI can be a checked out directory, 
or a remote URL pointing to a repository. If URI is omitted,
the current working directory will be used as a checked out directory.

Options:

  -h, --help         Print this usage message.
  -V, --version      Show version
      --profile      Enable profiling mode
  -f, --config-file  Use a custom configuration file
      --with-lines   Get lines added/removed per commit. Only disabled by default
                     for SVN repositories because of performance reasons

  -b, --branch       Repository branch to analyze (head/trunk/master)
  -l, --repo-logfile Logfile to use instead of getting log from the repository

Database:

      --db-driver    Output database driver [sqlite|mysql|postgres] (sqlite)
  -u, --db-user      Database user name (operator)
  -p, --db-password  Database user password
  -d, --db-database  Database name (cvsanaly)
  -H, --db-hostname  Name of the host where database server is running (localhost)
"""

def main (argv):
    # Short (one letter) options. Those requiring argument followed by :
    short_opts = "hVf:b:l:u:p:d:H:"
    # Long options (all started by --). Those requiring argument followed by =
    long_opts = ["help", "version", "profile", "config-file=", "branch=", "repo-logfile=", "with-lines",
                 "db-user=", "db-password=", "db-hostname=", "db-database=", "db-driver="]

    # Default options
    profile = None
    configfile = None
    user = None
    passwd = None
    hostname = None
    database = None
    branch = None
    driver = None
    logfile = None
    lines = None

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
        elif opt in ("--profile", ):
            profile = True
        elif opt in ("-f", "--config-file"):
            configfile = value
        elif opt in ("--with-lines", ):
            lines = True
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
        elif opt in ("-b", "--branch"):
            branch = value
        elif opt in ("-l", "--repo-logfile"):
            logfile = value

    if len (args) <= 0:
        uri = os.getcwd ()
    else:
        uri = args[0]

    config = Config ()
    if configfile is not None:
        config.load_from_file (configfile)
    else:
        config.load ()

    if profile is not None:
        config.profile = profile
    if branch is not None:
        config.branch = branch
    if logfile is not None:
        config.repo_logfile = logfile
    if driver is not None:
        config.db_driver = driver
    if user is not  None:
        config.db_user = user
    if passwd is not None:
        config.db_password = passwd
    if hostname is not None:
        config.db_hostname = hostname
    if database is not None:
        config.db_database = database

    path = uri_to_filename (uri)
    if path is not None:
        repo = create_repository_from_path (path)
    else:
        repo = create_repository ('svn', uri)

    if lines is not None:
        config.lines = lines
    else:
        if repo.get_type () == 'svn':
            config.lines = False

    if config.repo_logfile is not None:
        parser = create_parser_from_logfile (config.repo_logfile)
        parser.set_repository (repo)
    else:
        parser = create_parser_from_repository (repo)
        if path is not None:
            parser.set_uri (path)
        else:
            parser.set_uri (uri)

    if parser is None:
        print "Failed to create parser"
        return 1

    # TODO: check parser type == logfile type

    db_exists = False
    
    db = create_database (config.db_driver,
                          config.db_database,
                          config.db_user,
                          config.db_password,
                          config.db_hostname)
    cnn = db.connect ()
    cursor = cnn.cursor ()
    try:
        db.create_tables (cursor)
        cnn.commit ()
    except TableAlreadyExists:
        db_exists = True

    # Add repository to Database
    if db_exists:
        cursor.execute ("SELECT id from repositories where uri = ?", (repo.get_uri (),))
        rep = cursor.fetchone ()
        cursor.close ()
        
    if not db_exists or rep is None:
        # We consider the name of the repo as the last item of the root path
        name = repo.get_uri ().split ("/")[-1].strip ()
        cursor = cnn.cursor ()
        rep = DBRepository (None, repo.get_uri (), name, repo.get_type ())
        cursor.execute (statement (DBRepository.__insert__, db.place_holder), (rep.id, rep.uri, rep.name, rep.type))
        cursor.close ()
        cnn.commit ()

    cnn.close ()
        
    print "Parsing log for %s" % (uri)
    parser.set_content_handler (DBContentHandler (db))
    parser.run ()


