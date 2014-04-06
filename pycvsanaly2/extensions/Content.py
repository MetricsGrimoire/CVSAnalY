# Copyright(C) 2010 University of California, Santa Cruz
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.
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
#       Chris Lewis <cflewis@soe.ucsc.edu>
#       Zhongpeng Lin <linzhp@soe.ucsc.edu>

from pycvsanaly2.extensions import Extension, register_extension, \
    ExtensionRunError
from pycvsanaly2.Database import SqliteDatabase, MysqlDatabase, statement
from pycvsanaly2.utils import printdbg, printerr, uri_to_filename, to_unicode
from pycvsanaly2.profile import profiler_start, profiler_stop
from FileRevs import FileRevs
from repositoryhandler.backends import RepositoryCommandError
from repositoryhandler.backends.watchers import CAT, SIZE
from Jobs import JobPool, Job
from io import BytesIO
import os
import traceback


# This class holds a single repository retrieve task,
# and keeps the source code until the object is garbage-collected
class ContentJob(Job):
    def __init__(self, commit_id, file_id, rev, path):
        self.commit_id = commit_id
        self.file_id = file_id
        self.rev = rev
        self.path = path
        self._file_contents = ""
        self.file_size = None

    def run(self, repo, repo_uri):
        self.repo = repo
        self.repo_uri = repo_uri
        self.repo_type = self.repo.get_type()

        if self.repo_type == 'cvs':
            # CVS self.paths contain the module stuff
            uri = self.repo.get_uri_for_self.path(self.repo_uri)
            module = uri[len(self.repo.get_uri()):].strip('/')

            if module != '.':
                self.path = self.path[len(module):].strip('/')
            else:
                self.path = self.path.strip('/')
        else:
            self.path = self.path.strip('/')

        suffix = ''
        filename = os.path.basename(self.path)
        ext_ptr = filename.rfind('.')
        if ext_ptr != -1:
            suffix = filename[ext_ptr:]
            
        self._file_contents = self.listen_for_data(self.repo.cat, CAT)
        
        try:
            self.file_size = self.listen_for_data(self.repo.size, SIZE)
        except NotImplementedError:
            self.file_size = None
        
        if self.file_size:
            self.file_size = int(self.file_size)
            
    def listen_for_data(self, repo_func, watcher):
        def write_line(data, io):
            io.write(data)
        
        io = BytesIO()

        wid = self.repo.add_watch(watcher, write_line, io)
        
        # Git doesn't need retries because all of the revisions
        # are already on disk
        if self.repo_type == 'git':
            retries = 0
        else:
            retries = 3
            
        done = False
        failed = False
        # Try downloading the file revision
        while not done and not failed:
            try:
                repo_func(os.path.join(self.repo_uri, self.path), self.rev)
                done = True
            except RepositoryCommandError, e:
                if retries > 0:
                    printerr("Command %s returned %d(%s), try again",
                            (e.cmd, e.returncode, e.error))
                    retries -= 1
                    io.seek(0)
                elif retries == 0:
                    failed = True
                    printerr("Error obtaining %s@%s. " +
                             "Command %s returned %d(%s)",
                             (self.path, self.rev, e.cmd,
                             e.returncode, e.error))
            except:
                failed = True
                printerr("Error obtaining %s@%s.",
                        (self.path, self.rev))
                traceback.print_exc()
                
        self.repo.remove_watch(watcher, wid)
        
        results = None
        if not failed:
            try:
                results = io.getvalue()
            except Exception, e:
                printerr("Error getting contents." +
                         "Exception: %s", (str(e),))
            finally:
                io.close()
        return results
                
    def _get_file_contents(self):
            """Returns contents of the file, stripped of whitespace 
            at either end
            """
            # An encode will fail if the source code can't be converted to
            # unicode, ie. it's not already utf-8, or latin-1, or something
            # obvious. This almost always means that the file isn't source
            # code at all. 
            return to_unicode(self._file_contents)

    def _set_file_contents(self, contents):
        self._file_contents = contents
        
    def _get_number_of_lines(self):
        """Return the number of lines contained within the file, stripped
        of whitespace at either end.

        # Note that it looks like doctest doesn't work with properties,
        # depending on what your doctest runner is. That's why
        # it accesses the setter. There's no need to do this in your code.
        >>> cj = ContentJob(None, None, None, None)
        >>> cj._set_file_contents("Hello")
        >>> cj.file_number_of_lines
        1
        >>> cj._set_file_contents("Hello \\n world")
        >>> cj.file_number_of_lines
        2
        >>> cj._set_file_contents("")
        >>> cj.file_number_of_lines
        0
        >>> cj._set_file_contents(None)
        >>> cj.file_number_of_lines

        >>> cj._set_file_contents("\\n\\n Hello \\n\\n")
        >>> cj.file_number_of_lines
        1

        >>> cj._set_file_contents("a\\nb")
        >>> cj.file_number_of_lines
        2

        >>> cj._set_file_contents("a\\nb\\nc\\nd\\nea\\nb\\nc\\nd\\ne")
        >>> cj.file_number_of_lines
        9
        """
        
        # Access the internal variable to try and get a count even if
        # Unicode conversion fails
        
        try:
            contents = self._file_contents.strip()
        except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
            return None

        return len(contents.splitlines())
    
    file_number_of_lines = property(_get_number_of_lines)
    file_contents = property(_get_file_contents, _set_file_contents)


class Content(Extension):
    deps = ['FileTypes']
    
    MAX_THREADS = 10
    
    def __prepare_table(self, connection, drop_table=False):
        # Drop the table's old data
        if drop_table:
            cursor = connection.cursor()
            
            try:
                cursor.execute("DROP TABLE content")
            except Exception, e:
                printerr("Couldn't drop content table because %s", (e,))
            finally:
                cursor.close()

        if isinstance(self.db, SqliteDatabase):
            from sqlite3 import OperationalError
            cursor = connection.cursor()
            
            # Note that we can't guarentee sqlite is going
            # to provide foreign key support (it was only
            # introduced in 3.6.19), so no constraints are set
            try:
                cursor.execute("""CREATE TABLE content(
                    id INTEGER PRIMARY KEY,
                    commit_id INTEGER NOT NULL,
                    file_id INTEGER NOT NULL,
                    content CLOB,
                    loc INTEGER,
                    size INTEGER,
                    UNIQUE (commit_id, file_id))""")
                cursor.execute("""create index commit_id_index 
                    on content(commit_id)""")
                cursor.execute("""create index commit_id_index 
                    on content(file_id)""")
            except OperationalError:
                # It's OK if the table already exists
                pass
            except:
                raise
            finally:
                cursor.close()

        elif isinstance(self.db, MysqlDatabase):
            from MySQLdb import OperationalError

            cursor = connection.cursor()
            
            # I removed foreign key constraints because
            # cvsanaly uses MyISAM, which doesn't enforce them.
            # MySQL was giving errno:150 when trying to create with
            # them anyway
            try:
                cursor.execute("""CREATE TABLE content(
                    id int(11) NOT NULL auto_increment,
                    commit_id int(11) NOT NULL,
                    file_id int(11) NOT NULL,
                    content mediumtext,
                    loc int(11),
                    size int(11),
                    PRIMARY KEY(id),
                    UNIQUE (commit_id, file_id),
                    index(commit_id),
                    index(file_id)
                    ) ENGINE=InnoDB CHARACTER SET=utf8""")

            except OperationalError as e:
                if e.args[0] == 1050:
                    # It's OK if the table already exists
                    pass
                else:
                    raise
            except:
                raise
            finally:
                cursor.close()

        connection.commit()

    def __process_finished_jobs(self, job_pool, connection, db):
        if isinstance(self.db, SqliteDatabase):
            from sqlite3 import IntegrityError
        elif isinstance(self.db, MysqlDatabase):
            from MySQLdb import IntegrityError
        write_cursor = connection.cursor()
        finished_job = job_pool.get_next_done(0)
        processed_jobs = 0
        # commit_id is the commit ID. For some reason, the 
        # documentation advocates tablename_id as the reference,
        # but in the source, these are referred to as commit IDs.
        # Don't ask me why!
        while finished_job is not None:
            query = """
                insert into content(commit_id, file_id, content, loc, size) 
                    values(?,?,?,?,?)"""
            insert_statement = statement(query, db.place_holder)
            parameters = (finished_job.commit_id,
                          finished_job.file_id,
                          finished_job.file_contents,
                          finished_job.file_number_of_lines,
                          finished_job.file_size)
            try:                    
                write_cursor.execute(insert_statement, parameters)
            except IntegrityError as e:
                if isinstance(self.db, MysqlDatabase) and e.args[0] == 1062:
                    # Ignore duplicate entry
                    pass
                else:
                    printerr(
                        'Error while inserting content for file %d @ commit %d'
                        % (finished_job.file_id, finished_job.commit_id))
                    raise

            processed_jobs += 1
            finished_job = job_pool.get_next_done(0)

        connection.commit()
        write_cursor.close()
            
        return processed_jobs

    def run(self, repo, uri, db):
        # Start the profiler, per every other extension
        profiler_start("Running content extension")

        # Open a connection to the database and get cursors
        self.db = db
        connection = self.db.connect()
        read_cursor = connection.cursor()
        
        # Try to get the repository and get its ID from the database
        try:
            path = uri_to_filename(uri)
            if path is not None:
                repo_uri = repo.get_uri_for_path(path)
            else:
                repo_uri = uri

            read_cursor.execute(statement(
                "SELECT id from repositories where uri = ?",
                db.place_holder), (repo_uri,))
            repo_id = read_cursor.fetchone()[0]
        except NotImplementedError:
            raise ExtensionRunError(
                "Content extension is not supported for %s repos" %
                (repo.get_type()))
        except Exception, e:
            raise ExtensionRunError(
                "Error creating repository %s. Exception: %s" %
                (repo.get_uri(), str(e)))
            
        # Try to create a table for storing the content
        # TODO: Removed use case for choosing between all or just the HEAD,
        # should ideally put that back again. Just all for now is fine.
        try:
            self.__prepare_table(connection)
        except Exception as e:
            raise ExtensionRunError("Couldn't prepare table because " +
                                    str(e))

        queuesize = self.MAX_THREADS
        printdbg("Setting queuesize to " + str(queuesize))

        # This is where the threading stuff comes in, I expect
        job_pool = JobPool(repo, path or repo.get_uri(), queuesize=queuesize)

        # This filters files if they're not source files.
        # I'm pretty sure "unknown" is returning binary files too, but
        # these are implicitly left out when trying to convert to utf-8
        # after download. However, ignore them for now to speed things up
        query = "select f.id from file_types ft, files f " + \
                "where f.id = ft.file_id and " + \
                "ft.type in('code') and " + \
                "f.repository_id = ?"
                # "ft.type in('code', 'unknown') and " + \
        read_cursor.execute(statement(query, db.place_holder), (repo_id,))
        code_files = [item[0] for item in read_cursor.fetchall()]
        query = """select c.file_id, c.commit_id from content c, files f
            where c.file_id=f.id and f.repository_id=?
        """
        read_cursor.execute(statement(query, db.place_holder), (repo_id,))
        existing_content = [(item[0], item[1])
                            for item in read_cursor.fetchall()]

        fr = FileRevs(db, connection, read_cursor, repo_id)

        i = 0
        # Loop through each file and its revision
        for revision, commit_id, file_id, action_type, composed in fr:
            if action_type == 'D':
                continue
#            loop_start = datetime.now()
            if file_id not in code_files:
                continue
            if (file_id, commit_id) in existing_content:
                continue

            try:
                relative_path = fr.get_path(repo, path or repo.get_uri())
            except TypeError as e:
                printerr("No path found for file %d at commit %d", 
                         (file_id, commit_id))
                continue
            if composed:
                rev = revision.split("|")[0]
            else:
                rev = revision

            printdbg("Path for %d at %s -> %s", (file_id, rev, relative_path))

            # Ignore SVN tags
            if repo.get_type() == 'svn' and relative_path == 'tags':
                printdbg("Skipping file %s", (relative_path,))
                continue

            job = ContentJob(commit_id, file_id, rev, relative_path)
            job_pool.push(job)
            i = i + 1
            if i >= queuesize:
                printdbg("Content queue is now at %d, flushing to database", 
                         (i,))
                
                processed_jobs = self.__process_finished_jobs(job_pool, 
                                                              connection, db)
                i = i - processed_jobs
                if processed_jobs < (queuesize / 5):
                    job_pool.join()

        job_pool.join()
        self.__process_finished_jobs(job_pool, connection, db)

        read_cursor.close()
        connection.close()

        # This turns off the profiler and deletes it's timings
        profiler_stop("Running content extension", delete=True)
        
    def backout(self, repo, uri, db):
        update_statement = """delete from content where
                              commit_id in (select id from scmlog s
                                            where s.repository_id = ?)"""

        self._do_backout(repo, uri, db, update_statement)

register_extension("Content", Content)
