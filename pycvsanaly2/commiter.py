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
This class implements basic operations with Commiters

@author:       Alvaro Navarro and Israel Herraiz
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro,herraiz@gsyc.escet.urjc.es
"""

class Commiter:
    """ This class represents a commiter in the repository."""

    # Static variables
    counter = 0
    created_commiters = []

    def __init__(self,properties_dict=None, commits_list=None):
        """
        Constructor. 
        Can accept a dictionary containing the properties of the commiter, 
        and a list of commits objects affecting this commiter.
        """

        if properties_dict:
            self.properties_dict = properties_dict.copy()
        else:
            self.properties_dict = {}

        if commits_list:
            self.__commits_list = commits_list
        else:
            self.__commits_list = []


        self.id = Commiter.counter

        Commiter.counter += 1
        Commiter.created_commiters.append(self)


    def search_commiter(self,commiter_id):
        """
        Looks for a commiter with a given id. 
        It returns a commiter object, or None if given id does not exist.
        """

        try:
            commiter = Commiter.created_commiters(commiter_id)
        except:
            commiter = None

        return commiter

    def get_id(self):
        """
        Return integer id of this commiter
        """
        return self.id


    def add_commit(self,commit_obj):
        """
        Add a commit affecting this Commiter.
        """
        self.__commits_list.append(commit_obj)


    def get_commits(self):
        """
        Get a list of the commits affecting this Commiter.
        """
        return self.__commits_list

