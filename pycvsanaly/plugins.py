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

"""

@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro@gsyc.escet.urjc.es
"""
import os
import sys

main_module    = 'cvsplugins'
main_function  = 'main'

"""
All plugins should hitherate from this class
"""
class Plugin:

    def init (self, db=''):
        self.author = ''
        self.mail = ''
        self.description = ''
        self.date = ''

    def info (self):
        pass

    def run  (self, db=''):
        pass

    def get_author (self):
        return self.author

    def get_description (self):
        return self.description

class Loader:

    def __init__(self):
        """
        Constructor. 
        """
        self._plugins = []
        subdir = []

        # Look into sys.path variables in order to 
        # find valid plugins under $main_module value
        # For example: /usr/lib/python2.4/site-packages/cvsplugins

        for syspath in sys.path:
            aux = syspath + '/' + main_module

            # Only if we find a directory called 'cvsplugins'
            # in sys.path, we add subdirectories.
            # Each subdirectory will be a plugin
            if os.path.isdir (aux):
                #print "Searching plugins in " + aux
                subdir = os.listdir(aux)

                # Add each subdirectory as a valid plugin
                # Later, we will check if really this subdir is 
                # a valid plugin or not.
                for p in subdir:
                    if p not in self._plugins and p[0:8] != '__init__':
                        self._plugins.append (p)

    def get_plugins (self):

        return self._plugins

    def get_information (self, module):

        if not module in self._names:
            print "Cannot get information! Plugin not found \n"

    def my_import (self, name):

        mod = __import__ (name)
        comp = name.split ('.')
        for c in comp[1:]:
            mod = getattr (mod, c)
        return mod

    def scan (self):

        print "\nAvaiable plugins:\n"
        plugins = self.get_plugins ()

        for plugin in plugins:
            completepath = main_module + '.' + plugin + '.' + main_function
            try:
                mod = self.my_import (completepath)
                mod.info ()
                print "--------------------"
            except:
                pass

        if not plugins:
            print "No plugins found: No such file or directory: " + main_module
        print "\n"

