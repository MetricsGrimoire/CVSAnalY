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

from Repository import *
import datetime 

class DBRepository:

    id_counter = 1

    __insert__ = "INSERT INTO repositories (id, uri, name, type) values (?, ?, ?, ?)"

    def __init__ (self, id, uri, name, type):
        if id is None:
            self.id = DBRepository.id_counter
            DBRepository.id_counter += 1
        else:
            self.id = id

        self.uri = unicode (uri)
        self.name = unicode (name)
        self.type = unicode (type)

class DBLog:

    id_counter = 1

    __insert__ = "INSERT INTO scmlog (id, rev, committer, author, date, lines_added, lines_removed, message, composed_rev, repository_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    
    def __init__ (self, id, commit):
        if id is None:
            self.id = DBLog.id_counter
            DBLog.id_counter += 1
        else:
            self.id = id
        self.rev = unicode (commit.revision)
        self.committer = unicode (commit.committer, 'utf-8', 'replace')
        if commit.author is not None:
            self.author = unicode (commit.author, 'utf-8', 'replace')
        else:
            self.author = None

        if commit.lines is not None:
            self.lines_added = commit.lines[0]
            self.lines_removed = commit.lines[1]
        else:
            self.lines_added = self.lines_removed = 0
            
        self.date = commit.date
        self.message = unicode (commit.message, 'utf-8', 'replace')
        self.composed_rev = commit.composed_rev

class DBFile:

    id_counter = 1

    __insert__ = "INSERT INTO tree (id, parent, file_name, deleted) values (?, ?, ?, ?)"
    
    def __init__ (self, id, file_name, parent, deleted = False):
        if id is None:
            self.id = DBFile.id_counter
            DBFile.id_counter += 1
        else:
            self.id = id
        self.file_name = unicode (file_name)
        self.parent = parent
        self.deleted = deleted

class DBAction:

    id_counter = 1

    __insert__ = "INSERT INTO actions (id, type, file_id, commit_id) values (?, ?, ?, ?)"
    
    def __init__ (self, id, type):
        if id is None:
            self.id = DBAction.id_counter
            DBAction.id_counter += 1
        else:
            self.id = id
        self.type = type

class DatabaseException (Exception):
    '''Generic Database Exception'''

    def __init__ (self, message = None):
        Exception.__init__ (self)

        self.message = message
        
class DatabaseDriverNotAvailable (DatabaseException):
    '''Database driver is not available'''
class DatabaseDriverNotSupported (DatabaseException):
    '''Database driver is not supported'''
class DatabaseNotFound (DatabaseException):
    '''Selected database doesn't exist'''
class AccessDenied (DatabaseException):
    '''Access denied to databse'''
class TableAlreadyExists (DatabaseException):
    '''Table alredy exists in database'''

def statement (str, ph_mark):
    if "?" == ph_mark or "?" not in str:
        return str

    tokens = str.split("'")
    for i in range(0, len (tokens), 2):
        tokens[i] = tokens[i].replace("?", ph_mark)
        
    return "'".join (tokens)
    
class Database:
    '''CVSAnaly Database'''

    place_holder = "?"

    def __init__ (self, database):
        self.database = database
        
    ## Non storm interface
    def connect (self):
        raise NotImplementedError

class SqliteDatabase (Database):

    def __init__ (self, database):
        Database.__init__ (self, database)

    def connect (self):
        import pysqlite2.dbapi2 as db

        return db.connect (self.database)
    
    def create_tables (self, cursor):
        import pysqlite2.dbapi2

        try:
            cursor.execute ("CREATE TABLE repositories (" +
                            "id integer primary key," +
                            "uri varchar," +
                            "name varchar," +
                            "type varchar" + 
                            ")")
            cursor.execute ("CREATE TABLE scmlog (" +
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
            cursor.execute ("CREATE TABLE actions (" +
                            "id integer primary key," +
                            "type varchar(1)," +
                            "file_id integer," +
                            "commit_id integer" +
                            ")")
            cursor.execute ("CREATE TABLE tree (" +
                            "id integer primary key," +
                            "parent integer," +
                            "file_name varchar(255)," +
                            "deleted bool" +
                            ")")
        except pysqlite2.dbapi2.OperationalError:
            raise TableAlreadyExists
        except:
            raise
        
class MysqlDatabase (Database):

    place_holder = "%s"
    
    def __init__ (self, database, username, password, hostname):
        Database.__init__ (self, database)

        self.username = username
        self.password = password
        self.hostname = hostname
        
        self.db = None

    def connect (self):
        import MySQLdb
        import _mysql_exceptions

        try:
            if self.password is not None:
                return MySQLdb.connect (self.hostname, self.username, self.password, self.database)
            else:
                return MySQLdb.connect (self.hostname, self.username, db = self.database)
        except _mysql_exceptions.OperationalError, e:
            if e.args[0] == 1049:
                raise DatabaseNotFound
            elif e.args[0] == 1045:
                raise AccessDenied
            else:
                raise DatabaseException (str (e))
        except:
            raise
        
    def create_tables (self, cursor):
        import _mysql_exceptions

        try:
            cursor.execute ("CREATE TABLE repositories (" +
                            "id INT primary key," +
                            "uri varchar(255)," +
                            "name varchar(255)," +
                            "type varchar(30)" + 
                            ")")
            cursor.execute ("CREATE TABLE scmlog (" +
                            "id INT primary key," +
                            "rev mediumtext," +
                            "committer varchar(255)," +
                            "author varchar(255)," +
                            "date timestamp," +
                            "lines_added int," +
                            "lines_removed int," +
                            "message text," +
                            "composed_rev bool," +
                            "repository_id INT," + 
                            "FOREIGN KEY (repository_id) REFERENCES repositories(id)" + 
                            ")")
            cursor.execute ("CREATE TABLE tree (" +
                            "id INT primary key," +
                            "parent integer," +
                            "file_name varchar(255)," +
                            "deleted bool" +
                            ")")
            cursor.execute ("CREATE TABLE actions (" +
                            "id INT primary key," +
                            "type varchar(1)," +
                            "file_id integer," +
                            "commit_id integer," +
                            "FOREIGN KEY (file_id) REFERENCES tree(id)," +
                            "FOREIGN KEY (commit_id) REFERENCES scmlog(id)" + 
                            ")")
        except _mysql_exceptions.OperationalError, e:
            raise
            if e.args[0] == 1050:
                raise TableAlreadyExists
            else:
                raise DatabaseException (str (e))
        except:
            raise

# TODO
# class CAPostgresDatabase (CADatabase):

def create_database (driver, database, username = None, password = None, hostname = None):
    if driver == 'sqlite':
        db = SqliteDatabase (database)
        return db
    elif driver == 'mysql':
        db = MysqlDatabase (database, username, password, hostname)
    elif driver == 'postgres':
        # TODO
        raise DatabaseDriverNotSupported
    else:
        raise DatabaseDriverNotSupported
                
    # Try to connect to database
    try:
        db.connect ().close ()
        return db
    except AccessDenied:
        if password is None:
            import sys, getpass

            # FIXME: catch KeyboardInterrupt exception
            # FIXME: it only works on UNIX (/dev/tty),
            #  not sure whether it's bug or a feature, though
            oldout, oldin = sys.stdout, sys.stdin
            sys.stdin = sys.stdout = open ('/dev/tty', 'r+')
            password = getpass.getpass ()
            sys.stdout, sys.stdin = oldout, oldin
            
            return create_database (driver, database, username, password, hostname)
        raise AccessDenied
    
    return db

if __name__ == '__main__':
    db = create_database ('sqlite', '/tmp/foo.db')

    cnn = db.connect ()
    
    cursor = cnn.cursor ()
    db.create_tables (cursor)
    cursor.close ()
    
    cnn.commit ()
    cnn.close ()

    
