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


from pycvsanaly.libcvsanaly import CVSAnaly

__all__ = [
    'CVSAnalyPlugin',
    'register_plugin',
    'create_plugin',
    'scan_plugins'
]

class PluginUnknownError (Exception):
    '''Unknown pugin'''

    def __init__ (self):
        Exception.__init__ (self)
    
class CVSAnalyPlugin:
    
    def __init__ (self):
        self.ca = None

    def usage (self):
        raise NotImplementedError
        
    def run (self, ca):
        raise NotImplementedError


_plugins = {}
def register_plugin (plugin_name, plugin_class):
    _plugins[plugin_name] = plugin_class

def _get_plugin_class (plugin_name):
    if plugin_name not in _plugins:
        try:
            __import__ ('pycvsanaly.plugins.%s' % plugin_name)
        except ImportError:
            raise

    if plugin_name not in _plugins:
        raise PluginUnknownError ('Unknown plugin %s' % plugin_name)

    return _plugins[plugin_name]

def create_plugin (plugin_name, opts = []):
    plugin_class = _get_plugin_class (plugin_name)
    return plugin_class (opts)

_known_plugins = ['html', 'evolution']
def scan_plugins ():
    # TODO: scan path looking for plugins
    return _known_plugins
