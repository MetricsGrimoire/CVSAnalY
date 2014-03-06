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

from ContentHandler import ContentHandler
from DBContentHandler import DBContentHandler
from DBTempLog import DBTempLog
from AsyncQueue import AsyncQueue, TimeOut
from utils import printdbg
import threading


class DBProxyContentHandler(ContentHandler):
    def __init__(self, db):
        ContentHandler.__init__(self)

        self.db = db
        self.templog = None
        self.order = ContentHandler.ORDER_REVISION
        self.repo_uri = None

        self.db_handler = DBContentHandler(db)

    def begin(self, order=None):
        self.templog = DBTempLog(self.db)
        if order is not None:
            self.order = order

    def repository(self, uri):
        self.repo_uri = uri

    def commit(self, commit):
        self.templog.insert(commit)

    def __reader(self, templog, queue):
        def commit_cb(item):
            queue.put(item)

        printdbg("DBProxyContentHandler: thread __reader started")
        templog.foreach(commit_cb, self.order)
        printdbg("DBProxyContentHandler: thread __reader finished")

    def end(self):
        # The log is now in the temp table
        # Retrieve the data now and pass it to
        # the real content handler

        self.templog.flush()
        printdbg("DBProxyContentHandler: parsing finished, creating thread")

        self.db_handler.begin()
        self.db_handler.repository(self.repo_uri)

        queue = AsyncQueue(50)
        reader_thread = threading.Thread(target=self.__reader,
                                         args=(self.templog, queue))
        reader_thread.setDaemon(True)
        reader_thread.start()

        # Use the queue with mutexes while the
        # thread is alive
        while reader_thread.isAlive():
            try:
                item = queue.get(1)
            except TimeOut:
                continue
            printdbg("DBProxyContentHandler: commit: %s", (item.revision,))
            self.db_handler.commit(item)
            del item

        # No threads now, we don't need locks
        printdbg("DBProxyContentHandler: thread __reader is finished, continue without locks")
        while not queue.empty_unlocked():
            item = queue.get_unlocked()
            self.db_handler.commit(item)
            del item

        self.db_handler.end()
        self.templog.clear()
