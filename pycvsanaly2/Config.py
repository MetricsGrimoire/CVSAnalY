# Copyright (C) 2007  GSyC/LibreSoft
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

class ErrorLoadingConfig (Exception):

    def __init__ (self, message = None):
        Exception.__init__ (self)
        
        self.message = message

class Config:

    __shared_state = { 'debug'        : False,
                       'quiet'        : False,
                       'profile'      : False,
                       'repo_logfile' : None,
                       'save_logfile' : None, 
                       'lines'        : True,
                       'db_driver'    : 'sqlite',
                       'db_user'      : 'operator',
                       'db_password'  : None, 
                       'db_database'  : 'cvsanaly',
                       'db_hostname'  : 'localhost',
                       'extensions'   : [],
                       # Metrics xxtension options
                       'metrics_all'  : False}
    
    def __init__ (self):
        self.__dict__ = self.__shared_state
        
    def __getattr__ (self, attr):
        return self.__dict__[attr]

    def __setattr__ (self, attr, value):
        self.__dict__[attr] = value

    def __load_from_file (self, config_file):
        try:
            from types import ModuleType
            config = ModuleType ('cvsanaly-config')
            f = open (config_file, 'r')
            exec f in config.__dict__
            f.close ()
        except Exception, e:
            raise ErrorLoadingConfig ("Error reading config file %s (%s)" % (config_file, str (e)))

        try:
            self.debug = config.debug
        except:
            pass
        try:
            self.quiet = config.quiet
        except:
            pass        
        try:
            self.profile = config.profile
        except:
            pass
        try:
            self.repo_logfile = config.repo_logfile
        except:
            pass
        try:
            self.save_logfile = config.save_logfile
        except:
            pass
        try:
            self.lines = config.lines
        except:
            pass
        try:
            self.db_driver = config.db_driver
        except:
            pass
        try:
            self.db_user = config.db_user
        except:
            pass
        try:
            self.db_password = config.db_password
        except:
            pass
        try:
            self.db_database = config.db_database
        except:
            pass
        try:
            self.db_hostname = config.db_hostname
        except:
            pass
        try:
            self.extensions.extend ([item for item in config.extensions if item not in self.extensions])
        except:
            pass
        try:
            self.metrics_all = config.metrics_all
        except:
            pass

    def load (self):
        import os

        # First look in /etc
        # FIXME /etc is not portable
        config_file = os.path.join ('/etc', 'cvsanaly')
        if os.path.isfile (config_file):
            self.__load_from_file (config_file)

        # Then look at $HOME
        config_file = os.path.join (os.environ.get ('HOME'), '.cvsanaly')
        if os.path.isfile (config_file):
            self.__load_from_file (config_file)

    def load_from_file (self, path):
        self.__load_from_file (path)
         
