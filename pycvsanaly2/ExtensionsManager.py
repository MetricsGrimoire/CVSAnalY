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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from extensions import get_extension, ExtensionRunError, ExtensionUnknownError
from utils import printerr, printout
import os


class ExtensionException(Exception):
    '''ExtensionException'''


class InvalidExtension(ExtensionException):
    def __init__(self, name, message):
        self.name = name
        self.message = message


class InvalidDependency(ExtensionException):
    def __init__(self, name1, name2):
        self.name1 = name1
        self.name2 = name2


class ExtensionsManager:
    def __init__(self, exts):
        self.exts = {}
        for ext in exts:
            try:
                self.exts[ext] = get_extension(ext)
            except ExtensionUnknownError as e:
                raise InvalidExtension(ext, e.message)

            # Add dependencies
            self.determine_deps(ext)

    def determine_deps(self, ext):
        for dep in self.exts[ext].deps:
            if dep not in self.exts.keys():
                try:
                    self.exts[dep] = get_extension(dep)
                    if self.exts[dep].deps:
                        self.determine_deps(dep)
                except:
                    raise InvalidDependency(ext, dep)

    def run_extension(self, name, extension, repo, uri, db):
        printout("Executing extension %s", (name,))
        try:
            extension.run(repo, uri, db)
        except ExtensionRunError, e:
            printerr("Error running extension %s: %s", (name, str(e)))
            return False

        return True

    def run_extension_deps(self, deps, repo, uri, db, done):
        result = True
        for dep in deps:

            if dep in done:
                continue

            if self.exts[dep].deps:
                result = self.run_extension_deps(self.exts[dep].deps, repo, uri, db, done)

            if not result:
                break

            result = self.run_extension(dep, self.exts[dep](), repo, uri, db)
            done.append(dep)

        return result

    def run_extensions(self, repo, uri, db):
        done = []
        for name, extension in [(ext, self.exts[ext]()) for ext in self.exts]:
            if name in done:
                continue
            done.append(name)

            result = True
            result = self.run_extension_deps(extension.deps, repo, uri, db, done)

            if not result:
                printout("Skipping extension %s since one or more of its dependencies failed", (name,))
                continue

            self.run_extension(name, extension, repo, uri, db)

    def load_all_extensions(self):
        extensions = {}
        dir = os.path.dirname(os.path.realpath(__file__))
        for files in os.listdir(dir + "/extensions"):
            if files.endswith(".py"):
                ext = files[:-3]
                try:
                    extensions[ext] = get_extension(ext)
                except ExtensionUnknownError:
                    # Do nothing here, because we ignore errors during showing "help" ;)
                    pass

        return extensions.keys()
