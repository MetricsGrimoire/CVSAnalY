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
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

from Parser import ContentHandler
from Repository import *
from files import SQLFile
from commit import SQLCommit

file_properties = {'file_id':'',
                   'name': '',
                   'filetype' :'',
                   'creation_date': '',
                   'last_modification': '',
                   'module_id':'',
                   'size':'',
                   'repopath':''}

directory_properties = {'module_id':'',
                        'module':''}

commit_properties = {'commit_id':'',
                     'file_id':'',
                     'commiter_id':'',
                     'revision':'',
                     'plus':'',
                     'minus':'',
                     'cvs_flag':'',
                     'external':'',
                     'date_log':'',
                     'filetype':'',
                     'module_id':'',
                     'repopath':'',
                     'intrunk':'',
                     'removed':''}

#TODO: fill modules table, really?
#I think it's only useful for plugins so they could create a view or something
#Not sure what to do ... 

class DBContentHandler (ContentHandler):

    def __init__ (self, db):
        ContentHandler.__init__ (self)
        self.db = db
        self.level = 0
        
        self.authors = {}
        self.mfiles = {}
        self.mdirectories = {}
        self.modules = []

    def __get_file_id (self, path):
        for f in self.mfiles:
            if path == f:
                return self.mfiles[f]

    def __get_module_id (self, path):
        if path == '/':
            return path
        
        path = path.strip ('/')
        if self.level == -1:
            return path
        
        l = path.split ('/')
        level = len (l)
        
        return "/".join (l[:min (self.level, level)])

    def commit (self, commit):
        for fileTuple in commit.files:
            repopath = fileTuple[1].path
            type = fileTuple[0]

            if type == DELETE:
                removed = '1'
            else:
                removed = '0'
                        
            repopath = repopath.replace("'","\\'")

            filename = repopath.split('/')[-1]
            filepath = repopath[:-len(filename)]
            filetype = fileTuple[1].type

            if not filepath:
                filepath = '/'

        commit_properties['file_id'] = str (self.__get_file_id (repopath))
        commit_properties['commiter_id'] = str (self.authors[commit.commiter])
        commit_properties['revision'] = commit.revision
        commit_properties['plus'] = 0           # No plus in SVN logs
        commit_properties['minus'] = 0          # No plus in SVN logs
        commit_properties['cvs_flag'] = ''      # TODO
        commit_properties['external'] = ''      # TODO
        commit_properties['date_log'] = commit.date
        commit_properties['filetype'] = filetype
        commit_properties['module_id'] = self.mdirectories[filepath]
        commit_properties['removed'] = str(removed)
        c = SQLCommit ()
        c.add_properties (self.db, commit_properties)

    def commiter (self, commiter):
        if not self.authors.has_key (commiter):
            self.authors[commiter] = len (self.authors)
            
            query = "INSERT INTO commiters (commiter_id, commiter) VALUES ('"
            query += str (self.authors[commiter]) + "','" + str(commiter) + "');"
            self.db.insertData (query)
        
    def file (self, file):
        repopath = file.path.replace("'","\\'")

        filename = repopath.split('/')[-1]
        filepath = repopath[:-len(filename)]
        filetype = file.type

        if not filepath:
            filepath = '/'
        if not self.mdirectories.has_key (filepath):
            module = self.__get_module_id (filepath)
            if module not in self.modules:
                self.modules.append (module)
            self.mdirectories[filepath] = self.modules.index (module)
                        
        file_properties['name'] = filename
        file_properties['filetype'] = filetype
        file_properties['module_id'] = self.mdirectories[filepath]
        file_properties['size'] = '' # TODO
        file_properties['creation_date'] = file.cdate
        file_properties['last_modification'] = file.mdate

        if not self.mfiles.has_key (repopath):
            self.mfiles[repopath] = len (self.mfiles)

            query = "INSERT INTO files (file_id, module_id, name, creation_date, last_modification, size, filetype) "
            query += " VALUES ('" + str(self.mfiles[repopath]) + "','"
            query += str(file_properties['module_id']) + "','"
            query += str(file_properties['name']) + "','"
            query += str(file_properties['creation_date']) + "','"
            query += str(file_properties['last_modification']) + "','"
            query += str(file_properties['size']) + "','"
            query += str(file_properties['filetype']) + "');"
            self.db.insertData(query)
