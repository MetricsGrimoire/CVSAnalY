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

__all__ = ['Extension', 'get_extension', 'register_extension']


class ExtensionUnknownError(Exception):
    '''Unkown extension'''


class ExtensionRunError(Exception):
    '''Error running extension'''


class Extension:
    deps = []

    def run(self, repo, uri, db):
        raise NotImplementedError


_extensions = {}


def register_extension(extension_name, extension_class):
    _extensions[extension_name] = extension_class


def get_extension(extension_name):
    if extension_name not in _extensions:
        try:
            __import__("pycvsanaly2.extensions.%s" % extension_name)
        except ImportError as e:
            raise ExtensionUnknownError(e.message)

    # If the file can be loaded, but no register_extension() is called
    # this is not a valid extension. Raise an ExtensionUnknownError
    if extension_name not in _extensions:
        raise ExtensionUnknownError("Extension %s unknown" % extension_name)

    return _extensions[extension_name]
