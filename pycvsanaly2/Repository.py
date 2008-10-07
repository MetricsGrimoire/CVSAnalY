# Copyright (C) 2007 Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
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

class Commit:
    def __init__ (self):
        self.__dict__ = { 'revision'     : None,
                          'committer'    : None,
                          'author'       : None,
                          'date'         : None,
                          'lines'        : None, 
                          'actions'      : [],
                          'branch'       : None,
                          'message'      : "",
                          'composed_rev' : False }
        
    def __getattr__ (self, name):
        return self.__dict__[name]
        
    def __setattr__ (self, name, value):
        self.__dict__[name] = value

    def __eq__ (self, other):
        return self.revision == other.revision

    def __ne__ (self, other):
        return self.revision != other.revision

# Action types
# A Add
# M Modified
# D Deleted
# V moVed (Renamed)
# C Copied
# R Replaced

class Action:
    def __init__ (self):
        self.__dict__ = { 'type'   : None,
                          'branch' : None,
                          'f1'     : None,
                          'f2'     : None }

    def __getattr__ (self, name):
        return self.__dict__[name]

    def __setattr__ (self, name, value):
        self.__dict__[name] = value

    def __eq__ (self, other):
        return self.type == other.type and \
            self.f1 == other.f1 and \
            self.f2 == other.f2 and \
            self.branch == other.branch
    
    def __ne__ (self, other):
        return self.type != other.type or \
            self.f1 != other.f1 or \
            self.f2 != other.f2 or \
            self.branch != other.branch
    
class File:
    def __init__ (self):
        self.__dict__ = { 'path'  : None,
                          'type'  : None,
                          'size'  : None,
                          'cdate' : None,
                          'mdate' : None }

    def __getattr__ (self, name):
        return self.__dict__[name]

    def __setattr__ (self, name, value):
        self.__dict__[name] = value

    def __eq__ (self, other):
        return self.path == other.path

    def __ne__ (self, other):
        return self.path != other.path
