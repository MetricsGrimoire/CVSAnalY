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

from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists,
                                  statement, DBFile)
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.utils import to_utf8

class DBFilePath:

    id_counter = 1

    __insert__ = "INSERT INTO file_paths (id, file_id, path) values (?, ?, ?)"

    def __init__ (self, id, path, file_id):
        if id is None:
            self.id = DBFilePath.id_counter
            DBFilePath.id_counter += 1
        else:
            self.id = id

        self.path = to_utf8 (path)
        self.file_id = file_id

class FilePaths (Extension):

    def __init__ (self):
        self.db = None
    
    def __create_table (self, cnn):
        cursor = cnn.cursor ()

        if isinstance (self.db, SqliteDatabase):
            import pysqlite2.dbapi2
            
            try:
                cursor.execute ("CREATE TABLE file_paths (" +
                                "id integer primary key," +
                                "file_id integer," +
                                "path varchar" +
                                ")")
            except pysqlite2.dbapi2.OperationalError:
                cursor.close ()
                raise TableAlreadyExists
            except:
                raise
        elif isinstance (self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute ("CREATE TABLE file_paths (" +
                                "id INT primary key," +
                                "file_id integer," +
                                "path mediumtext," + 
                                "FOREIGN KEY (file_id) REFERENCES tree(id)" +
                                ") CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    cursor.close ()
                    raise TableAlreadyExists
                raise
            except:
                raise
            
        cnn.commit ()
        cursor.close ()

    def get_path_from_id (self, cnn, file_id):
        retval = []

        def get_file (cursor, fid):
            cursor.execute (statement ("SELECT id, parent, file_name from tree where id = ?", self.db.place_holder), (fid,))
            
            try:
                (id, parent, file_name) = cursor.fetchone ()
            except TypeError:
                return None
            
            return DBFile (id, file_name, parent)
        
        def build_path (cursor, node):
            if node is None or node.id == -1:
                return True

            retval.insert (0, node.file_name)
            return build_path (cursor, get_file (cursor, node.parent))

        cursor = cnn.cursor ()
        node = get_file (cursor, file_id)

        if build_path (cursor, node):
            cursor.close ()
            return '/'.join (retval)

        cursor.close ()
        
        return None

    def __get_paths_for_repository (self, repo_id, cursor):
        query = "SELECT fp.file_id from file_paths fp, tree t " + \
                "WHERE t.id = fp.file_id and t.repository_id = ?"
        cursor.execute (statement (query, self.db.place_holder), (repo_id,))
        paths = [res[0] for res in cursor.fetchall ()]

        return paths
    
    def run (self, repo, uri, db):
        self.db = db

        cnn = self.db.connect ()

        cursor = cnn.cursor ()
        cursor.execute (statement ("SELECT id from repositories where uri = ?", db.place_holder), (repo.get_uri (),))
        repo_id = cursor.fetchone ()[0]

        # If table does not exist, the list of paths is empty,
        # otherwise it will be filled within the except block below
        paths = []
        
        try:
            self.__create_table (cnn)
        except TableAlreadyExists:
            cursor.execute (statement ("SELECT max(id) from file_paths", db.place_holder))
            id = cursor.fetchone ()[0]
            if id is not None:
                DBFilePath.id_counter = id + 1

            paths = self.__get_paths_for_repository (repo_id, cursor)
        except Exception, e:
            raise ExtensionRunError (str (e))

        cursor.execute (statement ("SELECT id from tree where repository_id = ?", db.place_holder), (repo_id,))
        write_cursor = cnn.cursor ()
        rs = cursor.fetchmany ()
        while rs:
            files = []

            for id in rs:
                if id[0] in paths:
                    continue
                path = self.get_path_from_id (cnn, id[0])
                if path is not None:
                    files.append (DBFilePath (None, path, id[0]))

            file_paths = [(file.id, file.file_id, file.path) for file in files]
            write_cursor.executemany (statement (DBFilePath.__insert__, self.db.place_holder), file_paths)

            rs = cursor.fetchmany ()
            
        cnn.commit ()
        write_cursor.close ()
        cursor.close ()
        cnn.close ()

register_extension ("FilePaths", FilePaths)
                     
