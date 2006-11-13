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

"""
Abastract class that implements basic methods to work with
repositories

@author:       Alvaro Navarro and Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro,grex@gsyc.escet.urjc.es
"""

import os
import sys
import re

from commiter import Commiter
from directory import *
from files import File
from commit import Commit
from config_files import *

file_properties = {'file_id':'',
                   'name': '',
                   'filetype' :'',
                   'creation_date': '',
                   'last_modification': '',
                   'module_id':'',
                   'size':'',
                   'fileraw':''}

directory_properties = {'module_id':'',
                        'module':''}

commit_properties = {'commit_id':'',
                     'file_id':'',
                     'commiter_id':'',
                     'revision':'',
                     'plus':'',
                     'minus':'',
                     'inattic':'',
                     'cvs_flag':'',
                     'external':'',
                     'date_log':'',
                     'filetype':'',
                     'module_id':'',
                     'fileraw':'',
                     'intrunk':''}

class RepositoryFactory:
    """
    Basic Factory that abastracts the process to create new repositories
    """
    def create(type):
        if type.upper() == "CVS":
            return RepositoryCVS()
        if type.upper() == "SVN":
            return RepositorySVN()

    # We make it static
    create = staticmethod(create)


class Repository:
    """
    Generic class with basic information
    """

    def __init__(self):
        pass

    def log(self):
        pass

    def analyseFile(self,file):
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
                        if searchItem.search(file.lower()):
                                return i
                i+=1
        # if not found, specify it as unknown
        return config_files_names.index('unknown')

    def isFileInAttic(self,file):
        """
        Looks if a given file is in the Attic
        
        In CVS a file is in the Attic if it has been removed from the
        working copy
       
        @type  file: string
        @param file: name of the file
        
        @rtype: int (boolean)
        @return: 1 if file is in Attic, else 0
        """
        if re.compile('/Attic/').search(file):
            return 1
        else:
            return 0

    def countLOCs(self,filename):
        """
        CVS does not count the initial length of a file that is imported
        into the repository. In order to have a real picture a measure
        of the file size at a given time is needed.

        This function returns (if possible) the current size of the
        file in LOC (_with_ comments and blank lines) as wc would do
        In order to have the length for the imported version all the
        changes will have to be added (if removed lines) or subtracted
        (added lines)

        @type  filename: string
        @param filename: Name of the file that should be counted

        @rtype: int
        @return: number of LOCs
        """
        try:
                result = len(open(filename).readlines())
        except IOError:
                result = 0
        return result

    def commiters2sql(self, db, comms):
        """
        @type  db: Database object
        @param db: Object that represents connection with a database

        @type comms: dictionary
        @param comms: list of commiters
        """
        for co in comms:
            query = "INSERT INTO commiters (commiter_id, commiter) VALUES ('"
            query += str(comms[co]) + "','" + str(co) + "');"

            db.insertData(query)


class RepositoryCVS(Repository):
    """
    Child Class that implements CVS Repository basic access
    """

    def __init__(self):
        pass

    def log(self, db, logfile=''):

        if logfile:
            linelog = open(logfile,'r')
        else:
            linelog = os.popen3 ('/usr/bin/cvs -z9 -Q log -N .')

        filename = ''
        dirname = ''
        commitername = ''
        modificationdate = ''
        revision = ''
        plus = ''
        minus = ''
        sum_plus = 0
        sum_minus = 0
        inAttic = 0
        isbinary =0
        cvs_flag= 0
        newcommit = 0
        external = 0
        checkin= 0

        authors = {}

        f = None
        c = None
	d = Directory()

        while 1:
            if logfile:
                line = linelog.readline()
            else:
                line = linelog[1].readline()
            if not line:
                break
            else:
                line = line[:-1]
                pattern0 = re.compile("^RCS file: (.*)")
                pattern1 = re.compile("^Working file: (.*)")
                pattern2 = re.compile("^keyword substitution: b")
                pattern3 = re.compile("^revision ([\d\.]*)")
                pattern4 = re.compile("^date: (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d:\d\d:\d\d)(.*);  author: (.*);  state: (.*);  lines: \+(\d*) -(\d*)")
                pattern5 = re.compile("^date: (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d:\d\d:\d\d)(.*);  author: (.*);  state: ")
                pattern6 = re.compile("^CVS_SILENT")
                pattern7 = re.compile("patch(es)?\s?.* from |patch(es)?\s?.* by |patch(es)?\s.*@|@.* patch(es)?|'s.* patch(es)?|s' .* patch(es)?|patch(es)? of | <.* [Aa][Tt] .*>| attached to #")
                pattern8 = re.compile("^----------------------------")
                pattern9 = re.compile("^========================================")

                mobj0 = pattern0.match(line)
                if mobj0:
                    inAttic = self.isFileInAttic(mobj0.group(1))
                    isbinary = 0
                    cvs_flag = 0
                    revision = ''
                    sum_plus = 0
                    sum_minus = 0
                    external = 0
                    plus = '0'
                    minus = '0'
                    modificationdate = ''
                    creationdate = ''
                    filepath = ''
                    newcommit = 0

                mobj1 = pattern1.match(line)
                if mobj1:

                    # Directory and File
                    fileraw = mobj1.group(1)
                    fileraw = fileraw.replace("'","\\'")

                    filename = fileraw.split('/')[-1]
                    filepath = fileraw[:-len(filename)]
                    filetype = self.analyseFile(filename)

                    if not filepath:
                        filepath = '/'
                    d.add_directory(filepath)
                    print fileraw

                    file_properties['name'] = filename
                    file_properties['filetype'] = filetype
                    file_properties['module_id'] = str(d.get_id(filepath))
                    file_properties['filetype'] = filetype
                    file_properties['fileraw'] = fileraw

                    f = File()

                    newcommit = 1

                mobj2 = pattern2.match(line)
                if mobj2:
                    isbinary = 1

                mobj3 = pattern3.match(line)
                if mobj3:
                    revision = mobj3.group(1)

                mobj4 = pattern4.match(line)
                mobj5 = pattern5.match(line)
                if mobj4 or mobj5:

                    if not filepath:
                        filepath = '/'

                    # Commiter and Date
                    if mobj4:
                        year       = mobj4.group(1)
                        month      = mobj4.group(2)
                        day        = mobj4.group(3)
                        rest_date  = mobj4.group(4)
                    else:
                        year       = mobj5.group(1)
                        month      = mobj5.group(2)
                        day        = mobj5.group(3)
                        rest_date  = mobj5.group(4)

                    commit_date = (year + "-" + month + "-" + day + " " + rest_date)

                    if not modificationdate:
                        modificationdate = commit_date
                    creationdate = commit_date

                    # Create new Commiter objects
                    if mobj4:
                        commitername =  mobj4.group(6)
                    else:
                        commitername =  mobj5.group(6)

                    if not authors.has_key(commitername):
                        authors[commitername] = len(authors)

                    if mobj4:
                        plus       = mobj4.group(8)
                        minus      = mobj4.group(9)
                        sum_plus  += int(plus)
                        sum_minus += int(minus)

                    if isbinary:
                        plus = "0"
                        minus = "0"

                mobj6 = pattern6.match(line)
                if mobj6:
                    cvs_flag = 1

                mobj7 = pattern7.match(line)
                if mobj7:
                    external = 1

                mobj8 = pattern8.match(line)
                mobj9 = pattern9.match(line)

                if mobj8 or mobj9:
                    if revision != "1.1.1.1" and revision != "" and newcommit:
                        if not modificationdate:
                            modificationdate = creationdate

                        # Find out if revision is in main trunk (revision is like x.y)
                        if str(revision).count(".") > 1:
                            intrunk = "0"
                        else:
                            intrunk = "1"
                        

			# Add commit
                        commit_properties['file_id'] = str(f.get_id())
                        commit_properties['commiter_id'] = str(authors[commitername])
                        commit_properties['revision'] = str(revision)
                        commit_properties['plus'] = str(plus)
                        commit_properties['minus'] = str(minus)
                        commit_properties['inattic'] = str(inAttic)
                        commit_properties['cvs_flag'] = str(cvs_flag)
                        commit_properties['external'] = str(external)
                        commit_properties['date_log'] = str(creationdate)
                        commit_properties['filetype'] = str(filetype)
                        commit_properties['module_id'] = str(d.get_id(filepath))
                        commit_properties['fileraw'] = str(fileraw)
                        commit_properties['intrunk'] = str(intrunk)
			c = Commit ()
                        c.add_properties (db, commit_properties)

                if mobj9:
                    if newcommit:
                        if not isbinary and not inAttic:
                            checkin = self.countLOCs(filepath + "/" + filename)
                            checkin = checkin - sum_plus + sum_minus
		            if checkin < 0: checkin = 0
                            plus    = str(checkin)
                            minus   = "0"

                        # Add file
                        file_properties['size'] = str(checkin)
                        file_properties['creation_date'] = str(creationdate)
                        file_properties['last_modification'] = str(modificationdate)
                        f.add_properties (db,file_properties)
                        newcommit = 0

        try:
            # Directories
            d.directory2sql(db)
            # Commiters
            self.commiters2sql(db,authors)
        except:
            sys.exit("Cannot get log! Maybe this is not a CVS working directory or you are having problems with your connection\n")

        if logfile:
            linelog.close()

class RepositorySVN(Repository):
    """
    Child Class that implements SVN Repository basic access
    """

    def __init__(self):
        pass

    def get_fileid(self, mfiles, filename):
        for f in mfiles:
            if filename == f:
                return mfiles[f][0]
                break

    def files2sql(self, mfiles, db):
        for f in mfiles:
            id = mfiles[f][0]
            properties_dict = mfiles[f][1]

            query = "INSERT INTO files (file_id, module_id, name, creation_date, last_modification, size, filetype) "
            query += " VALUES ('" + str(id) + "','"
            query += str(properties_dict['module_id']) + "','"
            query += str(properties_dict['name']) + "','"
            query += str(properties_dict['creation_date']) + "','"
            query += str(properties_dict['last_modification']) + "','"
            query += str(properties_dict['size']) + "','"
            query += str(properties_dict['filetype']) + "');"

            db.insertData(query)

    def print_files(self, files):
        for f in files:
            print str(files[f][0]) + "\t" + str(files[f][1])

    def _getNextLine(self, logfile, linelog):

        if logfile:
            line = linelog.readline()
        else:
            line = linelog[1].readline()
            #print "Line:", line[:-1]
        return line


    def log(self, db, logfile=''):
        """

        """

        if logfile:
            linelog = open(logfile, 'r')
        else:
            linelog = os.popen3 ('/usr/bin/svn --verbose log .')

        fileList = []
        dirname = ''
        commitername = ''
        modificationdate = ''
        revision = ''
        linesComment = ''

        authors = {}

        commits = []
        mfiles = {}

        f = None
        c = None
        d = Directory()

        while 1:
            line = self._getNextLine(logfile, linelog)
            if not line:
                break
            else:
                line = line[:-1]
                pattern0 = re.compile("^r(\d*) \| (.*) \| (\d\d\d\d)[/-](\d\d)[/-](\d\d) (\d\d:\d\d:\d\d) ([+-]\d\d\d\d) \(.*\) \| (.*) line")

                mobj0 = pattern0.match(line)
                if mobj0:
                    fileList     = []
                    revision     = mobj0.group(1)
                    commitername = mobj0.group(2)
                    year         = mobj0.group(3)
                    month        = mobj0.group(4)
                    day          = mobj0.group(5)
                    rest_date    = mobj0.group(6)
                    timezone     = mobj0.group(7)
                    linesComment = mobj0.group(8)

                    #print revision, commitername, year, month, day, rest_date, timezone, linesComment

                    creationdate = (year + "-" + month + "-" + day + " " + rest_date)
                    if not authors.has_key(commitername):
                        authors[commitername] = len(authors)

                    ######
                    # Let's look at affected files
                    # First line: throw it away
                    line = self._getNextLine(logfile, linelog)
                    # But not the other lines
                    moreFiles = True
                    while moreFiles:
                        line = self._getNextLine(logfile, linelog)
                        if line[:5] == '   M ' or line[:5] == '   A ' or line[:5] == '   D ':
                            line = line.split()
                            modification = line[0]
                            fileraw      = line[1]
                            moreFiles = True
                            fileList.append((fileraw, modification))
                            print fileraw
                        else:
                            moreFiles = False

                    ######
                    # Let's look at the attached comment

                    comment = ''
                    for index in range(int(linesComment)):
                        comment += self._getNextLine(logfile, linelog).replace('\n', ' ')
                    # Removing trailing and other spaces
                    comment = ' '.join(comment.split())
                    #print "Comment: '" + comment + "'"

                    ######
                    ######
                    # Parsing complete!
                    # Now feeding our objects with the data

                    # Directory and File
                    for fileTuple in fileList:
                        fileraw = fileTuple[0]
                        type = fileTuple[1]

                        fileraw = fileraw.replace("'","\\'")

                        filename = fileraw.split('/')[-1]
                        filepath = fileraw[:-len(filename)]
                        filetype = self.analyseFile(filename)

                        if not filepath:
                            filepath = '/'
                        d.add_directory(filepath)

                        file_properties['name'] = filename
                        file_properties['filetype'] = filetype
                        file_properties['module_id'] = str(d.get_id(filepath))
                        file_properties['filetype'] = filetype
                        file_properties['size'] = '' # TODO
                        file_properties['creation_date'] = str(creationdate)
                        file_properties['last_modification'] = str(modificationdate)

                        if not mfiles.has_key(fileraw):
                            properties = file_properties.copy()
                            mfiles[fileraw] = (len(mfiles), properties)

                        commit_properties['file_id'] = str(self.get_fileid(mfiles, fileraw))
                        commit_properties['commiter_id'] = str(authors[commitername])
                        commit_properties['revision'] = str(revision)
                        commit_properties['plus'] = 0           # No plus in SVN logs
                        commit_properties['minus'] = 0          # No plus in SVN logs
                        commit_properties['inattic'] = ''       # TODO
                        commit_properties['cvs_flag'] = ''      # TODO
                        commit_properties['external'] = ''      # TODO
                        commit_properties['date_log'] = str(creationdate)
                        commit_properties['filetype'] = str(filetype)
                        commit_properties['module_id'] = str(d.get_id(filepath))
                        c = Commit ()
                        c.add_properties (db, commit_properties)


        # FIXME: modification and bug fixing on the way! grx
        #    SVN commits are not CVS commits, they are transactions!
        #    Files are considered differently!!
        try:
            # Files
            self.files2sql(mfiles, db)
            # Directories
            d.directory2sql(db)
            # Commiters
            self.commiters2sql(db,authors)
        except:
            sys.exit("Cannot get log! maybe this is not a SVN working directory or you are having problems with your connection\n")

        if logfile:
            linelog.close()

