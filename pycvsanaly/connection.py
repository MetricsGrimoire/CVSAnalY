# Copyright (C) 2006 Alvaro Navarro Clemente
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
# Authors : Alvaro Navarro <anavarro@gsyc.escet.urjc.es>

"""
Connection framework

@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro@gsyc.escet.urjc.es
"""

import os
import time
import sys
import _mysql
import _mysql_exceptions


class Connection:
    """
    Basic interface that defines which methods have to be
    implemented
    """

    def connect(self, user=None, passwd=None, host=None, db=None):
        pass

    def close(self):
        pass

    def execute(self,query):
        pass


class ConnectionFactory:

    def get_connection(driver):
        if str(driver).lower() == "mysql":
            return (ConnectionMySQL())
        elif str(driver).lower() == "stdout":
            return (ConnectionStdout())
        else:
            sys.exit("not implemented yet")

    get_connection = staticmethod(get_connection)


class ConnectionMySQL(Connection):

    def __init__(self):
        self._conn = None

    def connect(self, user='', passwd='', host='', db=''):
        self._conn = _mysql.connect(host, user, passwd, db)

    def execute(self, query):

        self._conn.query(query)
        result = self._conn.store_result()

        return result

    def close(self):

        try:
            if self._conn != None:
                self._conn.close()
        except:
            pass

        self._conn = None

class ConnectionStdout(Connection):

    def __init__(self):
        pass

    def execute(self, query):
        sys.stdout.flush()
        sys.stdout.write (query)
        print "\n"

        return None

