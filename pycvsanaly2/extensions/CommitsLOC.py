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

import os
import re
from subprocess import Popen, PIPE
from repositoryhandler.backends.watchers import DIFF

from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists, statement)
from pycvsanaly2.Log import LogReader
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.utils import printerr, uri_to_filename
from pycvsanaly2.FindProgram import find_program
from pycvsanaly2.Command import Command, CommandError


class DBCommitLines:
    id_counter = 1

    __insert__ = "INSERT INTO commits_lines (id, commit_id, added, removed) values (?, ?, ?, ?)"

    def __init__(self, id, commit_id, added, removed):
        if id is None:
            self.id = DBCommitLines.id_counter
            DBCommitLines.id_counter += 1
        else:
            self.id = id

        self.commit_id = commit_id
        self.added = added
        self.removed = removed


class LineCounter:
    def __init__(self, repo, uri):
        self.repo = repo
        self.uri = uri

    def get_lines_for_revision(self, revision):
        raise NotImplementedError


class CVSLineCounter(LineCounter):
    def __init__(self, repo, uri):
        LineCounter.__init__(self, repo, uri)

        from pycvsanaly2.Config import Config
        from pycvsanaly2.CVSParser import CVSParser

        p = CVSParser()
        p.set_repository(repo, uri)

        def new_line(line, parser):
            parser.feed(line)

        reader = LogReader()
        reader.set_repo(repo, uri)
        logfile = Config().repo_logfile
        if logfile is not None:
            reader.set_logfile(logfile)

        reader.start(new_line, p)

        self.lines = p.get_added_removed_lines()

    def get_lines_for_revision(self, revision):
        return self.lines.get(revision, (0, 0))


class SVNLineCounter(LineCounter):
    diffstat_pattern = re.compile("^ \d+ file[s]? changed(, (\d+) insertion[s]?\(\+\))?(, (\d+) deletion[s]?\(\-\))?$")

    def __init__(self, repo, uri):
        LineCounter.__init__(self, repo, uri)
        self.diffstat = find_program('diffstat')
        if self.diffstat is None:
            raise ExtensionRunError("Error running CommitsLOC extension: " +
                                    "required diffstat command cannot be found in path")

    def get_lines_for_revision(self, revision):

        revision = int(revision)

        def diff_line(data, diff_data_l):
            diff_data = diff_data_l[0]
            diff_data += data
            diff_data_l[0] = diff_data

        revs = []
        revs.append("%d" % (revision - 1))
        revs.append("%d" % (revision))
        env = os.environ.copy().update({'LC_ALL': 'C'})
        pipe = Popen(self.diffstat, shell=False, stdin=PIPE, stdout=PIPE, close_fds=True, env=env)
        diff_data = [""]
        wid = self.repo.add_watch(DIFF, diff_line, diff_data)
        try:
            self.repo.diff(self.repo.get_uri(), revs=revs)
        except Exception, e:
            printerr("Error running svn diff command: %s", (str(e)))
            self.repo.remove_watch(DIFF, wid)
            return (0, 0)

        out = pipe.communicate(diff_data[0])[0]
        self.repo.remove_watch(DIFF, wid)

        lines = out.split('\n')
        lines.reverse()

        for line in lines:
            m = self.diffstat_pattern.match(line)
            if m is None:
                continue

            added = removed = 0
            if m.group(1) is not None:
                added = int(m.group(2))

            if m.group(3) is not None:
                removed = int(m.group(4))

            return (added, removed)

        return (0, 0)


class GitLineCounter(LineCounter):
    diffstat_pattern = re.compile("^ \d+ files? changed(, (\d+) insertions?\(\+\))?(, (\d+) deletions?\(\-\))?$")

    def __init__(self, repo, uri):
        LineCounter.__init__(self, repo, uri)

        self.git = find_program('git')
        if self.git is None:
            raise ExtensionRunError("Error running CommitsLOC extension: " +
                                    "required git command cannot be found in path")

        self.lines = {}

        cmd = [self.git, 'log', '--all', '--topo-order', '--shortstat', '--pretty=oneline', 'origin']
        c = Command(cmd, uri)
        try:
            c.run(parser_out_func=self.__parse_line)
        except CommandError, e:
            if e.error:
                printerr("Error running git log command: %s", (e.error,))
            raise ExtensionRunError("Error running CommitsLOC extension: %s", str(e))

    def __parse_line(self, line):
        match = self.diffstat_pattern.match(line)
        if match:
            added = removed = 0
            if match.group(1) is not None:
                added = int(match.group(2))

            if match.group(3) is not None:
                removed = int(match.group(4))

            self.lines[self.rev] = (added, removed)
        else:
            # We only have two kinds of lines:
            # if it's not a diffstat, it's a rev line
            # (except if it is an empty line, in which case it is just ignored)
            parts = line.split(None, 1)
            if len(parts) > 0:
                self.rev = parts[0]

    def get_lines_for_revision(self, revision):
        return self.lines.get(revision, (0, 0))


_counters = {
    'cvs': CVSLineCounter,
    'svn': SVNLineCounter,
    'git': GitLineCounter
}


def create_line_counter_for_repository(repo, uri):
    try:
        counter = _counters[repo.get_type()]
    except KeyError:
        raise ExtensionRunError("Repository type %s is not supported by CommitsLOC extension" % (repo.get_type()))

    return counter(repo, uri)


class CommitsLOC(Extension):
    def __init__(self):
        self.db = None

    def __create_table(self, cnn):
        cursor = cnn.cursor()

        if isinstance(self.db, SqliteDatabase):
            import sqlite3

            try:
                cursor.execute("CREATE TABLE commits_lines (" +
                               "id integer primary key," +
                               "commit_id integer," +
                               "added integer," +
                               "removed integer" +
                               ")")
            except sqlite3.OperationalError:
                cursor.close()
                raise TableAlreadyExists
            except:
                raise
        elif isinstance(self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute("CREATE TABLE commits_lines (" +
                               "id INT primary key," +
                               "commit_id integer," +
                               "added int," +
                               "removed int," +
                               "FOREIGN KEY (commit_id) REFERENCES scmlog(id)" +
                               ") ENGINE=MyISAM" +
                               " CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    cursor.close()
                    raise TableAlreadyExists
                raise
            except:
                raise

        cnn.commit()
        cursor.close()

    def __get_commits_lines_for_repository(self, repo_id, cursor):
        query = "SELECT cm.commit_id from commits_lines cm, scmlog s " + \
                "WHERE cm.commit_id = s.id and repository_id = ?"
        cursor.execute(statement(query, self.db.place_holder), (repo_id,))
        commits = [res[0] for res in cursor.fetchall()]

        return commits

    def run(self, repo, uri, db):
        self.db = db

        path = uri_to_filename(uri)
        if path is not None:
            repo_uri = repo.get_uri_for_path(path)
        else:
            repo_uri = uri

        cnn = self.db.connect()

        cursor = cnn.cursor()
        cursor.execute(statement("SELECT id from repositories where uri = ?", db.place_holder), (repo_uri,))
        repo_id = cursor.fetchone()[0]

        # If table does not exist, the list of commits is empty,
        # otherwise it will be filled within the except block below
        commits = []

        try:
            self.__create_table(cnn)
        except TableAlreadyExists:
            cursor.execute(statement("SELECT max(id) from commits_lines", db.place_holder))
            id = cursor.fetchone()[0]
            if id is not None:
                DBCommitLines.id_counter = id + 1

            commits = self.__get_commits_lines_for_repository(repo_id, cursor)
        except Exception, e:
            raise ExtensionRunError(str(e))

        counter = create_line_counter_for_repository(repo, uri)

        cursor.execute(statement("SELECT id, rev, composed_rev from scmlog where repository_id = ?",
                                 db.place_holder), (repo_id,))
        write_cursor = cnn.cursor()
        rs = cursor.fetchmany()
        while rs:
            commit_list = []

            for commit_id, revision, composed_rev in rs:
                if commit_id in commits:
                    continue

                if composed_rev:
                    rev = revision.split("|")[0]
                else:
                    rev = revision

                (added, removed) = counter.get_lines_for_revision(revision)
                commit_list.append(DBCommitLines(None, commit_id, added, removed))

            if commit_list:
                commits_lines = [(commit.id, commit.commit_id, commit.added, commit.removed) for commit in commit_list]
                write_cursor.executemany(statement(DBCommitLines.__insert__, self.db.place_holder), commits_lines)

            rs = cursor.fetchmany()

        cnn.commit()
        write_cursor.close()
        cursor.close()
        cnn.close()


register_extension("CommitsLOC", CommitsLOC)
