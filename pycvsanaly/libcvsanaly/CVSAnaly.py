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

from Database import *
from storm.locals import *
import datetime

# Simple reports
# Number of commits
## Per author
## Per file

# TODO
# Age of the repo
# Commits per year
# Commits per month
# Commits per day
#
# Implement time intervals too (i.e. number of commits per committer last month)

class IntervalTime:

    MINUTE = 60
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    MONTH = 30 * DAY
    YEAR = 365 * DAY
    
    def __init__ (self, first, last = None, step = None):
        self.__dict__ = { 'first'    : first,
                          'last'     : last,
                          'step'     : step,
                          '_current' : first}

        
        if last is None:
            self.__dict__['last'] = datetime.datetime.now ()
            
        if step is None:
            self.__dict__['step'] = self.DAY

    def __getattr__ (self, name):
        return self.__dict__[name]
    
    def __iter__ (self):
        return self

    def next (self):
        if self._current == self.last:
            self.__dict__['_current'] = self.first
            raise StopIteration

        first = self._current
        nxt = datetime.datetime.fromtimestamp (int (self._current.strftime ("%s")) + self.step)
        self.__dict__['_current'] = min (nxt, self.last)

        return IntervalTime (first, nxt)
    

class CVSAnaly:

    def __init__ (self, db):
        self.store = db.get_store ()

        self.include_deleted = False
        
        self.cache = {}

    def __get_repository_ids (self, reps):
        rs = self.store.find (DBRepository,
                              Or (DBRepository.uri.is_in (reps), DBRepository.name.is_in (reps))).values (DBRepository.id)
        return [id for id in rs]

    def __has_authors (self):
        return self.store.find (DBLog).count (DBLog.author) != 0
        
    def n_commits (self, intval = None, reps = []):
        '''Number of commits'''

        reps = self.__get_repository_ids (reps)

        if intval is not None and len (reps) > 0:
            n_commits = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps),
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last).count ()
        elif intval is not None:
            n_commits = self.store.find (DBLog,
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last).count ()
        elif len (reps) > 0:
            n_commits = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps)).count ()
        else:
            n_commits = self.store.find (DBLog).count ()

        return n_commits

    def n_committers (self, intval = None, reps = []):
        '''Number of committers'''

        reps = self.__get_repository_ids (reps)
        
        if intval is not None and len (reps) > 0:
            n_committers = self.store.find (DBLog,
                                            DBLog.repository_id.is_in (reps),
                                            DBLog.date >= intval.first,
                                            DBLog.date <= intval.last).count (DBLog.committer, distinct=True)
        elif intval is not None:
            n_committers = self.store.find (DBLog,
                                            DBLog.date >= intval.first,
                                            DBLog.date <= intval.last).count (DBLog.committer, distinct=True)
        elif len (reps) > 0:
            n_committers = self.store.find (DBLog,
                                            DBLog.repository_id.is_in (reps)).count (DBLog.committer, distinct=True)
        else:
            n_committers = self.store.find (DBLog).count (DBLog.committer, distinct=True)
        
        return n_committers

    def n_authors (self, intval = None, reps = []):
        '''Number of authors'''

        reps = self.__get_repository_ids (reps)

        if intval is not None and len (reps) > 0:
            n_authors = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps),
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last).count (DBLog.author, distinct=True)
        elif intval is not None:
            n_authors = self.store.find (DBLog,
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last).count (DBLog.author, distinct=True)
        elif len (reps) > 0:
            n_authors = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps)).count (DBLog.author, distinct=True)
        else:
            n_authors = self.store.find (DBLog).count (DBLog.author, distinct=True)

        return n_authors

    def n_paths (self, deleted = False, intval = None, reps = []):
        '''Number of paths'''

        if deleted == self.include_deleted and self.cache.has_key ("n-paths"):
            return self.cache["n-paths"]

        n_paths = len (self.paths (deleted))
        self.cache["n-paths"] = n_paths

        self.include_deleted = deleted

        return n_paths

    def repository_interval_time (self, reps = []):
        '''Interval time from first commit to last commit'''

        if self.cache.has_key ("intval-time"):
            return self.cache["intval-time"]

        rs = self.store.find (DBLog).order_by (Desc (DBLog.id))

        retval = IntervalTime (rs.first ().date, rs.last ().date)
        self.cache["intval-time"] = retval

        return retval
        
    def __get_committers (self, intval = None, reps = []):
        # reps should already contain the ids

        if intval is not None and len (reps) > 0:
            rs = self.store.find (DBLog,
                                  DBLog.repository_id.is_in (reps),
                                  DBLog.date >= intval.first,
                                  DBLog.date <= intval.last).config (distinct=True).values (DBLog.committer)
        elif intval is not None:
            rs = self.store.find (DBLog,
                                  DBLog.date >= intval.first,
                                  DBLog.date <= intval.last).config (distinct=True).values (DBLog.committer)
        elif len (reps) > 0:
            rs = self.store.find (DBLog,
                                  DBLog.repository_id.is_in (reps)).config (distinct=True).values (DBLog.committer)
        else:
            rs = self.store.find (DBLog).config (distinct=True).values (DBLog.committer)

        return [committer for committer in rs]

    def committers (self, intval = None, reps = []):
        '''List of committers'''

        reps = self.__get_repository_ids (reps)
        return self.__get_committers (intval, reps)

    def __get_commits_for_committer (self, committer, intval, reps):
        # reps should already contain the ids

        if intval is not None and len (reps) > 0:
            n_commits = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps),
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last,
                                         DBLog.committer == committer).count ()
        elif intval is not None:
            n_commits = self.store.find (DBLog,
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last,
                                         DBLog.committer == committer).count ()
        elif len (reps) > 0:
            n_commits = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps),
                                         DBLog.committer == committer).count ()
        else:
            n_commits = self.store.find (DBLog, DBLog.committer == committer).count ()

        return n_commits
                                         
    def n_commits_per_committer (self, intval = None, reps = []):
        '''Number of commits per committer. It returns a
        list of tuples [(committer, n_commits)] ordered by n_commits.
        '''

        reps = self.__get_repository_ids (reps)
        
        retval = []
        for committer in self.__get_committers (intval, reps):
            n_commits = self.__get_commits_for_committer (committer, intval, reps)
            retval.append ((committer, n_commits))

        retval.sort (cmp=lambda x,y: y[1]-x[1])
        return retval

    def __get_authors (self, intval = None, reps = []):
        # reps should already contain the ids
        
        if intval is not None and len (reps) > 0:
            rs = self.store.find (DBLog,
                                  DBLog.repository_id.is_in (reps),
                                  DBLog.date >= intval.first,
                                  DBLog.date <= intval.last).config (distinct=True).values (DBLog.author)
        elif intval is not None:
            rs = self.store.find (DBLog,
                                  DBLog.date >= intval.first,
                                  DBLog.date <= intval.last).config (distinct=True).values (DBLog.author)
        elif len (reps) > 0:
            rs = self.store.find (DBLog,
                                  DBLog.repository_id.is_in (reps)).config (distinct=True).values (DBLog.author)
        else:
            rs = self.store.find (DBLog).config (distinct=True).values (DBLog.author)

        return [author for author in rs]

    def authors (self, intval = None, reps = []):
        '''List of committers'''

        reps = self.__get_repository_ids (reps)
        return self.__get_authors (intval, reps)

    def __get_commits_for_author (self, author, intval, reps):
        # reps should already contain the ids

        if intval is not None and len (reps) > 0:
            n_commits = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps),
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last,
                                         DBLog.author == author).count ()
        elif intval is not None:
            n_commits = self.store.find (DBLog,
                                         DBLog.date >= intval.first,
                                         DBLog.date <= intval.last,
                                         DBLog.author == author).count ()
        elif len (reps) > 0:
            n_commits = self.store.find (DBLog,
                                         DBLog.repository_id.is_in (reps),
                                         DBLog.author == author).count ()
        else:
            n_commits = self.store.find (DBLog, DBLog.author == author).count ()

        return n_commits
                                         
    def n_commits_per_author (self, intval = None, reps = []):
        '''Number of commits per author. It returns a
        list of tuples [(author, n_commits)] ordered by n_commits.
        '''

        reps = self.__get_repository_ids (reps)
        
        retval = []
        for author in self.__get_authors (intval, reps):
            n_commits = self.__get_commits_for_author (author, intval, reps)
            retval.append ((author, n_commits))

        retval.sort (cmp=lambda x,y: y[1]-x[1])
        return retval    

    @staticmethod
    def _get_path_from_id (store, file_id, deleted = False):
        retval = []

        def build_path (store, node):
            if node is None or node.id == -1:
                return True

            if not deleted and node.deleted:
                return False
            
            retval.insert (0, node.file_name)
            return build_path (store, store.find (DBFile, DBFile.id == node.parent).one ())

        node = store.get (DBFile, file_id)
        assert node

        if build_path (store, node):
            return '/'.join (retval)

        return None
    
    def paths (self, deleted = False, intval = None, reps = []):
        '''List fo paths'''

        if deleted == self.include_deleted and self.cache.has_key ("paths"):
            return [item[0] for item in self.cache["paths"]]

        retval = []
        
        actions = self.store.find (DBAction).config (distinct=True).values (DBAction.file_id)
        for file_id in actions:
            # Do not include deleted paths
            if not deleted and self.store.get (DBFile, file_id).deleted:
                continue
            
            path = CVSAnaly._get_path_from_id (self.store, file_id, deleted)
            if path is None:
                # Deleted path
                continue
            
            retval.append ((path, file_id))

        self.cache["paths"] = retval

        self.include_deleted = deleted

        return [item[0] for item in retval]

    def n_commits_per_path (self, intval = None, reps = []):
        '''Number of commits per path.It returns a
        list of tuples [(path, n_commits)] ordered by n_commits.
        '''

        retval = []
        if not self.cache.has_key ("paths") or self.include_deleted:
            self.paths ()
            
        for path, id in self.cache["paths"]:
            n_commits = self.store.find (DBAction,
                                         DBAction.file_id == id).count ()
            retval.append ((path, n_commits))

        retval.sort (cmp=lambda x,y: y[1]-x[1])
        return retval

    def committers_per_path (self, intval = None, reps = []):
        '''Committer per path. It returns a list of tuples
        [(path, [committers])]'''

        retval = []
        
        if not self.cache.has_key ("paths") or self.include_deleted:
            self.paths ()

        for path, id in self.cache["paths"]:
            committers = self.store.find (DBLog,
                                          DBAction.commit_id == DBLog.id,
                                          DBAction.file_id == id).config (distinct=True).values (DBLog.committer)
            retval.append ((path, [committer for committer in committers]))

        return retval
    
    def n_committers_per_path (self, intval = None, reps = []):
        '''Committer per path. It returns a list of tuples
        [(path, n_committers)] order by n_committers'''

        retval = []
        
        rs = self.committers_per_path ()
        for path, committers in rs:
            retval.append ((path, len (committers)))

        retval.sort (cmp=lambda x,y: y[1]-x[1])
        return retval

    def paths_per_committer (self, intval = None, reps = []):
        '''Paths perl committer. It returns a list of tuples
        [(committer, [paths])]'''

        retval = []

        committers = self.committers ()
        for committer in committers:
            paths = self.store.find (DBFile,
                                     DBFile.id == DBAction.file_id,
                                     DBLog.id == DBAction.commit_id,
                                     DBLog.committer == unicode (committer)).config (distinct=True).values (DBFile.id)
            path_list = []
            for path_id in paths:
                path = CVSAnaly._get_path_from_id (self.store, path_id, True)
                if path is None:
                    continue
                
                path_list.append (path)
                
            retval.append ((committer, path_list))

        return retval

    def n_paths_per_committer (self, intval = None, reps = []):
        '''Numnber of paths per committer. It returns a list of tuples
        [(committer, n_paths)] order by n_paths'''

        retval = []

        rs = self.paths_per_committer ()
        for committer, paths in rs:
            retval.append ((committer, len (paths)))

        retval.sort (cmp=lambda x,y: y[1]-x[1])
        return retval

            
if __name__ == '__main__':
    import sys

    db = get_database ('sqlite', sys.argv[1])
    db.connect ()
    ca = CVSAnaly (db)
    print "First commit: %s" % (str (ca.repository_interval_time ().first))
    print "Last commit: %s" % (str (ca.repository_interval_time ().last))

    it = IntervalTime (ca.repository_interval_time ().first, ca.repository_interval_time ().last)
    for t in it:
        print "%s - %s" % (str (t.first), str (t.last))

    reps = []
    if len (sys.argv) > 2:
        for arg in sys.argv[2:]:
            reps.append (unicode (arg))
            

    print "Number of commits: %d" % (ca.n_commits (None, reps))
    print "Number of committers: %d" % (ca.n_committers (None, reps))
    n_authors = ca.n_authors (None, reps)
    print "Number of authors: %d" % (n_authors)
#    print "Number of paths: %d" % (ca.n_paths ())
#    print "Number of paths (including deleted): %d" % (ca.n_paths (True))
    print "Committers:"
    print ca.committers (None, reps)
    print "Commits per Committer:"
    print ca.n_commits_per_committer (None, reps)
    if n_authors > 0:
        print "Authors:"
        print ca.authors (None, reps)
        print "Commits per Author:"
        print ca.n_commits_per_author (None, reps)
    sys.exit (0)
    print ca.paths ()
    print ca.n_commits_per_path ()
    print ca.n_committers_per_path ()
    print ca.committers_per_path ()
    print ca.paths_per_committer ()
    print ca.n_paths_per_committer ()
        
    db.close ()
