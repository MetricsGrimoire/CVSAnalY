# Copyright (C) 2013 Bitergia
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
#       Daniel Izquierdo Cortazar <dizquierdo@bitergia.com>

"""
Produces a table with the detected licenses per file
for the current working tree.

This extensions needs the output of the Ninka tool.
Licenses are only calculated for the current state of 
working tree. 
"""

from time import strptime, strftime
from datetime import datetime

from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.extensions.DBTable import DBTable
import os
import tempfile

class LicensesTable (DBTable):
    """Class for managing the licenses table

    Each record in the table has three fields:
      - id: an auto incremented integer
      - file_id: an integer pointing to id in table files
      - license: a string containing the license detected by Ninka
    """

    _sql_create_table_sqlite = "CREATE table licenses (" +\
         "id integer primary key," +\
         "file_id integer," +\
         "license varchar(20)" +\
         ")"

    _sql_create_table_mysql = "CREATE table licenses (" +\
         "id INTEGER NOT NULL AUTO_INCREMENT," +\
         "file_path varchar(4096) NOT NULL," +\
         "license varchar(20) NOT NULL,"+ \
         "PRIMARY KEY(id)" \
         ") ENGINE=MyISAM" +\
         " CHARACTER SET=utf8"

class Licenses (Extension):

    def run(self, repo, uri, db):

        #Creation of temporary file to store Ninka output
        tmp_file = tempfile.NamedTemporaryFile(prefix="cvsanaly_", dir='/tmp')
        tmp_file_path = tmp_file.name
 
        #Creation of exec command line for Ninka
        exec_command = "find "+ str(uri) +" | grep -v .git | xargs -n1 -I@ /usr/lib/ninka/ninka.pl -d '@' > " + str(tmp_file_path)

        #Creation of access to database
        connector = db.connect()
        cursor = connector.cursor()
        write_cursor = connector.cursor()
        licensesTable = LicensesTable(db, connector, repo)
    
       
        #Remove old table if exists
        cursor.execute ("DROP TABLE IF EXISTS licenses")

        print exec_command
        os.system(exec_command)

        fd = open(tmp_file_path, "r")

        line = "foo"
        cont = 0
        while line <> '':
            if ";" in line:
                file_path = line.split(";")[0]
                license = line.split(";")[1]
                file_path = file_path.replace("./", "")
            
                query = "Insert into licenses(file_path, license) " +\
                        " values('" + file_path + "', '" + license + "');"
                print(query)
                licensesTable.add_pending_row(query)
                cont = cont +1
                if cont == 10:
                    break

        licensesTable.insert_rows(write_cursor)
        connector.commit()
        write_cursor.close()
        cursor.close()
        connector.close()
             
                   
# Register in the CVSAnalY extension system
register_extension ("Licenses", Licenses)
