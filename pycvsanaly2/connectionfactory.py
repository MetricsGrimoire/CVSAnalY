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
Connection factory class

@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro@gsyc.escet.urjc.es
"""

import sys

class ConnectionFactory:

    def create_connector_stdout ():
        import connectionStdout
        return connectionStdout.ConnectionStdout ()

    def create_connector_mysql ():
        import connectionMySQL
        return connectionMySQL.ConnectionMySQL ()

    def create_connector_sqlite ():
        import connectionSQLite
        return connectionSQLite.ConnectionSQLite ()

    drivers = {                                     \
            'mysql'  : create_connector_mysql, \
            'stdout' : create_connector_stdout,  \
            'sqlite' : create_connector_sqlite \
    }

    def create_connector (driver):
        key = str(driver).lower ()

        if not ConnectionFactory.drivers.has_key (key):
            sys.exit ("Driver %s is not yet implemented" % driver)

        return ConnectionFactory.drivers[key] ()

    create_connector = staticmethod (create_connector)

