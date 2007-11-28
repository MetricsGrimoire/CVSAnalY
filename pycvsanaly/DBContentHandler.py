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
from CADatabase import *

class DBContentHandler (ContentHandler):

    def __init__ (self, db):
        ContentHandler.__init__ (self)

        self.store = db.get_store ()
        
        self.file_cache = {}
        self.commit_cache = None

    def repository (self, uri):
        repo = self.store.find (DBRepository, DBRepository.uri == unicode (uri)).one ()
        self.repo_id = repo.id

    def __get_repository_commits (self):
        # FIXME: this doesn't work for cvs
        if self.commit_cache is not None:
            return self.commit_cache

        res = self.store.find (DBLog, DBLog.repository_id == self.repo_id)
        self.commit_cache = [commit.rev for commit in res]

        return self.commit_cache
        
    def __ensure_path (self, path):
#        print "DBG: ensure_path %s" % (path)
        tokens = path.strip ('/').split ('/')

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
            
            node = self.store.find (DBFile,
                                    DBFile.file_name == unicode (token),
                                    DBFile.parent == parent).order_by (DBFile.id).last ()
            if node is None:
                node = self.store.add (DBFile (token, parent))
                self.store.flush ()
                
            parent = node.id
            i += 1

        assert node is not None

#        print "DBG: path ensured %s = %d (%s)" % (path, node.id, node.file_name)
        
        return node

    def commit (self, commit):
        if commit.revision in self.__get_repository_commits ():
            return
        
        log = self.store.add (DBLog (commit))
        log.repository_id = self.repo_id
        self.store.flush ()

#        print "DBG: commit: %d rev: %s" % (log.id, log.rev)
        renamed_from = None

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
                
            dbaction = self.store.add (DBAction (action.type))
            dbaction.commit_id = log.id
            dbaction.file_id = file.id
            self.store.flush ()

        self.store.commit ()
            
        
if __name__ == '__main__':
    import sys
    from ParserFactory import create_parser
    from libcvsanaly.Database import get_database

    p = create_parser (sys.argv[1])
    db = get_database ('sqlite', '/tmp/cvsanaly')
    db.connect ()
    db.create_tables ()
    p.set_content_handler (DBContentHandler (db))
    p.run ()
    db.close ()
