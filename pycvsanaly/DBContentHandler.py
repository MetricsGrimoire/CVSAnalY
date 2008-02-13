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

class DBContentHandler (ContentHandler):

    def __init__ (self, db):
        ContentHandler.__init__ (self)

        self.db = db
        self.cnn = db.connect ()
        
        self.file_cache = {}
        self.commit_cache = None

    def __del__ (self):
        self.cnn.close ()

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
        
    def __ensure_path (self, path):
#        print "DBG: ensure_path %s" % (path)
        tokens = path.strip ('/').split ('/')

        cursor = self.cnn.cursor ()
        
        parent = -1
        node = None
        i = 1
        for token in tokens:
            rpath = '/' + '/'.join (tokens[:i])
#            print "DBG: rpath: %s" % (rpath)
            if self.file_cache.has_key (rpath):
                node = self.file_cache[rpath]
#                print "DBG: found %s in cache file_id = %d (%s)" % (rpath, node.id, node.file_name)
#                print "DBG: parent = %d" % (node.id)
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
#        print "DBG: path ensured %s = %d (%s)" % (path, node.id, node.file_name)
        
        return node

    def commit (self, commit):
        if commit.revision in self.__get_repository_commits ():
            return

        log = DBLog (None, commit)
        log.repository_id = self.repo_id
        cursor = self.cnn.cursor ()
        cursor.execute (statement (DBLog.__insert__, self.db.place_holder), (log.id, log.rev, log.committer, log.author, log.date, log.lines_added, log.lines_removed, log.message, log.composed_rev, log.repository_id))

#        print "DBG: commit: %d rev: %s" % (log.id, log.rev)
        renamed_from = None

        dbactions = []
        for action in commit.actions:
#            print "DBG: Action: %s" % (action.type)
            if action.f2 is not None:
                if self.file_cache.has_key (action.f1.path):
                    file = self.file_cache[action.f1.path]
#                    print "DBG: found %s in cache file_id = %d (%s)" % (action.f1.path, file.id, file.file_name)
                else:
                    file = self.__ensure_path (action.f1.path)

                # TODO: Replace actions!!!
                if action.type == 'V':
                    # Rename the node
                    self.file_cache[action.f2.path] = file
#                    print "DBG: update cache %s = %d (%s)" % (action.f2.path, file.id, file.file_name)
                else:
                    self.file_cache[action.f1.path] = file
#                    print "DBG: update cache %s = %d (%s)" % (action.f1.path, file.id, file.file_name)
            else:
                if self.file_cache.has_key (action.f1.path):
                    file = self.file_cache[action.f1.path]
#                    print "DBG: found %s in cache file_id = %d" % (action.f1.path, file.id)
                else:
                    file = self.__ensure_path (action.f1.path)
                    self.file_cache[action.f1.path] = file
#                    print "DBG: update cache %s = %d (%s)" % (action.f1.path, file.id, file.file_name)

            if action.type == 'D':
                file.deleted = True

            dbaction = DBAction (None, action.type)
            dbaction.commit_id = log.id
            dbaction.file_id = file.id
            dbactions.append ((dbaction.id, dbaction.type, dbaction.file_id, dbaction.commit_id))

        if dbactions:
            cursor.executemany (statement (DBAction.__insert__, self.db.place_holder), dbactions)
            
        cursor.close ()
        self.cnn.commit ()
            
        
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
