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
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

"""
@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro@gsyc.escet.urjc.es
"""

__all__ = [
        'Plugin', 
        'register_plugin', 
        'get_plugin',
        'scan_plugins'
]

class PluginUnknownError (Exception):
    '''Unknown pugin'''

"""
All plugins should inheritate from this class
"""
class Plugin:

    def __init__ (self, db = None):
        self.author = None
        self.name = None
        self.description = None
        self.date = None
        self.db = db

    def info (self):
        print "Name: %s" % (self.name)
        print "Author(s): %s" % (self.author)
        print "Description: %s" % (self.description)
        print "Last Updated: %s" % (self.date)

    def run (self):
        raise NotImplementedError

    def get_author (self):
        return self.author

    def get_description (self):
        return self.description

    def get_options (self):
        return []

    def usage (self):
        pass

_plugins = {}
def register_plugin (plugin_name, plugin_class):
    _plugins[plugin_name] = plugin_class

def _get_plugin_class (plugin_name):
    if plugin_name not in _plugins:
        try:
            __import__ ('pycvsanaly.plugins.%s' % plugin_name)
        except ImportError:
            pass

    if plugin_name not in _plugins:
        raise PluginUnknownError ('Unknown plugin %s' % plugin_name)

    return _plugins[plugin_name]

def get_plugin (plugin_name, db = None, opts = []):
    plugin_class = _get_plugin_class (plugin_name)
    return plugin_class (db, opts)

def scan_plugins ():
    import sys, os

    list = []

    for path in sys.path:
        dir = os.path.join (path, "pycvsanaly/plugins")
        if os.path.exists (dir) and os.path.isdir (dir):
            root, dirs, files = os.walk (dir).next ()
            for plugin in dirs:
                try:
                    _get_plugin_class (plugin)
                    list.append (plugin)
                except:
                    continue

    return list

