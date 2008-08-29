# Copyright (C) 2008 LibreSoft
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

from pycvsanaly2.Database import SqliteDatabase, MysqlDatabase, TableAlreadyExists, statement
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.extensions.file_types import guess_file_type
from pycvsanaly2.utils import to_utf8

class DBFileType:

    id_counter = 1

    __insert__ = "INSERT INTO file_types (id, file_id, type) values (?, ?, ?)"

    def __init__ (self, id, type, file_id):
        if id is None:
            self.id = DBFileType.id_counter
            DBFileType.id_counter += 1
        else:
            self.id = id

        self.type = to_utf8 (type)
        self.file_id = file_id
        

class FileTypes (Extension):
    
    deps = ['FilePaths']

    def __init__ (self):
        self.db = None
    
    def __create_table (self, cnn):
        cursor = cnn.cursor ()

        if isinstance (self.db, SqliteDatabase):
            import pysqlite2.dbapi2
            
            try:
                cursor.execute ("CREATE TABLE file_types (" +
                                "id integer primary key," +
                                "file_id integer," +
                                "type varchar" +
                                ")")
            except pysqlite2.dbapi2.OperationalError:
                raise TableAlreadyExists
            except:
                raise
        elif isinstance (self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute ("CREATE TABLE file_types (" +
                                "id INT primary key," +
                                "file_id integer," +
                                "type mediumtext," + 
                                "FOREIGN KEY (file_id) REFERENCES tree(id)" +
                                ") CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    raise TableAlreadyExists
                raise
            except:
                raise
            
        cnn.commit ()
        cursor.close ()

    def __get_files (self, cnn):
        cursor = cnn.cursor ()
        cursor.execute (statement ("SELECT file_id from file_types", self.db.place_holder))
        files = [res[0] for res in cursor.fetchall ()]
        cursor.close ()

        return files
        
    def run (self, repo, db):
        self.db = db
        
        cnn = self.db.connect ()

        files = []
        
        try:
            self.__create_table (cnn)
        except TableAlreadyExists:
            cursor = cnn.cursor ()
            cursor.execute (statement ("SELECT max(id) from file_types", db.place_holder))
            id = cursor.fetchone ()[0]
            if id is not None:
                DBFileType.id_counter = id
            cursor.close ()

            files = self.__get_files (cnn)
        except Exception, e:
            raise ExtensionRunError (str (e))

        cursor = cnn.cursor ()
        cursor.execute (statement ("SELECT file_id, path from file_paths", db.place_holder))
        rs = cursor.fetchmany ()
        while rs:
            types = []

            for file_id, path in rs:
                if file_id not in files:
                    type = guess_file_type (path)
                    types.append (DBFileType (None, type, file_id))
                    
            new_cursor = cnn.cursor ()
            file_types = [(type.id, type.file_id, type.type) for type in types]
            new_cursor.executemany (statement (DBFileType.__insert__, self.db.place_holder), file_types)
            new_cursor.close ()

            rs = cursor.fetchmany ()
            
        cnn.commit ()
        cnn.close ()
        

register_extension ("FileTypes", FileTypes)
