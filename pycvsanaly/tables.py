# Copyright (C) 2006 Alvaro Navarro Clemente
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
# Authors : Alvaro Navarro <anavarro@gsyc.escet.urjc.es>

"""
Tables definitions. (dictionary format)

@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro@gsyc.escet.urjc.es
"""


comments = {'identifier':'int(8) not null',
            'email': 'varchar(30)',
            'title': 'varchar(40)',
            'comment':'text',
            'date_posted': 'datetime',
            'time_posted': 'time',
            'primary key': 'identifier'}

files = {'file_id':'int(8) NOT NULL',
         'module_id': 'int(8) NOT NULL',
         'name':'varchar(128)',
         'creation_date ':'datetime NOT NULL',
         'last_modification':'datetime NOT NULL',
         'size':'int(8)',
         'filetype':'int(1)',
         'repopath':'tinytext',
         'primary key':'file_id'}

modules = { 'module_id': 'int(8) NOT NULL',
                'module': 'varchar(64) NOT NULL',
                'primary key': 'module_id'}

commiters = {'commiter_id':'int(8) unsigned NOT NULL',
             'commiter':'varchar(60)',
             'primary key':'commiter_id'}

commiters_module = {'commiter_id':'int(8) NOT NULL',
                    'module_id':'int(8) NOT NULL',
                    'primary key': 'commiter_id, module_id'}

log = {'commit_id':'int(8) NOT NULL',
       'file_id': 'int(8) NOT NULL',
       'commiter_id': 'int(8) NOT NULL',
       'revision': 'varchar(16)',
       'plus':'int(8)',
       'minus':'int(8)',
       'cvs_flag':'int(1)',
       'external':'int(1)',
       'date_log':'datetime NOT NULL',
       'filetype':'int(1)',
       'module_id':'int(8)',
       'repopath':'tinytext',
       'intrunk':'int(1)',
       'removed':'bool',
       'primary key':'commit_id'}


cvsanal_fileTypes = {'fileType_id': 'int(1) unsigned NOT NULL',
                     'fileType': 'char(16) NOT NULL',
                     'primary key':'fileType_id'}


cvsanal_temp_commiters = {'commiter_id': 'int(8) NOT NULL',
                          'commits': 'int(8) unsigned NOT NULL',
                          'plus' : 'int(8) unsigned NOT NULL',
                          'minus': 'int(8) unsigned NOT NULL',
                          'files' : 'int(8) unsigned NOT NULL',
                          'filetype' : 'int(1) NOT NULL',
                          'removedCommits' :'int(8) NOT NULL',
                          'removedFiles':'int(8) NOT NULL',
                          'external':'int(8) NOT NULL',
                          'cvs_flag':'int(8) NOT NULL',
                          'first_commit':'datetime NOT NULL',
                          'last_commit':'datetime NOT NULL',
                          'module_id':'int(8)'}

cvsanal_temp_modules = {'module_id':'int(8) unsigned NOT NULL',
                        'module':'char(128) NOT NULL',
                        'commiters':'int(8) unsigned NOT NULL',
                        'commits':'int(8) unsigned NOT NULL',
                        'plus':'int(8) unsigned NOT NULL',
                        'minus':'int(8) unsigned NOT NULL',
                        'files':'int(8) unsigned NOT NULL',
                        'cvs_flag':'int(8) unsigned NOT NULL',
                        'external':'int(8) unsigned NOT NULL',
                        'removedCommits':'int(8) unsigned NOT NULL',
                        'removedFiles':'int(8) NOT NULL',
                        'filetype':'char(16) NOT NULL',
                        'first_commit':'datetime NOT NULL',
                        'last_commit':'datetime NOT NULL'}

cvsanal_temp_inequality = {'module_id int(8)': 'unsigned NOT NULL',
                           'filetype':'int(1) NOT NULL',
                           'gini':'float(8) unsigned',
                           'concentration':'float(8) unsigned',
                           'eu':'float(8) unsigned',
                           'atkinson':'float(8) unsigned',
                           'theil':'float(8) unsigned',
                           'reserve':'float(8) unsigned',
                           'd_and_r':'float(8) unsigned',
                           'kullback_liebler':'float(8) unsigned',
                           'hoover':'float(8) unsigned',
                           'coulter':'float(8) unsigned',
                           'herfindahl':'int(5) unsigned'}


cvsanal_modrequest =  {'request_id':'int(8) unsigned NOT NULL',
                       'commit_id':'int(8) unsigned NOT NULL'}
