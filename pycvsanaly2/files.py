# Copyright (C) 2006 Libresoft
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
# Authors : 
#       Alvaro Navarro <anavarro@gsyc.escet.urjc.es>
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>       

"""
Class that implements basic operations with files

@author:       Alvaro Navarro and Israel Herraiz
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro,herraiz@gsyc.escet.urjc.es
"""

class File:
    """ This class represents a file in the repository."""

    # Static variables
    counter = 0
    created_files = []

    def __init__(self,properties_dict=None, commits_list=None):
        """
        Constructor. 
        Can accept a dictionary containing the properties of the file, 
        and a list of commits objects affecting this file.
        """

        if properties_dict:
            self.properties_dict = properties_dict.copy()
            self.properties_dict['file_id'] = File.counter
        else:
            self.properties_dict = {}

        if commits_list:
            self.__commits_list = commits_list
        else:
            self.__commits_list = []


        self.id = File.counter

        File.counter += 1
        File.created_files.append(self)

    def search_file(self,file_id):
        """Looks for a file with a given id. It returns a File object, or None if given id does not exist."""

        try:
            file = File.created_files(file_id)
        except:
            file = None

        return file

    def get_id(self):
        """
        Return integer id of this file
        """

        return self.id


    def add_properties(self, db, properties):
        """ 
        Add properties 
        """

        query = "INSERT INTO files (file_id, module_id, name, creation_date, last_modification, size, filetype, repopath) "
        query += " VALUES ('" + str(self.id) + "','"
        query += str(properties['module_id']) + "','"
        query += str(properties['name']) + "','"
        query += str(properties['creation_date']) + "','"
        query += str(properties['last_modification']) + "','"
        query += str(properties['size']) + "','"
        query += str(properties['filetype']) + "','"
        query += str(properties['repopath']) + "');"

        db.insertData(query)

    def add_commit(self,commit_obj):
        """
        Add a commit affecting this file.
        """

        self.__commits_list.append(commit_obj)


    def get_commits(self):
        """
        Get a list of the commits affecting this file.
        """

        return self.__commits_list

