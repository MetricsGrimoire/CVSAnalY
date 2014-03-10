# Copyright (C) 2008 Libresoft
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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import threading
from time import time as _time
from collections import deque


class TimeOut(Exception):
    pass


class AsyncQueue:
    def __init__(self, maxsize=0):
        self._init(maxsize)
        self.mutex = threading.Lock()
        self.empty_cond = threading.Condition(self.mutex)
        self.full_cond = threading.Condition(self.mutex)
        self.finish = threading.Condition(self.mutex)

        self.pending_items = 0

    def done(self):
        self.finish.acquire()
        try:
            pending = self.pending_items - 1
            if pending < 0:
                raise ValueError('done() called too many times')
            elif pending == 0:
                self.finish.notifyAll()
            self.pending_items = pending
        finally:
            self.finish.release()

    def join(self):
        self.finish.acquire()
        try:
            while self.pending_items:
                self.finish.wait()
        finally:
            self.finish.release()

    def empty(self):
        self.mutex.acquire()
        retval = self._empty()
        self.mutex.release()

        return retval

    def empty_unlocked(self):
        return self._empty()

    def put(self, item, timeout=None):
        self.full_cond.acquire()
        try:
            if timeout is None:
                while self._full():
                    self.full_cond.wait()
            else:
                if timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                endtime = _time() + timeout
                while self._full():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise TimeOut
                    self.full_cond.wait(remaining)

            self._put(item)
            self.pending_items += 1
            self.empty_cond.notify()
        finally:
            self.full_cond.release()

    def put_unlocked(self, item):
        self._put(item)

    def get(self, timeout=None):
        self.empty_cond.acquire()
        try:
            if timeout is None:
                while self._empty():
                    self.empty_cond.wait()
            else:
                if timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                endtime = _time() + timeout
                while self._empty():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise TimeOut
                    self.empty_cond.wait(remaining)

            item = self._get()
            self.full_cond.notify()
            return item
        finally:
            self.empty_cond.release()

    def get_unlocked(self):
        return self._get()

    # Queue implementation
    def _init(self, maxsize):
        self.maxsize = maxsize
        self.queue = deque()

    def _empty(self):
        return not self.queue

    def _full(self):
        return self.maxsize > 0 and len(self.queue) == self.maxsize

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.popleft()


if __name__ == '__main__':
    def worker(q):
        while True:
            item = q.get()
            print "Got item ", item
            q.done()

    q = AsyncQueue()
    for i in range(5):
        t = threading.Thread(target=worker, args=(q,))
        t.setDaemon(True)
        t.start()

    for item in ['foo', 'bar', 1, 2, {'a': 'b'}, [5, 6, 7]]:
        q.put(item)

    q.join()

    try:
        q.get(5)
    except TimeOut:
        print "Queue empty! bye bye!"
