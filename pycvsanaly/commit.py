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
This class implements basic operations with commits

@author:       Alvaro Navarro and Israel Herraiz
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro,herraiz@gsyc.escet.urjc.es
"""

class SQLCommit:
    """ This class represents a commit made in the repository."""

    # Static variables
    counter = 0
    created_commits = []

    def __init__(self, properties_dict=None, files_list=None):
        """
        Constructor. 
        Can accept a dictionary containing the properties of this commit, 
        and a list of files objects affected by this commit.
        """

        if properties_dict:
            self.properties_dict = properties_dict.copy()
        else:
            self.properties_dict = {}

        if files_list:
            self.__files_list = files_list
        else:
            self.__files_list = []

        self.id = SQLCommit.counter

        SQLCommit.counter += 1
        SQLCommit.created_commits.append(self)

    def search_commit(self,commit_id):
        """
        Looks for a commit with a given id. 
        It returns a Commit object, or None if given id does not exist.
        """
        try:
            commit = SQLCommit.created_commits(commit_id)
        except:
            commit = None

        return commit

    def get_id(self):
        """
        Return integer id of this commit
        """

        return self.id

    def add_file(self,file_obj):
        """
        Add a file affected by this commit.
        """

        self.__files_list.append(file_obj)


    def get_files(self):
        """
        Get a list of the files affected by this commit.
        """

        return self.__files_list


    def add_properties(self, db, properties):

        query  = "INSERT INTO log (commit_id, file_id, commiter_id, revision, "
        query += "plus, minus, cvs_flag, external, date_log, filetype, module_id, repopath, intrunk, removed) "
        query += " VALUES ('" + str(self.id) + "','"
        query += str(properties['file_id']) + "','"
        query += str(properties['commiter_id']) + "','"
        query += str(properties['revision']) + "','"
        query += str(properties['plus']) + "','"
        query += str(properties['minus']) + "','"
        query += str(properties['cvs_flag']) + "','"
        query += str(properties['external']) + "','"
        query += str(properties['date_log']) + "','"
        query += str(properties['filetype']) + "','"
        query += str(properties['module_id']) + "','"
        query += str(properties['repopath']) + "','"
        query += str(properties['intrunk']) + "','"
        query += str(properties['removed']) + "');"

        db.insertData(query)
        
