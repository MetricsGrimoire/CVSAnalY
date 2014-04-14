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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import sys
import re
import os
import errno

from Config import Config

config = Config()


def to_utf8(string):
    if isinstance(string, unicode):
        return string.encode('utf-8')
    elif isinstance(string, str):
        for encoding in ['ascii', 'utf-8', 'iso-8859-15']:
            try:
                s = unicode(string, encoding)
            except:
                continue
            break
        return s.encode('utf-8')
    else:
        return string


def to_unicode(string):
    """Converts a string type to an object of unicode type.

    Gets an string object as argument, and tries several
    encoding to convert it to unicode. It basically tries
    encodings in sequence, until one of them doesn't raise
    an exception, since conversion into unicode using a
    given encoding raises an exception of one unknown character
    (for that encoding) is found.

    The string should usually be of str type (8-bit encoding),
    and the returned object is of unicode type.
    If the string is already of unicode type, just return it."""

    if isinstance(string, unicode):
        return string
    elif isinstance(string, str):
        encoded = False
        for encoding in ['ascii', 'utf-8', 'iso-8859-15']:
            try:
                uni_string = unicode(string, encoding)
            except:
                continue
            encoded = True
            break
        if encoded:
            return uni_string
        else:
            # All conversions failed, get unicode with unknown characters
            return (unicode(string, errors='replace'))
    else:
        raise TypeError("string should be of str type")


def uri_is_remote(uri):
    match = re.compile("^.*://.*$").match(uri)
    if match is None:
        return False
    else:
        return not uri.startswith("file://")


def uri_to_filename(uri):
    if uri_is_remote(uri):
        return None

    if uri.startswith("file://"):
        return uri[uri.find("file://") + len("file://"):]

    return uri


def printout(str='\n', args=None):
    if config.quiet:
        return

    if args is not None:
        str = str % tuple(to_utf8(arg) for arg in args)

    if str != '\n':
        str += '\n'
    sys.stdout.write(to_utf8(str))
    sys.stdout.flush()


def printerr(str='\n', args=None):
    if args is not None:
        str = str % tuple(to_utf8(arg) for arg in args)

    if str != '\n':
        str += '\n'
    sys.stderr.write(to_utf8(str))
    sys.stderr.flush()


def printdbg(str='\n', args=None):
    if not config.debug:
        return

    printout("DBG: " + str, args)


def remove_directory(path):
    if not os.path.exists(path):
        return

    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))

    os.rmdir(path)


_dirs = {}


def cvsanaly_dot_dir():
    try:
        return _dirs['dot']
    except KeyError:
        pass

    dot_dir = os.path.join(os.environ.get('HOME'), '.cvsanaly2')
    create_directory(dot_dir)

    _dirs['dot'] = dot_dir

    return dot_dir


def cvsanaly_cache_dir():
    try:
        return _dirs['cache']
    except KeyError:
        pass

    cache_dir = os.path.join(cvsanaly_dot_dir(), 'cache')
    create_directory(cache_dir)

    _dirs['cache'] = cache_dir

    return cache_dir


def create_directory(path):
    try:
        os.makedirs(path, 0700)
    except OSError, e:
        if e.errno == errno.EEXIST:
            if not os.path.isdir(path):
                raise
        else:
            raise


def set_writable_path_from_config(context, path):
    if context == 'cache':
        path_postfix = os.path.join('.cvsanaly2', context)
    elif context == 'dot':
        path_postfix = '.cvsanaly2'
    else:
        raise TypeError("foo")

    directory = os.path.join(path, path_postfix)
    create_directory(directory)
    _dirs[context] = directory


if __name__ == '__main__':
    print cvsanaly_dot_dir()
    print cvsanaly_cache_dir()
