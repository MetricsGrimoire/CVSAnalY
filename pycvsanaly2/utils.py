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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import sys

from Config import Config

config = Config ()

def to_utf8 (string):
    if isinstance (string, unicode):
        return string.encode ('utf-8')

    for encoding in ['ascii', 'utf-8', 'iso-8859-15']:
        try:
            s = unicode (string, encoding)
        except:
            continue
        break
        
    return s.encode ('utf-8')

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

def printout (str = '\n', args = None):
    if config.quiet:
        return

    if args is not None:
        str = str % args
    
    if str != '\n':
        str += '\n'
    sys.stdout.write (str)
    sys.stdout.flush ()

def printerr (str = '\n', args = None):
    if args is not None:
        str = str % args
    
    if str != '\n':
        str += '\n'
    sys.stderr.write (str)
    sys.stderr.flush ()

def printdbg (str = '\n', args = None):
    if not config.debug:
        return

    printout ("DBG: " + str, args)
