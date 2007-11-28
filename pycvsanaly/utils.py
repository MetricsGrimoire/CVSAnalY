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
#       Gregorio Robles <grex@gsyc.escet.urjc.es>

from pycvsanaly.config_files import *

def uri_is_remote (uri):
    import re

    match = re.compile ("^.*://.*$").match (uri)
    if match is None:
        return False
    else:
        return not uri.startswith ("file://")

def uri_to_filename (uri):
    if uri_is_remote (uri):
        return None

    if uri.startswith ("file://"):
        return uri[uri.find ("file://") + len ("file://"):]

    return uri

def get_file_type (path):
    """
    Given a filename, returns what type of file it is.
    The file type is set in the config_files configuration file
    and usually this depends on the extension, although other
    simple heuristics are used.

    @type  file: string
    @param file: filename
    
    @rtype: string
    @return: file type id (see config_files_names for transformation into their names: documentation => 0, etc.)
    """
    i = 0
    for fileTypeSearch_list in config_files_list:
        for searchItem in fileTypeSearch_list:
            if searchItem.search (path.lower ()):
                return i
        i += 1

    # if not found, specify it as unknown
    return config_files_names.index ('unknown')

