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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import time


class Timer:
    def __init__(self):
        self.start()

    def start(self):
        self._active = True
        self._start = time.time()

    def stop(self):
        self._active = False
        self._end = time.time()

    def resume(self):
        elapsed = self._end - self._start
        self._start = time.time()
        self._start -= elapsed
        self._active = True

    def elapsed(self):
        if self._active:
            self._end = time.time()

        elapsed = self._end - self._start

        return elapsed


if __name__ == '__main__':
    t = Timer()
    time.sleep(5)
    t.stop()
    print "Elapsed %f" % (t.elapsed())
    print

    t.start()
    for i in range(10):
        time.sleep(2)
        print "Elapsed %f " % (t.elapsed())
    print

    for i in range(10):
        t.start()
        time.sleep(2)
        print "Elapsed %f " % (t.elapsed())
    print

    t.start()
    time.sleep(2)
    t.stop()
    print "Elapsed %f " % (t.elapsed())
    t.resume()
    time.sleep(2)
    print "Elapsed %f " % (t.elapsed())
