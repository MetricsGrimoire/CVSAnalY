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

if __name__ == '__main__':
    import sys
    sys.path.insert (0, "../../")

from pycvsanaly2.Database import statement
from pycvsanaly2.utils import to_utf8
from pycvsanaly2.profile import profiler_start, profiler_stop

class FilePaths:

    class Adj:

        def __init__ (self):
            self.files = {}
            self.adj = {}

    
    __shared_state = { 'rev' : None,
                       'adj' : None,
                       'db'  : None}

    def __init__ (self, db):
        self.__dict__ = self.__shared_state
        self.__dict__['db'] = db

    def __get_adj_for_revision (self, cursor, repo_id, commit_id):
        db = self.__dict__['db']

        profiler_start ("Getting adjacency matrix for commit %d", (commit_id,))
        
        adj = FilePaths.Adj ()

        query = "select files.id, files.file_name, new_file_name from files " + \
                "LEFT JOIN (select fv.file_id ffid, new_file_name " + \
                "from (select file_id, max(commit_id) md " + \
                "from actions_file_names where commit_id <= ? " + \
                "and type = 'V' group by file_id) fv, actions_file_names af " + \
                "where af.commit_id = fv.md and " + \
                "af.file_id = fv.file_id) new_names " + \
                "ON files.id = new_names.ffid and repository_id = ?"
        
        profiler_start ("Getting files for commit %d", (commit_id,))
        cursor.execute (statement (query, db.place_holder), (commit_id, repo_id))
        profiler_stop ("Getting files for commit %d", (commit_id,))
        rs = cursor.fetchmany ()
        files = {}
        while rs:
            for id, file_name, rev_name in rs:
                files[id] = rev_name or file_name
            rs = cursor.fetchmany ()
        adj.files = files

        query = "select file_links.parent_id, file_links.file_id " + \
                "from (select fl.file_id file_id, max(commit_id) md " + \
                "from file_links fl, files f " + \
                "where fl.file_id = f.id and f.repository_id = ? and " + \
                "fl.commit_id <= ? and fl.file_id not in " + \
                "(select file_id from actions where type in " + \
                "('D', 'R') and commit_id <= ?) group by fl.file_id) f, file_links " + \
                "where file_links.file_id = f.file_id and " + \
                "file_links.commit_id = f.md order by 1"

        profiler_start ("Getting file links for commit %d", (commit_id,))
        cursor.execute (statement (query, db.place_holder), (repo_id, commit_id, commit_id))
        profiler_stop ("Getting file links for commit %d", (commit_id,))
        rs = cursor.fetchmany ()
        adj_ = {}
        tops = []
        while rs:
            for f1, f2 in rs:
                adj_[f2] = f1
            rs = cursor.fetchmany ()
        adj.adj = adj_

        profiler_stop ("Getting adjacency matrix for commit %d", (commit_id,))

        return adj

    def __build_path (self, file_id, adj):
        if file_id not in adj.adj:
            return None

        profiler_start ("Building path for file %d", (file_id,))
        
        tokens = []
        id = file_id
        
        while id != -1:
            tokens.insert (0, adj.files[id])
            id = adj.adj[id]

        profiler_stop ("Building path for file %d", (file_id,))

        return "/" + "/".join (tokens)
    
    def get_path (self, cursor, file_id, commit_id, repo_id):
        db = self.__dict__['db']

        profiler_start ("Getting path for file %d at commit %d", (file_id, commit_id))

        if commit_id == self.__dict__['rev']:
            adj = self.__dict__['adj']
        else:
            del self.__dict__['adj']
            self.__dict__['rev'] = commit_id
            adj = self.__get_adj_for_revision (cursor, repo_id, commit_id)
            self.__dict__['adj'] = adj

        path = self.__build_path (file_id, adj)
        
        profiler_stop ("Getting path for file %d at commit %d", (file_id, commit_id))

        return path


if __name__ == '__main__':
    import sys
    from pycvsanaly2.Database import create_database
    from pycvsanaly2.Config import Config

    db = create_database ('sqlite', sys.argv[1])
    cnn = db.connect ()

    fp = FilePaths (db)

    config = Config ()
    config.profile = True

    cursor = cnn.cursor ()
    cursor.execute ("select s.id, file_id from scmlog s, actions a where s.id = a.commit_id")
    old_id = -1
    for id, file_id in cursor.fetchall ():
        if old_id != id:
            print "Commit ",id
            old_id = id
        print fp.get_path (cursor, file_id, id, 1)

    cursor.close ()
    
    cnn.close ()
