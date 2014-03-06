# Copyright (C) 2009 LibreSoft
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
# Authors:
#       Carlos Garcia Campos <carlosgc@libresoft.es>

if __name__ == '__main__':
    import sys

    sys.path.insert(0, "../")

from pycvsanaly2.AsyncQueue import AsyncQueue, TimeOut
import repositoryhandler.backends as rh
import threading


class JobPool:
    POOL_SIZE = 5

    def __init__(self, repo, repo_uri, jobs_done=True, poolsize=POOL_SIZE, queuesize=None):
        self.jobs_done = jobs_done

        self.queue = AsyncQueue(queuesize or 0)
        if self.jobs_done:
            self.done = AsyncQueue()

        for i in range(poolsize):
            rep = rh.create_repository(repo.get_type(), repo.get_uri())
            thread = threading.Thread(target=self._job_thread, args=(rep, repo_uri))
            thread.setDaemon(True)
            thread.start()

    def _job_thread(self, repo, repo_uri):
        while True:
            job = self.queue.get()
            job.run(repo, repo_uri)
            self.queue.done()

            if self.jobs_done:
                self.done.put(job)

    def push(self, job):
        self.queue.put(job)

    def get_next_done(self, timeout=None):
        if not self.jobs_done:
            return None

        try:
            job = self.done.get(timeout)
            self.done.done()
            return job
        except TimeOut:
            return None

    def get_next_done_unlocked(self):
        if not self.jobs_done:
            return None

        if self.done.empty_unlocked():
            return None

        return self.done.get_unlocked()

    def join(self):
        self.queue.join()


class Job:
    def run(self, repo, repo_uri):
        raise NotImplementedError


if __name__ == '__main__':
    class JobLastRev(Job):
        def __init__(self, module):
            self.module = module

        def run(self, repo, repo_uri):
            uri = repo_uri + self.module
            print "%s -> %s" % (uri, repo.get_last_revision(uri))

    modules = ['cvsanaly', 'octopus', 'cmetrics', 'repositoryhandler', 'retrieval_system',
               'bicho', 'pandaRest']
    repo = rh.create_repository('svn', 'https://svn.forge.morfeo-project.org/svn/libresoft-tools/')
    repo_uri = 'https://svn.forge.morfeo-project.org/svn/libresoft-tools/'

    pool = JobPool(repo, repo_uri, False)
    for module in modules:
        job = JobLastRev(module)
        pool.push(job)

    pool.join()
