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
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import threading
from collections import deque

class AsyncQueue:

    def __init__ (self):
        self._init ()
        self.mutex = threading.Lock ()
        self.cond = threading.Condition (self.mutex)
        self.finish = threading.Condition (self.mutex)

        self.pending_items = 0

    def done (self):
        self.finish.acquire ()
        try:
            pending = self.pending_items - 1
            if pending < 0:
                raise ValueError ('done() called too many times')
            elif pending == 0:
                self.finish.notifyAll ()
            self.pending_items = pending
        finally:
            self.finish.release ()

    def join (self):
        self.finish.acquire ()
        try:
            while self.pending_items:
                self.finish.wait ()
        finally:
            self.finish.release ()
        
    def empty (self):
        self.mutex.acquire ()
        retval = self._empty ()
        self.mutex.release ()

        return retval

    def empty_unlocked (self):
        return self._empty ()

    def put (self, item):
        self.cond.acquire ()
        try:
            self._put (item)
            self.pending_items += 1
            self.cond.notify ()
        finally:
            self.cond.release ()

    def put_unlocked (self, item):
        self._put (item)

    def get (self):
        self.cond.acquire ()
        try:
            while self._empty ():
                self.cond.wait ()
            item = self._get ()
            return item
        finally:
            self.cond.release ()

    def get_unlocked (self):
        return self._get ()


    # Queue implementation
    def _init (self):
        self.queue = deque ()

    def _empty (self):
        return not self.queue

    def _put (self, item):
        self.queue.append (item)

    def _get (self):
        return self.queue.popleft ()

if __name__ == '__main__':
    def worker (q):
        while True:
             item = q.get ()
             print "Got item ", item
             q.done ()

    q = AsyncQueue ()
    for i in range (5):
        t = threading.Thread (target=worker, args=(q,))
        t.setDaemon (True)
        t.start ()

    for item in ['foo', 'bar', 1, 2, {'a' : 'b'}, [5,6,7]]:
        q.put (item)

    q.join ()
        
