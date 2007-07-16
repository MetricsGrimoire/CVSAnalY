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

(
    ADD,
    DELETE,
    MODIFY
) = range (3)

class Commit:
    def __init__ (self):
        self.__dict__ = { 'revision' : None,
                          'commiter' : None,
                          'date'     : None,
                          'files'    : [],
                          'message'  : "" }
        
    def __getattr__ (self, name):
        return self.__dict__[name]
        
    def __setattr__ (self, name, value):
        self.__dict__[name] = value

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

