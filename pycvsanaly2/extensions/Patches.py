# Copyright (C) 2009 LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from repositoryhandler.backends.watchers import DIFF
from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists, statement, ICursor)
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.utils import printerr, uri_to_filename
from cStringIO import StringIO


class DBPatch:
    id_counter = 1

    __insert__ = "INSERT INTO patches (id, commit_id, patch) values (?, ?, ?)"

    def __init__(self, id, commit_id, data):
        if id is None:
            self.id = DBPatch.id_counter
            DBPatch.id_counter += 1
        else:
            self.id = id

        self.commit_id = commit_id
        self.patch = data


class Patches(Extension):
    INTERVAL_SIZE = 100

    def __init__(self):
        self.db = None

    def __create_table(self, cnn):
        cursor = cnn.cursor()

        if isinstance(self.db, SqliteDatabase):
            import sqlite3

            try:
                cursor.execute("CREATE TABLE patches (" +
                               "  id integer primary key," +
                               "  commit_id integer," +
                               "  patch blob" +
                               ")")
            except sqlite3.OperationalError:
                cursor.close()
                raise TableAlreadyExists
            except:
                raise
        elif isinstance(self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute("CREATE TABLE patches (" +
                              "  id INT primary key," +
                              "  commit_id integer," +
                              "  patch LONGBLOB," +
                              "  FOREIGN KEY (commit_id) REFERENCES scmlog(id)" +
                              ") ENGINE=MyISAM CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    cursor.close()
                    raise TableAlreadyExists
                raise
            except:
                raise

        cnn.commit()
        cursor.close()

    def __get_patches_for_repository(self, repo_id, cursor):
        query = "SELECT p.commit_id from patches p, scmlog s " + \
                "WHERE p.commit_id = s.id and repository_id = ?"
        cursor.execute(statement(query, self.db.place_holder), (repo_id,))
        commits = [res[0] for res in cursor.fetchall()]

        return commits

    def get_patch_for_commit(self, rev):
        def diff_line(data, io):
            io.write(data)

        io = StringIO()
        wid = self.repo.add_watch(DIFF, diff_line, io)
        try:
            self.repo.show(self.repo_uri, rev)
            data = io.getvalue()
        except Exception, e:
            printerr("Error running show command: %s", (str(e)))
            data = None

        self.repo.remove_watch(DIFF, wid)
        io.close()

        return data

    def run(self, repo, uri, db):
        self.db = db
        self.repo = repo

        path = uri_to_filename(uri)
        if path is not None:
            repo_uri = repo.get_uri_for_path(path)
        else:
            repo_uri = uri

        path = uri_to_filename(uri)
        self.repo_uri = path or repo.get_uri()

        cnn = self.db.connect()

        cursor = cnn.cursor()
        cursor.execute(statement("SELECT id from repositories where uri = ?", db.place_holder), (repo_uri,))
        repo_id = cursor.fetchone()[0]

        # If table does not exist, the list of commits is empty,
        # otherwise it will be filled within the except block below
        commits = []

        try:
            self.__create_table(cnn)
        except TableAlreadyExists:
            cursor.execute(statement("SELECT max(id) from patches", db.place_holder))
            id = cursor.fetchone()[0]
            if id is not None:
                DBPatch.id_counter = id + 1

            commits = self.__get_patches_for_repository(repo_id, cursor)
        except Exception, e:
            raise ExtensionRunError(str(e))

        write_cursor = cnn.cursor()
        icursor = ICursor(cursor, self.INTERVAL_SIZE)
        icursor.execute(statement("SELECT id, rev, composed_rev from scmlog where repository_id = ?",
                                  db.place_holder), (repo_id,))
        rs = icursor.fetchmany()
        while rs:
            for commit_id, revision, composed_rev in rs:
                if commit_id in commits:
                    continue

                if composed_rev:
                    rev = revision.split("|")[0]
                else:
                    rev = revision

                p = DBPatch(None, commit_id, self.get_patch_for_commit(rev))
                write_cursor.execute(statement(DBPatch.__insert__, self.db.place_holder),
                                     (p.id, p.commit_id, self.db.to_binary(p.patch)))

            rs = icursor.fetchmany()

        cnn.commit()
        write_cursor.close()
        cursor.close()
        cnn.close()


register_extension("Patches", Patches)
