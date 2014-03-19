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

import os
import sys
import threading

from Timer import Timer
from Config import Config

config = Config()


def plog(data):
    if not config.profile:
        return

    str = "MARK: %s: %s" % ('foo', data)
    os.access(str, os.F_OK)


def profiler_start(msg, args=None):
    if not config.profile:
        return

    if args is not None:
        msg = msg % args

    ct = threading.currentThread()
    try:
        _timers = ct._timers
    except AttributeError:
        ct._timers = {}
        _timers = ct._timers

    if msg in _timers:
        _timers[msg].start()
    else:
        _timers[msg] = Timer()


def profiler_stop(msg, args=None, delete=False):
    if not config.profile:
        return

    if args is not None:
        msg = msg % args

    ct = threading.currentThread()
    _timers = ct._timers
    t = _timers[msg]
    t.stop()

    str = "[ %s ] %f s elapsed\n" % (msg, t.elapsed())
    sys.stdout.write(str)
    sys.stdout.flush()

    if delete:
        del _timers[msg]


if __name__ == '__main__':
    import time

    Config().profile = True

    def _thread(n):
        profiler_start("Running thread %d sleeping %d seconds", (n, n + 1))
        time.sleep(n + 1)
        profiler_stop("Running thread %d sleeping %d seconds", (n, n + 1), True)

    for i in range(6):
        thread = threading.Thread(target=_thread, args=(i,))
        thread.setDaemon(True)
        thread.start()

    thread.join()
