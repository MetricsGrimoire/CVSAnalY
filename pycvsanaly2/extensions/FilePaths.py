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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

if __name__ == '__main__':
    import sys

    sys.path.insert(0, "../../")

from pycvsanaly2.Database import statement
from pycvsanaly2.profile import profiler_start, profiler_stop


class FilePaths:
    class Adj:

        def __init__(self):
            self.files = {}
            self.adj = {}

    __shared_state = {'rev': None,
                      'adj': None,
                      'files': None,
                      'db': None}

    def __init__(self, db):
        self.__dict__ = self.__shared_state
        self.__dict__['db'] = db

    def update_for_revision(self, cursor, commit_id, repo_id):
        db = self.__dict__['db']

        if commit_id == self.__dict__['rev']:
            return

        prev_commit_id = self.__dict__['rev']
        self.__dict__['rev'] = commit_id

        profiler_start("Updating adjacency matrix for commit %d", (commit_id,))

        if self.__dict__['adj'] is None:
            adj = FilePaths.Adj()
            self.__dict__['adj'] = adj
        else:
            adj = self.__dict__['adj']

        rf = self.__dict__['files']
        if rf is not None:
            repo_files_id, repo_files = rf
            if repo_files_id != repo_id:
                del self.__dict__['files']
                repo_files = {}
        else:
            repo_files = {}

        if not repo_files:
            # Get and cache all the files table
            query = "select id, file_name from files where repository_id = ?"
            profiler_start("Getting files for repository %d", (repo_id,))
            cursor.execute(statement(query, db.place_holder), (repo_id,))
            profiler_stop("Getting files for repository %d", (repo_id,), True)
            rs = cursor.fetchmany()
            while rs:
                for id, file_name in rs:
                    repo_files[id] = file_name
                rs = cursor.fetchmany()
            self.__dict__['files'] = (repo_id, repo_files)
            adj.files = repo_files

        # Get the files that have been renamed
        # with the new name for the given rev
        query = "select af.file_id, af.new_file_name " + \
                "from actions_file_names af, files f " + \
                "where af.file_id = f.id " + \
                "and af.commit_id = ? " + \
                "and af.type = 'V' " + \
                "and f.repository_id = ?"
        profiler_start("Getting new file names for commit %d", (commit_id,))
        cursor.execute(statement(query, db.place_holder), (commit_id, repo_id))
        profiler_stop("Getting new file names for commit %d", (commit_id,), True)
        rs = cursor.fetchmany()
        while rs:
            for id, file_name in rs:
                adj.files[id] = file_name
            rs = cursor.fetchmany()

        # Get the new file links since the last time
        query = "select fl.parent_id, fl.file_id " + \
                "from file_links fl, files f " + \
                "where fl.file_id = f.id "
        if prev_commit_id is None:
            query += "and fl.commit_id = ? "
            args = (commit_id, repo_id)
        else:
            query += "and fl.commit_id between ? and ? "
            args = (prev_commit_id, commit_id, repo_id)
        query += "and f.repository_id = ?"
        profiler_start("Getting file links for commit %d", (commit_id,))
        cursor.execute(statement(query, db.place_holder), args)
        profiler_stop("Getting file links for commit %d", (commit_id,), True)
        rs = cursor.fetchmany()
        while rs:
            for f1, f2 in rs:
                adj.adj[f2] = f1
            rs = cursor.fetchmany()

        self.__dict__['adj'] = adj

        profiler_stop("Updating adjacency matrix for commit %d", (commit_id,), True)

    def __build_path(self, file_id, adj):
        if file_id not in adj.adj:
            return None

        profiler_start("Building path for file %d", (file_id,))

        tokens = []
        id = file_id

        while id != -1:
            tokens.insert(0, adj.files[id])
            id = adj.adj[id]

        profiler_stop("Building path for file %d", (file_id,), True)

        return "/" + "/".join(tokens)

    def get_path(self, file_id, commit_id, repo_id):
        profiler_start("Getting path for file %d at commit %d", (file_id, commit_id))

        adj = self.__dict__['adj']
        assert adj is not None, "Matrix no updated"

        path = self.__build_path(file_id, adj)

        profiler_stop("Getting path for file %d at commit %d", (file_id, commit_id), True)

        return path

    def get_filename(self, file_id):
        adj = self.__dict__['adj']
        assert adj is not None, "Matrix no updated"
        try:
            return adj.files[file_id]
        except KeyError:
            return None

    def get_commit_id(self):
        return self.__dict__['rev']


if __name__ == '__main__':
    import sys
    from pycvsanaly2.Database import create_database
    from pycvsanaly2.Config import Config

    db = create_database('sqlite', sys.argv[1])
    cnn = db.connect()

    fp = FilePaths(db)

    config = Config()
    config.profile = True

    cursor = cnn.cursor()
    cursor.execute("select s.id, file_id from scmlog s, actions a where s.id = a.commit_id")
    old_id = -1
    for id, file_id in cursor.fetchall():
        if old_id != id:
            print "Commit ", id
            fp.update_for_revision(cursor, id, 1)
            old_id = id
        print fp.get_path(file_id, id, 1)

    cursor.close()

    cnn.close()
