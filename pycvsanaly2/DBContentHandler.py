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

import os

from ContentHandler import ContentHandler
from Database import (DBRepository, DBLog, DBFile, DBFileLink, DBAction,
                      DBFileCopy, DBBranch, DBPerson, DBTag, DBTagRev,
                      statement)
from profile import profiler_start, profiler_stop
from utils import printdbg, printout, to_utf8

class FileNotInCache (Exception):
    '''File is not in Cache'''

class DBContentHandler (ContentHandler):

    MAX_ACTIONS = 100

    def __init__ (self, db):
        ContentHandler.__init__ (self)

        self.db = db
        self.cnn = None
        self.cursor = None
        
        self.file_cache = {}
        self.moves_cache = {}
        self.deletes_cache = {}
        self.revision_cache = {}
        self.branch_cache = {}
        self.tags_cache = {}
        self.people_cache = {}

    def __del__ (self):
        if self.cnn is not None:
            self.cnn.close ()

    def begin (self, order=None):
        self.cnn = self.db.connect ()

        self.cursor = self.cnn.cursor ()

        self.commits = []
        self.actions = []

    def repository (self, uri):
        cursor = self.cursor
        cursor.execute (statement ("SELECT id from repositories where uri = ?", self.db.place_holder), (uri,))
        self.repo_id = cursor.fetchone ()[0]

    def __insert_many (self):
        cursor = self.cursor

        if self.actions:
            actions = [(a.id, a.type, a.file_id, a.commit_id, a.branch_id) for a in self.actions]
            profiler_start ("Inserting actions for repository %d", (self.repo_id,))
            cursor.executemany (statement (DBAction.__insert__, self.db.place_holder), actions)
            self.actions = []
            profiler_stop ("Inserting actions for repository %d", (self.repo_id,))
        if self.commits:
            commits = [(c.id, c.rev, c.committer, c.author, c.date, c.message, c.composed_rev, c.repository_id) for c in self.commits]
            profiler_start ("Inserting commits for repository %d", (self.repo_id,))
            cursor.executemany (statement (DBLog.__insert__, self.db.place_holder), commits)
            self.commits = []
            profiler_stop ("Inserting commits for repository %d", (self.repo_id,))

        profiler_start ("Committing inserts for repository %d", (self.repo_id,))
        self.cnn.commit ()
        profiler_stop ("Committing inserts for repository %d", (self.repo_id,))
        
    def __add_new_file_and_link (self, file_name, parent_id, commit_id):
        dbfile = DBFile (None, file_name)
        dbfile.repository_id = self.repo_id
        self.cursor.execute (statement (DBFile.__insert__, self.db.place_holder), (dbfile.id, dbfile.file_name, dbfile.repository_id))
        
        dblink = DBFileLink (None, parent_id, dbfile.id)
        dblink.commit_id = commit_id
        self.cursor.execute (statement (DBFileLink.__insert__, self.db.place_holder), (dblink.id, dblink.parent, dblink.child, dblink.commit_id))

        return dbfile.id

    def __add_new_copy (self, dbfilecopy):
        self.cursor.execute (statement (DBFileCopy.__insert__, self.db.place_holder),
                             (dbfilecopy.id, dbfilecopy.to_id, dbfilecopy.from_id,
                              dbfilecopy.from_commit, dbfilecopy.new_file_name, dbfilecopy.action_id))

    def __ensure_person (self, person):
        profiler_start ("Ensuring person %s for repository %d", (person.name, self.repo_id))
        printdbg ("DBContentHandler: ensure_person %s <%s>", (person.name, person.email))
        cursor = self.cursor

        name = to_utf8 (person.name)
        email = person.email
        cursor.execute (statement ("SELECT id from people where name = ?", self.db.place_holder), (name,))
        rs = cursor.fetchone ()
        if not rs:
            p = DBPerson (None, person)
            cursor.execute (statement (DBPerson.__insert__, self.db.place_holder), (p.id, p.name, email))
            person_id = p.id
        else:
            person_id = rs[0]

        self.people_cache[name] = person_id

        profiler_stop ("Ensuring person %s for repository %d", (person.name, self.repo_id))

        return person_id

    def __ensure_branch (self, branch):
        profiler_start ("Ensuring branch %s for repository %d", (branch, self.repo_id))
        printdbg ("DBContentHandler: ensure_branch %s", (branch))
        cursor = self.cursor

        cursor.execute (statement ("SELECT id from branches where name = ?", self.db.place_holder), (branch,))
        rs = cursor.fetchone ()
        if not rs:
            b = DBBranch (None, branch)
            cursor.execute (statement (DBBranch.__insert__, self.db.place_holder), (b.id, b.name))
            branch_id = b.id
        else:
            branch_id = rs[0]
            
        self.branch_cache[branch] = branch_id
            
        profiler_stop ("Ensuring branch %s for repository %d", (branch, self.repo_id))

        return branch_id

    def __ensure_tag (self, tag):
        profiler_start ("Ensuring tag %s for repository %d", (tag, self.repo_id))
        printdbg ("DBContentHandler: ensure_tag %s", (tag))
        cursor = self.cursor

        cursor.execute (statement ("SELECT id from tags where name = ?", self.db.place_holder), (tag,))
        rs = cursor.fetchone ()
        if not rs:
            t = DBTag (None, tag)
            cursor.execute (statement (DBTag.__insert__, self.db.place_holder), (t.id, t.name))
            tag_id = t.id
        else:
            tag_id = rs[0]

        profiler_stop ("Ensuring tag %s for repository %d", (tag, self.repo_id))

        return tag_id

    def __move_path_to_deletes_cache (self, path):
        self.deletes_cache[path] = self.file_cache[path]
        del (self.file_cache[path])

    def __get_file_from_moves_cache (self, path):
        # Path is not in the cache, but it should
        # Look if any of its parents was moved
        current_path = path
        while current_path not in self.file_cache:
            found = False
            for new_path in self.moves_cache.keys ():
                if not current_path.startswith (new_path):
                    continue

                current_path = current_path.replace (new_path, self.moves_cache[new_path], 1)
                found = True
            
            if not found:
                raise FileNotInCache

        return self.file_cache[current_path]

    def __ensure_path (self, path, commit_id):
        profiler_start ("Ensuring path %s for repository %d", (path, self.repo_id))
        printdbg ("DBContentHandler: ensure_path %s", (path))
        tokens = path.strip ('/').split ('/')

        parent = -1
        node_id = None
        for i, token in enumerate (tokens):
            rpath = '/' + '/'.join (tokens[:i + 1])
            printdbg ("DBContentHandler: rpath: %s", (rpath,))
            try:
                node_id, parent_id = self.file_cache[rpath]
                parent = node_id
                
                continue
            except:
                pass

            # Rpath not in cache, add it
            node_id = self.__add_new_file_and_link (token, parent, commit_id)
            parent_id = parent
            parent = node_id

            self.file_cache[rpath] = (node_id, parent_id)

        assert node_id is not None

        printdbg ("DBContentHandler: path ensured %s = %d (%d)", (path, node_id, parent_id))
        profiler_stop ("Ensuring path %s for repository %d", (path, self.repo_id))

        return node_id, parent_id
            
    def __get_file_for_path (self, path, commit_id, old = False):
        printdbg ("DBContentHandler: Looking for path %s in cache", (path,))

        # First of all look at the cache
        try:
            return self.file_cache[path]
        except KeyError:
            pass
        
        # It's not in the cache look now at moves cache
        try:
            retval = self.__get_file_from_moves_cache (path)
            printdbg ("DBContentHandler: Found %s in moves cache", (path,))
            self.file_cache[path] = retval
            return retval
        except FileNotInCache:
            pass

        # If it's an old file (that is, the path has been
        # taken from the "from" part of an action that
        # has two paths) it might be deletes or replaced
        if old:
            try:
                return self.deletes_cache[path]
            except KeyError:
                pass
        
        # It hasen't been moved (or any of its parents)
        # so it was copied at some point
        return self.__ensure_path (path, commit_id)

    def commit (self, commit):
        profiler_start ("New commit %s for repository %d", (commit.revision, self.repo_id))
        
        log = DBLog (None, commit)
        log.repository_id = self.repo_id
        self.revision_cache[commit.revision] = log.id
                       
        committer = to_utf8 (commit.committer.name)
        author = commit.author is not None and to_utf8 (commit.author.name) or None
        
        if committer in self.people_cache:
            log.committer = self.people_cache[committer]
        else:
            log.committer = self.__ensure_person (commit.committer)

        if author == committer:
            log.author = log.committer
        elif author is not None:
            if author in self.people_cache:
                log.author = self.people_cache[author]
            else:
                log.author = self.__ensure_person (commit.author)

        self.commits.append (log)

        printdbg ("DBContentHandler: commit: %d rev: %s", (log.id, log.rev))

        # TODO: sort actions? R, A, D, M, V, C
        
        for action in commit.actions:
            printdbg ("DBContentHandler: Action: %s", (action.type))
            dbaction = DBAction (None, action.type)
            dbaction.commit_id = log.id

            if action.type == 'A':
                # New file
                path = action.f1
                parent_path = os.path.dirname (path)
                file_name = os.path.basename (path)

                if parent_path == '/':
                    parent_id = -1
                else:
                    parent_id = self.__get_file_for_path (parent_path, log.id)[0]

                file_id = self.__add_new_file_and_link (file_name, parent_id, log.id)
                self.file_cache[path] = (file_id, parent_id)
            elif action.type == 'M':
                file_id = self.__get_file_for_path (action.f1, log.id)[0]
            elif action.type == 'D':
                path = action.f1
                file_id = self.__get_file_for_path (path, log.id)[0]
                
                # Remove the old references
                dirpath = path.rstrip ("/") + "/"
                for cpath in self.file_cache.keys ():
                    if cpath.startswith (dirpath):
                        self.__move_path_to_deletes_cache (cpath)
                self.__move_path_to_deletes_cache (path)
            elif action.type == 'V':
                path = action.f1
                new_parent_path = os.path.dirname (path)
                new_file_name = os.path.basename (path)

                old_path = action.f2
                file_id, parent_id = self.__get_file_for_path (old_path, log.id, True)
                
                dbfilecopy = DBFileCopy (None, file_id)
                dbfilecopy.action_id = dbaction.id
                dbfilecopy.from_commit = self.revision_cache.get (action.rev, None)

                if new_parent_path == '/':
                    new_parent_id = -1
                else:
                    new_parent_id = self.__get_file_for_path (new_parent_path, log.id)[0]
                if new_parent_id != parent_id:
                    # It's not a simple rename, but a move operation
                    # we have to write down the new link
                    parent_id = new_parent_id
                    dblink = DBFileLink (None, parent_id, file_id)
                    dblink.commit_id = log.id
                    self.cursor.execute (statement (DBFileLink.__insert__, self.db.place_holder),
                                         (dblink.id, dblink.parent, dblink.child, dblink.commit_id))
                    self.moves_cache[path] = old_path
                    
                self.file_cache[path] = (file_id, parent_id)
                
                # Move/rename is a special case of copy. There's not a new file_id
                dbfilecopy.from_id = file_id
                dbfilecopy.new_file_name = new_file_name
                self.__add_new_copy (dbfilecopy)
            elif action.type == 'C':
                path = action.f1
                parent_path = os.path.dirname (path)
                file_name = os.path.basename (path)

                from_file_id = self.__get_file_for_path (action.f2, log.id, True)[0]
                
                if parent_path == '/':
                    parent_id = -1
                else:
                    parent_id = self.__get_file_for_path (parent_path, log.id)[0]
                    
                        
                file_id = self.__add_new_file_and_link (file_name, parent_id, log.id)
                self.file_cache[path] = (file_id, parent_id)

                dbfilecopy = DBFileCopy (None, file_id)
                dbfilecopy.from_id = from_file_id
                dbfilecopy.action_id = dbaction.id
                dbfilecopy.from_commit = self.revision_cache.get (action.rev, None)
                self.__add_new_copy (dbfilecopy)
            elif action.type == 'R':
                # Replace action: Path has been removed and
                # a new one has been added with the same path
                path = action.f1
                file_name = os.path.basename (path)

                # The replace action is over the old file_id
                file_id, parent_id = self.__get_file_for_path (path, log.id)
                self.__move_path_to_deletes_cache (path)
                
                if action.f2 is not None:
                    from_file_id = self.__get_file_for_path (action.f2, log.id, True)[0]
                else:
                    from_file_id = file_id
                    
                # Remove the old references
                dirpath = path.rstrip ("/") + "/"
                for cpath in self.file_cache.keys ():
                    if cpath.startswith (dirpath):
                        self.__move_path_to_deletes_cache (cpath)

                # Add the new path
                new_file_id = self.__add_new_file_and_link (file_name, parent_id, log.id)
                self.file_cache[path] = (new_file_id, parent_id)

                # Register the action in the copies table in order to
                # be able to know which file replaced this file
                dbfilecopy = DBFileCopy (None, new_file_id)
                dbfilecopy.from_id = from_file_id
                dbfilecopy.action_id = dbaction.id
                dbfilecopy.from_commit = self.revision_cache.get (action.rev, None)
                self.__add_new_copy (dbfilecopy)
            else:
                assert "Unknown action type %s" % (action.type)

            dbaction.file_id = file_id

            branch = commit.branch or action.branch
                    
            if branch in self.branch_cache:
                branch_id = self.branch_cache[branch]
            else:
                branch_id = self.__ensure_branch (branch)
                    
            dbaction.branch_id = branch_id
            
            self.actions.append (dbaction)

        # Tags
        if commit.tags is not None:
            tag_revs = []
            for tag in commit.tags:
                if tag in self.tags_cache:
                    tag_id = self.tags_cache[tag]
                else:
                    tag_id = self.__ensure_tag (tag)
                    
                db_tagrev = DBTagRev (None)
                tag_revs.append ((db_tagrev.id, tag_id, log.id))

            self.cursor.executemany (statement (DBTagRev.__insert__, self.db.place_holder), tag_revs)

        if len (self.actions) >= self.MAX_ACTIONS:
            printdbg ("DBContentHandler: %d actions inserting", (len (self.actions)))
            self.__insert_many ()

        profiler_stop ("New commit %s for repository %d", (commit.revision, self.repo_id))

    def end (self):
        # flush pending inserts
        printdbg ("DBContentHandler: flushing pending inserts")
        self.__insert_many ()
        self.cursor.close ()
        self.cnn.close ()
        self.cnn = None

if __name__ == '__main__':
    import sys
    from cStringIO import StringIO
    from cPickle import dump, load
    from Database import create_database, DBRepository

    uri = "http://svn.test-cvsanaly.org/svn/test"
    
    db = create_database ('mysql', 'dbcontenthandler', sys.argv[1], None, 'localhost')
    cnn = db.connect ()

    tables = ['actions', 'branches', 'file_copies', 'file_links', 'files',
              'people', 'repositories', 'scmlog', 'tag_revisions', 'tags']
    
    cursor = cnn.cursor ()
    for table in tables:
        query = "delete from %s" % (table)
        cursor.execute (statement (query, db.place_holder))
    cursor.close ()
    cnn.commit ()

    name = uri.rstrip ("/").split ("/")[-1].strip ()
    cursor = cnn.cursor ()
    rep = DBRepository (None, uri, name, 'svn')
    cursor.execute (statement (DBRepository.__insert__, db.place_holder), (rep.id, rep.uri, rep.name, rep.type))
    cursor.close ()
    cnn.commit ()
    
    ch = DBContentHandler (db)
    ch.begin ()
    ch.repository (uri)
    
    cursor = cnn.cursor ()

    i = 0
    while True:
        query = "SELECT object from _temp_log order by id desc limit %d, 100" % i
        i += 100
        cursor.execute (statement (query, db.place_holder))        
        rs = cursor.fetchmany ()
        if not rs:
            break

        while rs:
            for t in rs:
                obj = t[0]
                io = StringIO (obj)
                commit = load (io)
                io.close ()
                ch.commit (commit)
            
            rs = cursor.fetchmany ()
            
    ch.end ()
    cursor.close ()
    cnn.close ()


        
            
