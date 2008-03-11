# Copyright (C) 2008 LibreSoft
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

from extensions import get_extension, ExtensionRunError
from utils import printerr, printout

class InvalidExtension (Exception):
    def __init__ (self, name):
        self.name = name

class ExtensionsManager:

    def __init__ (self, exts):
        self.exts = {}
        for ext in exts:
            try:
                self.exts[ext] = get_extension (ext)
            except:
                raise
                raise InvalidExtension (ext)

        # TODO: add dependencies
            
    def run_extensions (self, repo, db):
        # TODO: sort the list taking deps into account
        for name, extension in [(ext, self.exts[ext] ()) for ext in self.exts]:
            printout ("Executing extension %s", (name))
            try:
                extension.run (repo, db)
            except ExtensionRunError, e:
                printerr ("Error running extension %s: %s", (name, e.message))
    
