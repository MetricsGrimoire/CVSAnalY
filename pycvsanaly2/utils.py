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
import re
import os

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

def remove_directory (path):
    if not os.path.exists (path):
        return

    for root, dirs, files in os.walk (path, topdown = False):
        for file in files:
            os.remove (os.path.join (root, file))
        for dir in dirs:
            os.rmdir (os.path.join (root, dir))

    os.rmdir (path)

def get_path_for_revision (current_path, current_file_id, rev, cursor, place_holder):
    from Database import statement
    
    cursor.execute (statement ("select date from scmlog where rev = ?", place_holder), (rev,))
    commit_date = cursor.fetchone ()[0]

    file_id = current_file_id
    old_path = None
    index = len (current_path)
    while index >= 0:
        path = current_path[:index]

        query =  "select old_path, date from actions, scmlog "
        query += "where commit_id = scmlog.id and type = 'V' and file_id = ? and date > ? order by date"
        cursor.execute (statement (query, place_holder), (file_id, commit_date))
        rs = cursor.fetchone ()
        if rs is not None:
            old_path = rs[0]
            break

        cursor.execute (statement ("select parent from tree where id = ?", place_holder), (file_id,))
        file_id = cursor.fetchone ()[0]

        index = current_path.rfind ('/', 0, index)

    if old_path is not None:
        return current_path.replace (path, old_path)

    return current_path

def path_is_deleted_for_revision (path, file_id, rev, cursor, place_holder):
    from Database import statement
    
    cursor.execute (statement ("select date from scmlog where rev = ?", place_holder), (rev,))
    commit_date = cursor.fetchone ()[0]

    fid = file_id

    while fid != -1:
        query =  "select actions.id from actions, scmlog where "
        query += "commit_id = scmlog.id and type = 'D' and file_id = ? and "
        query += "date > ? order by date"
        cursor.execute (statement (query, place_holder), (fid, commit_date))
        rs = cursor.fetchone ()
        if rs is not None:
            return True

        cursor.execute (statement ("select parent from tree where id = ?", place_holder), (fid,))
        fid = cursor.fetchone ()[0]

    return False
