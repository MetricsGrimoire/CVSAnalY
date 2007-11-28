# Copyright (C) 2007 LibreSoft
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
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from Repository import *
import libcvsanaly.Database as db

class DBRepository (db.DBRepository):

    def __init__ (self, uri, name):
        self.uri = unicode (uri)
        self.name = unicode (name)

class DBLog (db.DBLog):

    def __init__ (self, commit):
        self.rev = unicode (commit.revision)
        self.committer = unicode (commit.committer, 'utf-8', 'replace')
        if commit.author is not None:
            self.author = unicode (commit.author, 'utf-8', 'replace')
            
        self.date = commit.date
        self.message = unicode (commit.message, 'utf-8', 'replace')
        self.composed_rev = commit.composed_rev

class DBFile (db.DBFile):

    def __init__ (self, file_name, parent):
        self.file_name = unicode (file_name)
        self.parent = parent
        self.deleted = False
        
class DBAction (db.DBAction):
    
    def __init__ (self, type):
        self.type = type

