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
from Database import DBRepository, DBLog, DBFile, DBAction, statement
from profile import plog
from utils import printdbg

class DBContentHandler (ContentHandler):

    MAX_ACTIONS = 100

    def __init__ (self, db):
        ContentHandler.__init__ (self)

        self.db = db
        self.cnn = None
        
        self.file_cache = {}
        self.commit_cache = None

    def __del__ (self):
        if self.cnn is not None:
            self.cnn.close ()

    def begin (self):
        self.cnn = self.db.connect ()

        self.commits = []
        self.actions = []

    def repository (self, uri):
        cursor = self.cnn.cursor ()
        cursor.execute (statement ("SELECT id from repositories where uri = ?", self.db.place_holder), (uri,))
        self.repo_id = cursor.fetchone ()[0]
        cursor.close ()

    def __get_repository_commits (self):
        if self.commit_cache is not None:
            return self.commit_cache

        cursor = self.cnn.cursor ()
        cursor.execute (statement ("SELECT rev from scmlog where repository_id = ?", self.db.place_holder), (self.repo_id,))
        res = cursor.fetchall ()
        self.commit_cache = [rev[0] for rev in res]
        cursor.close ()

        return self.commit_cache

    def __insert_many (self):
        cursor = self.cnn.cursor ()

        if self.actions:
            cursor.executemany (statement (DBAction.__insert__, self.db.place_holder), self.actions)
            self.actions = []
        if self.commits:
            cursor.executemany (statement (DBLog.__insert__, self.db.place_holder), self.commits)
            self.commits = []

        cursor.close ()
        self.cnn.commit ()        
        
    def __ensure_path (self, path):
        printdbg ("DBContentHandler: ensure_path %s" % (path))
        tokens = path.strip ('/').split ('/')

        cursor = self.cnn.cursor ()
        
        parent = -1
        node = None
        i = 1
        for token in tokens:
            rpath = '/' + '/'.join (tokens[:i])
            printdbg ("DBContentHandler: rpath: %s" % (rpath))
            if self.file_cache.has_key (rpath):
                node = self.file_cache[rpath]
                printdbg ("DBContentHandler: found %s in cache file_id = %d (%s)" % (rpath, node.id, node.file_name))
                printdbg ("DBContentHandler: parent = %d" % (node.id))
                parent = node.id
                i += 1

                continue

            cursor.execute (statement ("SELECT * from tree where file_name = ? AND parent = ? order by id", self.db.place_holder), (token, parent))
            rs = cursor.fetchall ()
            if not rs:
                node = DBFile (None, token, parent)
                cursor.execute (statement (DBFile.__insert__, self.db.place_holder), (node.id, node.parent, node.file_name, node.deleted))
                self.file_cache[rpath] = node
            else:
                node = DBFile (rs[-1][0], rs[-1][2], rs[-1][1], rs[-1][3]) 

            parent = node.id 
            i += 1

        assert node is not None

        cursor.close ()
        printdbg ("DBContentHandler: path ensured %s = %d (%s)" % (path, node.id, node.file_name))
        
        return node

    def commit (self, commit):
        if commit.revision in self.__get_repository_commits ():
            return

        log = DBLog (None, commit)
        log.repository_id = self.repo_id
        self.commits.append ((log.id, log.rev, log.committer, log.author, log.date, log.lines_added, log.lines_removed, log.message, log.composed_rev, log.repository_id))

        printdbg ("DBContentHandler: commit: %d rev: %s" % (log.id, log.rev))
        renamed_from = None

        for action in commit.actions:
            printdbg ("DBContentHandler: Action: %s" % (action.type))
            if action.f2 is not None:
                if self.file_cache.has_key (action.f1.path):
                    file = self.file_cache[action.f1.path]
                    printdbg ("DBContentHandler: found %s in cache file_id = %d (%s)" % (action.f1.path, file.id, file.file_name))
                else:
                    file = self.__ensure_path (action.f1.path)

                # TODO: Replace actions!!!
                if action.type == 'V':
                    # Rename the node
                    self.file_cache[action.f2.path] = file
                    printdbg ("DBContentHandler: update cache %s = %d (%s)" % (action.f2.path, file.id, file.file_name))
                else:
                    self.file_cache[action.f1.path] = file
                    printdbg ("DBContentHandler: update cache %s = %d (%s)" % (action.f1.path, file.id, file.file_name))
            else:
                if self.file_cache.has_key (action.f1.path):
                    file = self.file_cache[action.f1.path]
                    printdbg ("DBContentHandler: found %s in cache file_id = %d" % (action.f1.path, file.id))
                else:
                    file = self.__ensure_path (action.f1.path)
                    self.file_cache[action.f1.path] = file
                    printdbg ("DBContentHandler: update cache %s = %d (%s)" % (action.f1.path, file.id, file.file_name))

            if action.type == 'D':
                file.deleted = True

            dbaction = DBAction (None, action.type)
            dbaction.commit_id = log.id
            dbaction.file_id = file.id
            self.actions.append ((dbaction.id, dbaction.type, dbaction.file_id, dbaction.commit_id))

        if len (self.actions) >= self.MAX_ACTIONS:
            self.__insert_many ()
            
    def end (self):
        # flush pending inserts
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
