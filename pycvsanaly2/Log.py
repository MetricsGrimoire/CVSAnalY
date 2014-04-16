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

import threading
from repositoryhandler.backends.watchers import LOG
from AsyncQueue import AsyncQueue, TimeOut
from utils import printerr


class RepoOrLogfileRequired(Exception):
    '''Repository or Logfile is required to read a log'''


class LogReader:
    def __init__(self):
        self.logfile = None
        self.repo = None
        self.uri = None
        self.files = None
        self.gitref = None

    def set_repo(self, repo, uri=None, files=None, gitref=None):
        self.repo = repo
        if uri is not None:
            self.uri = uri
        if files is not None:
            self.files = files
        if gitref is not None:
            self.gitref = gitref

    def set_logfile(self, filename):
        self.logfile = filename

    def _read_from_logfile(self, new_line_cb, user_data):
        try:
            f = open(self.logfile, 'r')
        except IOError, e:
            printerr(str(e))
            return

        line = f.readline()
        while line:
            new_line_cb(line, user_data)
            line = f.readline()

        f.close()

    def _logreader(self, repo, queue):
        def new_line(data, user_data=None):
            queue.put(data)

        repo.add_watch(LOG, new_line)

        if repo.type == 'git':
            repo.log(self.uri or repo.get_uri(), files=self.files, gitref=self.gitref)
        else:
            repo.log(self.uri or repo.get_uri(), files=self.files)

    def _read_from_repository(self, new_line_cb, user_data):
        queue = AsyncQueue()
        logreader_thread = threading.Thread(target=self._logreader,
                                            args=(self.repo, queue))
        logreader_thread.setDaemon(True)
        logreader_thread.start()

        # Use the queue with mutexes while the
        # thread is alive
        while logreader_thread.isAlive():
            try:
                line = queue.get(1)
            except TimeOut:
                continue
            new_line_cb(line, user_data)

        # No threads now, we don't need locks
        while not queue.empty_unlocked():
            line = queue.get_unlocked()
            new_line_cb(line, user_data)

    def start(self, new_line_cb, user_data=None):
        if self.logfile is not None:
            try:
                self._read_from_logfile(new_line_cb, user_data)
            except IOError, e:
                printerr(str(e))
        elif self.repo is not None:
            self._read_from_repository(new_line_cb, user_data)
        else:
            raise RepoOrLogfileRequired("In order to start the log reader " +
                                        "a repository or a logfile has to be provided")


class LogWriter:
    CHUNK_SIZE = 1024

    def __init__(self, filename):
        self.fd = open(filename, "w")
        self.buffer = ""

    def add_line(self, line):
        self.buffer += line
        if len(self.buffer) >= self.CHUNK_SIZE:
            self.fd.write(self.buffer)
            self.buffer = ""

    def close(self):
        if self.buffer:
            self.fd.write(self.buffer)
        self.fd.close()


if __name__ == '__main__':
    import sys
    import os
    from utils import uri_to_filename
    from repositoryhandler.backends import create_repository, create_repository_from_path

    def new_line(line, user_data=None):
        print line.strip('\n')
        if user_data is not None:
            user_data.add_line(line)

    path = uri_to_filename(sys.argv[1])
    if path is not None:
        repo = create_repository_from_path(path)
    else:
        repo = create_repository('svn', sys.argv[1])
        path = sys.argv[1]

    reader = LogReader()
    reader.set_repo(repo, path)

    writer = None

    if len(sys.argv) > 2:
        if os.path.isfile(sys.argv[2]):
            reader.set_logfile(sys.argv[2])
        else:
            writer = LogWriter(sys.argv[2])

    reader.start(new_line, writer)
    writer and writer.close()
