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

from ContentHandler import ContentHandler
from Database import DBRepository, DBLog, DBFile, DBAction, DBBranch, DBPerson, statement
from profile import profiler_start, profiler_stop
from utils import printdbg

class DBContentHandler (ContentHandler):

    MAX_ACTIONS = 100

    def __init__ (self, db):
        ContentHandler.__init__ (self)

        self.db = db
        self.cnn = None
        
        self.file_cache = {}
        self.commit_cache = None
        self.branch_cache = {}
        self.heads_cache = None
        self.people_cache = {}

    def __del__ (self):
        if self.cnn is not None:
            self.cnn.close ()

    def begin (self):
        self.cnn = self.db.connect ()

        self.commits = []
        self.actions = []
        self.heads = {}

    def repository (self, uri):
        cursor = self.cnn.cursor ()
        cursor.execute (statement ("SELECT id from repositories where uri = ?", self.db.place_holder), (uri,))
        self.repo_id = cursor.fetchone ()[0]
        cursor.close ()

    def __get_repository_commits (self):
        if self.commit_cache is not None:
            return self.commit_cache

        profiler_start ("Getting commits for repository %d", (self.repo_id,))
        
        cursor = self.cnn.cursor ()
        cursor.execute (statement ("SELECT rev from scmlog where repository_id = ?", self.db.place_holder), (self.repo_id,))
        res = cursor.fetchall ()
        self.commit_cache = [rev[0] for rev in res]
        cursor.close ()

        profiler_stop ("Getting commits for repository %d", (self.repo_id,))
        
        return self.commit_cache

    def __get_heads (self):
        if self.heads_cache is not None:
            return self.heads_cache

        profiler_start ("Getting heads for repository %d", (self.repo_id,))
        
        cursor = self.cnn.cursor ()
        query =  "SELECT a.id, a.file_id, a.branch_id from actions a, scmlog s "
        query += "where a.commit_id = s.id and head and repository_id = ?"
        cursor.execute (statement (query, self.db.place_holder), (self.repo_id,))
        self.heads_cache = []
        for action_id, file_id, branch_id in cursor.fetchall ():
            self.heads_cache.append ((action_id, file_id, branch_id))
        cursor.close ()

        profiler_stop ("Getting heads for repository %d", (self.repo_id,))
        
        return self.heads_cache

    def __update_heads (self, cursor):
        heads = self.__get_heads ()

        if not heads:
            return

        profiler_start ("Updating heads for repository %d", (self.repo_id,))
        
        old_heads = []
        for action_id, file_id, branch_id in [item for item in heads]:
            if file_id in self.heads.get (branch_id, []):
                old_heads.append (action_id)
                heads.remove ((action_id, file_id, branch_id))

        if not old_heads:
            profiler_stop ("Updating heads for repository %d", (self.repo_id,))
            return
        
        query = "UPDATE actions set head = ? where id in ("
        query += ",".join (['?' for item in old_heads])
        query += ")"
        old_heads.insert (0, False)
        cursor.execute (statement (query, self.db.place_holder), (old_heads))

        profiler_stop ("Updating heads for repository %d", (self.repo_id,))

    def __insert_many (self):
        cursor = self.cnn.cursor ()

        # Update the heads before inserting actions
        self.__update_heads (cursor)
        
        if self.actions:
            profiler_start ("Inserting actions for repository %d", (self.repo_id,))
            cursor.executemany (statement (DBAction.__insert__, self.db.place_holder), self.actions)
            self.actions = []
            profiler_stop ("Inserting actions for repository %d", (self.repo_id,))
        if self.commits:
            profiler_start ("Inserting commits for repository %d", (self.repo_id,))
            cursor.executemany (statement (DBLog.__insert__, self.db.place_holder), self.commits)
            self.commits = []
            profiler_stop ("Inserting commits for repository %d", (self.repo_id,))

        profiler_start ("Committing inserts for repository %d", (self.repo_id,))
        cursor.close ()
        self.cnn.commit ()
        profiler_stop ("Committing inserts for repository %d", (self.repo_id,))
        
    def __ensure_path (self, path):
        profiler_start ("Ensuring path %s for repository %d", (path, self.repo_id))
        printdbg ("DBContentHandler: ensure_path %s", (path))
        tokens = path.strip ('/').split ('/')

        cursor = self.cnn.cursor ()
        
        parent = -1
        node = None
        for i, token in enumerate (tokens):
            rpath = '/' + '/'.join (tokens[:i + 1])
            printdbg ("DBContentHandler: rpath: %s", (rpath,))
            if rpath in self.file_cache:
                node_id = self.file_cache[rpath]
                printdbg ("DBContentHandler: found %s in cache file_id = %d", (rpath, node_id))
                printdbg ("DBContentHandler: parent = %d", (node_id))
                parent = node_id

                continue

            profiler_start ("Looking for path %s parent %d for repository %d", (token, parent, self.repo_id))
            cursor.execute (statement ("SELECT id from tree where file_name = ? AND parent = ? AND repository_id = ?", self.db.place_holder),
                            (token, parent, self.repo_id))
            rs = cursor.fetchone ()
            profiler_stop ("Looking for path %s parent %d for repository %d", (token, parent, self.repo_id))
            if not rs:
                node = DBFile (None, token, parent)
                node.repository_id = self.repo_id
                profiler_start ("Inserting path %s parent %d for repository %d", (token, parent, self.repo_id))
                cursor.execute (statement (DBFile.__insert__, self.db.place_holder), (node.id, node.parent, node.file_name, node.repository_id))
                profiler_stop ("Inserting path %s parent %d for repository %d", (token, parent, self.repo_id))
                self.file_cache[rpath] = node.id
                node_id = node.id
            else:
                node_id = rs[0]

            parent = node_id 

        assert node_id is not None

        cursor.close ()
        printdbg ("DBContentHandler: path ensured %s = %d", (path, node_id))
        profiler_stop ("Ensuring path %s for repository %d", (path, self.repo_id))
        
        return node_id

    def __ensure_person (self, person):
        profiler_start ("Ensuring person %s for repository %d", (person, self.repo_id))
        printdbg ("DBContentHandler: ensure_person %s", (person))
        cursor = self.cnn.cursor ()

        cursor.execute (statement ("SELECT id from people where name = ?", self.db.place_holder), (person,))
        rs = cursor.fetchone ()
        if not rs:
            p = DBPerson (None, person)
            cursor.execute (statement (DBPerson.__insert__, self.db.place_holder), (p.id, p.name))
            person_id = p.id
        else:
            person_id = rs[0]

        self.people_cache[person] = person_id

        cursor.close ()

        profiler_stop ("Ensuring person %s for repository %d", (person, self.repo_id))

        return person_id

    def __ensure_branch (self, branch):
        profiler_start ("Ensuring branch %s for repository %d", (branch, self.repo_id))
        printdbg ("DBContentHandler: ensure_branch %s", (branch))
        cursor = self.cnn.cursor ()

        cursor.execute (statement ("SELECT id from branches where name = ?", self.db.place_holder), (branch,))
        rs = cursor.fetchone ()
        if not rs:
            b = DBBranch (None, branch)
            cursor.execute (statement (DBBranch.__insert__, self.db.place_holder), (b.id, b.name))
            branch_id = b.id
        else:
            branch_id = rs[0]
            
        self.branch_cache[branch] = branch_id
            
        cursor.close ()

        profiler_stop ("Ensuring branch %s for repository %d", (branch, self.repo_id))

        return branch_id
    
    def commit (self, commit):
        if commit.revision in self.__get_repository_commits ():
            return

        profiler_start ("New commit %s for repository %d", (commit.revision, self.repo_id))
        
        log = DBLog (None, commit)
        log.repository_id = self.repo_id

        if log.committer in self.people_cache:
            committer = self.people_cache[log.committer]
        else:
            committer = self.__ensure_person (log.committer)

        if log.author == log.committer:
            author = committer
        elif log.author is not None:
            if log.author in self.people_cache:
                author = self.people_cache[log.author]
            else:
                author = self.__ensure_person (log.author)
        else:
            author = None
            
        self.commits.append ((log.id, log.rev, committer, author, log.date,
                              log.lines_added, log.lines_removed, log.message,
                              log.composed_rev, log.repository_id))

        printdbg ("DBContentHandler: commit: %d rev: %s", (log.id, log.rev))
        renamed_from = None
        
        for action in commit.actions:
            printdbg ("DBContentHandler: Action: %s", (action.type))
            dbaction = DBAction (None, action.type)

            if action.f2 is not None:
                if action.f1.path in self.file_cache:
                    file_id = self.file_cache[action.f1.path]
                    printdbg ("DBContentHandler: found %s in cache file_id = %d", (action.f1.path, file_id))
                else:
                    file_id = self.__ensure_path (action.f1.path)

                # TODO: Replace actions!!!
                if action.type == 'V':
                    # Rename the node
                    self.file_cache[action.f2.path] = file_id
                    dbaction.old_path = action.f2.path
                    printdbg ("DBContentHandler: update cache %s = %d", (action.f2.path, file_id))
                else:
                    self.file_cache[action.f1.path] = file_id
                    printdbg ("DBContentHandler: update cache %s = %d", (action.f1.path, file_id))
            else:
                if action.f1.path in self.file_cache:
                    file_id = self.file_cache[action.f1.path]
                    printdbg ("DBContentHandler: found %s in cache file_id = %d", (action.f1.path, file_id))
                else:
                    file_id = self.__ensure_path (action.f1.path)
                    self.file_cache[action.f1.path] = file_id
                    printdbg ("DBContentHandler: update cache %s = %d", (action.f1.path, file_id))

            if action.branch in self.branch_cache:
                branch_id = self.branch_cache[action.branch]
            else:
                branch_id = self.__ensure_branch (action.branch)

            if branch_id not in self.heads:
                self.heads[branch_id] = [file_id]
                dbaction.head = True
            else:
                if file_id not in self.heads[branch_id]:
                    self.heads[branch_id].append (file_id)
                    dbaction.head = True
                
            dbaction.commit_id = log.id
            dbaction.file_id = file_id
            dbaction.branch_id = branch_id

            self.actions.append ((dbaction.id, dbaction.type, dbaction.file_id, dbaction.old_path,
                                  dbaction.commit_id, dbaction.branch_id, dbaction.head))

        if len (self.actions) >= self.MAX_ACTIONS:
            printdbg ("DBContentHandler: %d actions inserting", (len (self.actions)))
            self.__insert_many ()

        profiler_stop ("New commit %s for repository %d", (commit.revision, self.repo_id))
            
    def end (self):
        # flush pending inserts
        printdbg ("DBContentHandler: flushing pensing inserts")
        self.__insert_many ()
        self.cnn.close ()
        self.cnn = None
            
        
if __name__ == '__main__':
    import sys
    from ParserFactory import create_parser
    from Database import create_database

    p = create_parser (sys.argv[1])
    db = create_database ('sqlite', '/tmp/cvsanaly')
    cnn = db.connect ()
    cursor = cnn.cursor ()
    db.create_tables (cursor)
    cursor.close ()
    p.set_content_handler (DBContentHandler (cnn))
    p.run ()
    cnn.close ()
