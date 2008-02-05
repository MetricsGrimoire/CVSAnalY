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

from storm.locals import *
from storm.exceptions import *
import datetime

class DBRepository (object):

    __storm_table__ = "repositories"

    id = Int (primary = True)
    uri = Unicode ()
    name = Unicode ()
    type = Unicode ()

class DBLog (object):

    __storm_table__ = "scmlog"
    
    id = Int (primary = True)
    rev = Unicode ()
    committer = Unicode ()
    author = Unicode ()
    date = DateTime ()
    lines_added = Int ()
    lines_removed = Int ()
    message = Unicode ()
    composed_rev = Bool ()
    repository_id = Int ()
    repository = Reference (repository_id, DBRepository.id)

class DBFile (object):

    __storm_table__ = "tree"

    id = Int (primary = True)
    parent = Int ()
    file_name = Unicode ()
    deleted = Bool ()

class DBAction (object):
    
    __storm_table__ = "actions"
    
    id = Int (primary = True)
    type = Chars ()
    file_id = Int ()
    file = Reference (file_id, DBFile.id)
    commit_id = Int ()
    commit = Reference (commit_id, DBLog.id)
    
class CADatabaseException (Exception):
    '''Generic Database Exception'''

    def __init__ (self, message = None):
        Exception.__init__ (self)

        self.message = message

class CADatabaseDriverNotAvailable (CADatabaseException):
    '''Database driver is not available'''
class CADatabaseDriverNotSupported (CADatabaseException):
    '''Database driver is not supported'''
class CADatabaseNotFound (CADatabaseException):
    '''Selected database doesn't exist'''
class CAAccessDenied (CADatabaseException):
    '''Access denied to databse'''
class CATableAlreadyExists (CADatabaseException):
    '''Table alredy exists in database'''
        
class CADatabase:
    '''CVSAnaly Database'''

    def __init__ (self, conn_uri):
        try:
            self.db = create_database (conn_uri)
        except DatabaseModuleError, e:
            raise CADatabaseDriverNotAvailable (str (e))
        except ImportError:
            raise CADatabaseDriverNotSupported
        except:
            raise

        self.store = None
        
    def create_tables (self):
        raise NotImplementedError

    def get_store (self):
        return self.store

    def connect (self):
        if self.store is not None:
            self.close ()
        self.store = Store (self.db)

    def close (self):
        if self.store is not None:
            self.store.close ()
            self.store = None

    def commit (self):
        if self.store is not None:
            self.store.commit ()

    def flush (self):
        if self.store is not None:
            self.store.flush ()

class CASqliteDatabase (CADatabase):

    def __init__ (self, conn_uri):
        CADatabase.__init__ (self, conn_uri)

    def create_tables (self):
        import pysqlite2.dbapi2

        assert self.store is not None
        
        try:
            self.store.execute ("CREATE TABLE repositories (" +
                                "id integer primary key," +
                                "uri varchar," +
                                "name varchar," +
                                "type varchar" + 
                                ")")
            self.store.execute ("CREATE TABLE scmlog (" +
                                "id integer primary key," +
                                "rev varchar," +
                                "committer varchar," +
                                "author varchar," +
                                "date timestamp," +
                                "lines_added integer," +
                                "lines_removed integer," +
                                "message varchar," +
                                "composed_rev bool," + 
                                "repository_id integer" +
                                ")")
            self.store.execute ("CREATE TABLE actions (" +
                                "id integer primary key," +
                                "type varchar(1)," +
                                "file_id integer," +
                                "commit_id integer" +
                                ")")
            self.store.execute ("CREATE TABLE tree (" +
                                "id integer primary key," +
                                "parent integer," +
                                "file_name varchar(255)," +
                                "deleted bool" +
                                ")")
            self.store.commit ()
        except pysqlite2.dbapi2.OperationalError:
            raise CATableAlreadyExists
        except:
            raise
        
class CAMysqlDatabase (CADatabase):

    def __init__ (self, conn_uri):
        CADatabase.__init__ (self, conn_uri)

    def create_tables (self):
        import _mysql_exceptions

        assert self.store is not None
        
        try:
            self.store.execute ("CREATE TABLE repositories (" +
                                "id INT AUTO_INCREMENT primary key," +
                                "uri varchar(255)," +
                                "name varchar(255)," +
                                "type varchar(30)" + 
                                ") ENGINE = INNODB")
            self.store.execute ("CREATE TABLE scmlog (" +
                                "id INT AUTO_INCREMENT primary key," +
                                "rev varchar(255)," +
                                "committer varchar(255)," +
                                "author varchar(255)," +
                                "date timestamp," +
                                "lines_added int," +
                                "lines_removed int," +
                                "message varchar(255)," +
                                "composed_rev bool," +
                                "repository_id INT," + 
                                "FOREIGN KEY (repository_id) REFERENCES repositories(id)" + 
                                ") ENGINE = INNODB")
            self.store.execute ("CREATE TABLE tree (" +
                                "id INT AUTO_INCREMENT primary key," +
                                "parent integer," +
                                "file_name varchar(255)," +
                                "deleted bool" +
                                ") ENGINE = INNODB")
            self.store.execute ("CREATE TABLE actions (" +
                                "id INT AUTO_INCREMENT primary key," +
                                "type varchar(1)," +
                                "file_id integer," +
                                "commit_id integer," +
                                "FOREIGN KEY (file_id) REFERENCES tree(id)," +
                                "FOREIGN KEY (commit_id) REFERENCES scmlog(id)" + 
                                ") ENGINE = INNODB")
        except _mysql_exceptions.OperationalError, e:
            raise
            if e.args[0] == 1050:
                raise CATableAlreadyExists
            else:
                raise CADatabaseException (str (e))
        except:
            raise
        
    def get_store (self):
        import _mysql_exceptions
        
        try:
            return Store (self.db)
        except _mysql_exceptions.OperationalError, e:
            if e.args[0] == 1049:
                raise CADatabaseNotFound
            elif e.args[0] == 1045:
                raise CAAccessDenied
            else:
                raise CADatabaseException (str (e))
        except:
            raise

class CAPostgresDatabase (CADatabase):

    def __init__ (self, conn_uri):
        CADatabase.__init__ (self, conn_uri)

    def create_tables (self, store):
        # TODO
        pass


def get_database (driver, database, username = None, password = None, hostname = None):
    if driver == 'sqlite':
        conn_uri =  driver + ':' + database
    elif password is not None:
        conn_uri = driver + '://' + username + ':' + password + '@' + hostname + '/' + database
    else:
        conn_uri = driver + '://' + username + '@' + hostname + '/' + database
    
    if driver == 'sqlite':
        db = CASqliteDatabase (conn_uri)
        return db
    elif driver == 'mysql':
        db = CAMysqlDatabase (conn_uri)
    elif driver == 'postgres':
        db = CAPostgresDatabase (conn_uri)
    else:
        raise CADatabaseDriverNotSupported
                
    # Try to connect to database
    try:
        db.get_store ().close ()
        return db
    except CAAccessDenied:
        if password is None:
            import sys, getpass

            # FIXME: catch KeyboardInterrupt exception
            # FIXME: it only works on UNIX (/dev/tty),
            #  not sure whether it's bug or a feature, though
            oldout, oldin = sys.stdout, sys.stdin
            sys.stdin = sys.stdout = open ('/dev/tty', 'r+')
            password = getpass.getpass ()
            sys.stdout, sys.stdin = oldout, oldin
            
            return get_database (driver, database, username, password, hostname)
        raise CAAccessDenied
    
    return db
