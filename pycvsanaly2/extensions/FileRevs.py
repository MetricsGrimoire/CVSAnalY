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
#       Carlos Garcia Campos  <carlosgc@libresoft.es>

from pycvsanaly2.Database import statement, ICursor
from FilePaths import FilePaths

if __name__ == '__main__':
    import sys
    sys.path.insert (0, "../../")

class FileRevs:

    INTERVAL_SIZE = 1000
    __query__ = '''select s.rev rev, s.id commit_id, af.file_id, af.action_type, s.composed_rev 
from scmlog s, action_files af where s.id = af.commit_id and s.repository_id = ? order by s.id'''

    def __init__ (self, db, cnn, cursor, repoid):
        self.db = db
        self.cnn = cnn
        self.repoid = repoid

        self.icursor = ICursor (cursor, self.INTERVAL_SIZE)
        self.icursor.execute (statement (self.__query__, db.place_holder), (repoid,))
        self.rs = iter (self.icursor.fetchmany ())
        self.prev_commit = -1
        self.current = None

        self.fp = FilePaths (db)

    def __iter__ (self):
        return self

    def __get_next (self):
        try:
            t = self.rs.next ()
        except StopIteration:
            self.rs = iter (self.icursor.fetchmany ())
            if not self.rs:
                raise StopIteration
            t = self.rs.next ()

        return t

    def next (self):
        if not self.rs:
            raise StopIteration

        while True:
            self.current = self.__get_next ()
            revision, commit_id, file_id, action_type, composed = self.current

            if action_type in ('V', 'C'):
                if self.prev_commit != commit_id:
                    # Get the matrix for revision
                    self.prev_commit = commit_id
                    aux_cursor = self.cnn.cursor ()
                    self.fp.update_for_revision (aux_cursor, commit_id, self.repoid)
                    aux_cursor.close ()
                    continue
            elif action_type == 'D':
                continue
            elif action_type in  ('A', 'R'):
                if self.prev_commit != commit_id:
                    # Get the matrix for revision
                    self.prev_commit = commit_id
                    aux_cursor = self.cnn.cursor ()
                    self.fp.update_for_revision (aux_cursor, commit_id, self.repoid)
                    aux_cursor.close ()

            return self.current

    def get_path (self):
        if not self.current:
            return None

        revision, commit_id, file_id, action_type, composed = self.current
        if composed:
            rev = revision.split ("|")[0]
        else:
            rev = revision

        try:
            relative_path = self.fp.get_path (file_id, commit_id, self.repoid).strip ("/")
        except AttributeError, e:
            if self.fp.get_commit_id () != commit_id:
                aux_cursor = self.cnn.cursor ()
                self.fp.update_for_revision (aux_cursor, commit_id, self.repoid)
                aux_cursor.close ()

                relative_path = self.fp.get_path (file_id, commit_id, self.repoid).strip ("/")
            else:
                raise e

        return relative_path

if __name__ == '__main__':
    import sys
    from pycvsanaly2.Database import create_database
    from pycvsanaly2.Config import Config

    config = Config ()
    config.load ()
    db = create_database (config.db_driver, sys.argv[1], config.db_user, config.db_password, config.db_hostname)
    cnn = db.connect ()
    cursor = cnn.cursor ()

    fr = FileRevs (db, cnn, cursor, 1)
    for revision, commit_id, file_id, action_type, composed in fr:
        print revision, commit_id, action_type, fr.get_path ()

    cursor.close ()
    cnn.close ()
