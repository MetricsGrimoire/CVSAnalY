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
# Authors :
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>

# Description
# -----------
# This extension calculates some metrics for all the different
# versions of all the files stored in the control version system.
#
# It needs the FilePaths extension to be called first.

from repositoryhandler.backends import create_repository
from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists,
                                  statement, DBFile)
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.utils import printdbg
from tempfile import mkdtemp
import os
import commands

class Metrics (Extension):

    deps = ['FilePaths']

    def __init__ (self):
        self.db = None
        self.__reposlist = []
    
    def __create_table (self, cnn):
        cursor = cnn.cursor ()

        if isinstance (self.db, SqliteDatabase):
            import pysqlite2.dbapi2
            
            try:
                cursor.execute ("CREATE TABLE metrics (" +
                                "id integer primary key," +
                                "file_id integer," +
                                "commit_id integer," +
                                "lang text," +
                                "sloc integer," +
                                "loc integer," +
                                "ncomment integer," +
                                "lcomment integer," +
                                "lblank integer," +
                                "nfunctions integer," +
                                "mccabe_max integer," +
                                "mccabe_min integer," +
                                "mccabe_sum integer," +
                                "mccabe_mean integer," +
                                "mccabe_median integer," +
                                "halstead_length integer,"+
                                "halstead_vol integer," +
                                "halstead_level double,"+
                                "halstead_md integer" +
                                ")")
            except pysqlite2.dbapi2.OperationalError:
                raise TableAlreadyExists
            except:
                raise
        elif isinstance (self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute ("CREATE TABLE metrics (" +
                                "id integer primary key not null auto_increment," +
                                "file_id integer," +
                                "commit_id integer," +
                                "lang tinytext," +
                                "sloc integer," +
                                "loc integer," +
                                "ncomment integer," +
                                "lcomment integer," +
                                "lblank integer," +
                                "nfunctions integer," +
                                "mccabe_max integer," +
                                "mccabe_min integer," +
                                "mccabe_sum integer," +
                                "mccabe_mean integer," +
                                "mccabe_median integer," +
                                "halstead_length integer,"+
                                "halstead_vol integer," +
                                "halstead_level double,"+
                                "halstead_md integer," +
                                "FOREIGN KEY (file_id) REFERENCES tree(id)," +
                                "FOREIGN KEY (commit_id) REFERENCES scmlog(id)" +
                                ") CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    raise TableAlreadyExists
                raise
            except:
                raise
            
        cnn.commit ()
        cursor.close ()

    def run (self, repo, db):

        self.db = db

        cnn = self.db.connect()

        try:
            self.__create_table (cnn)
        except TableAlreadyExists:
            # Do something
            pass
        except Exception, e:
            raise ExtensionRunError (str(e))

        read_cursor = cnn.cursor()
        write_cursor = cnn.cursor()
        
        # Obtain repository data and create repo object
        query = 'SELECT id, uri, type '
        query += 'FROM repositories'
        
        read_cursor.execute(query)
        rs = read_cursor.fetchone()
        while rs:
            self.__populateRepoList(rs)
            rs = read_cursor.fetchone()

        repobj = None
        repoid = -1
        uri = None
        # Analyze all the repos contained in the db
        for repodata in self.__reposlist:
            repoid, uri, type = repodata
            repobj = create_repository(type,uri)        

            # Temp dir for the checkouts
            tmpdir = mkdtemp()
            
            # Obtain first revision
            query =  'SELECT MIN(rev) '
            query += 'FROM scmlog'
            read_cursor.execute(statement (query, db.place_holder))
            first_rev = read_cursor.fetchone()[0]
            
            # SVN needs the first revision
            if type == 'svn':
                try:
                    repobj.checkout('.', tmpdir, newdir='.', rev=first_rev)
                except Exception, e:
                    msg = 'SVN checkout first rev (%s) failed. Error: %s' % (str(first_rev), 
                                                                             str(e))
                    raise ExtensionRunError (msg)
                printdbg('SVN checkout first rev finished')
            
            # Obtain files and revisions
            query =  'SELECT rev, path, a.commit_id, a.file_id, composed_rev '
            query += 'FROM scmlog s, actions a, file_paths f '
            query += 'WHERE (a.type="M" or a.type="A") '
            query += 'AND a.commit_id=s.id '
            query += 'AND a.file_id=f.id '
            query += 'AND s.repository_id="' + str(repoid) + '"'

            read_cursor.execute (statement (query, db.place_holder))
            rs = read_cursor.fetchone()
            while rs:
                # Obtain file and revision from row
                filepath, revision, file_id, commit_id = self.__extractFileRev(rs)

                # Remove repository url from filepath
                # (all the filepaths begin with the repo URL)

                # Heuristics, depending on the repository
                relative_path = ""
                
                if 'svn' == type:                    
                    try:
                        relative_path = filepath.split(uri)[1]
                    except IndexError:
                        relative_path = filepath
                        
                if 'cvs' == type:                    
                    try:
                        relative_path = filepath.split(uri)[1]
                    except IndexError:
                        relative_path = filepath

                    try:
                        relative_path = filepath.split(uri.split(":")[-1])[1]
                    except IndexError:
                        relative_path = filepath

                printdbg(repobj.uri)
                printdbg(relative_path)

                # Measure files
                measures = self.__measureFile(relative_path,revision,repobj,tmpdir)
                
                # Create SQL Query insert
                fields = ['file_id', 'commit_id']
                values = [str(file_id), str(commit_id)]
                
                for key in measures.keys():
                    fields.append("%s" % str(key))
                    if key == 'lang':
                        values.append("'%s'" % str(measures[key]))
                    else:
                        values.append("%s" % str(measures[key]))
                fields = ','.join(fields)
                values = ','.join(values)
                
                query =  'INSERT INTO metrics '
                query += '(%s) VALUES (%s)' % (fields, values)
                write_cursor.execute(query)
                rs = read_cursor.fetchone()

            # Write everything related to this repo
            cnn.commit()
            # Clean tmpdir

        cnn.close()

    def __populateRepoList(self,rs):
        repo_id, uri, type = rs
        repodata = (repo_id,uri,type)        
        self.__reposlist.append(repodata)
        

    def __extractFileRev(self,rs):
        revision, filepath, commit_id, file_id, composed = rs

        if composed:
            revision = revision.split("|")[0]

        return filepath, revision, file_id, commit_id
            
    def __measureFile(self,filepath,revision,repository,outputdir):

        printdbg("Obtaining "+filepath+" @ "+revision)

        loc = -1
        sloc = -1
        lang = "NULL"
             
        # Download file from repository
        try:
            if repository.get_type() == 'svn':
                repository.update(os.path.join(outputdir, filepath),
                                  rev=revision,force=True)
            else:
                repository.checkout(filepath,outputdir,rev=revision)
                
        except Exception, e:
            printdbg("Error obtaining %s@%s. Exception: %s" % (filepath, revision, str(e)))
            return loc, sloc, lang
            
        checkout_path = os.path.join(outputdir,filepath)

        # Initialize measures
        measures = {
                    'lang'           : 'unknown',
                    'loc'            : -1,
                    'sloc'           : -1,
                    'ncomment'       : -1,
                    'lcomment'       : -1,
                    'lblank'         : -1,
                    'nfunctions'     : -1,
                    'mccabe_max'     : -1,
                    'mccabe_min'     : -1,
                    'mccabe_sum'     : -1,
                    'mccabe_mean'    : -1,
                    'mccabe_median'  : -1,
                    'halstead_length': -1,
                    'halstead_vol'   : -1,
                    'halstead_level' : -1,
                    'halstead_md'    : -1,
                    }
            
        try:
            measures['loc'] = self.__getLOC(checkout_path)
        except Exception, e:
            printdbg('Error loc. Exception: %s' % str(e))
            
        try:
            measures['sloc'], measures['lang'] = self.__getSLOCLang(checkout_path)        
        except Exception, e:
            printdbg('Error sloc. Exception: %s' % str(e))
            
        try:
            if measures['lang'] == 'ansic':
                cmetrics = self.__getCMetrics(checkout_path)
                measures.update(cmetrics)
        except Exception, e:
            printdbg('Error cmetrics. Exception: %s' % str(e))
            
        return measures

    def __getLOC(self,filename):
        """Measures LOC using Python file functions"""
        fileobj = open(filename,'r')
        loc = len(fileobj.readlines())
        fileobj.close()
        return loc

    def __getSLOCLang(self,filename):
        """Measures SLOC and identifies programming language using SlocCount"""

        sloccountcmd = 'sloccount --wide --details '+filename
        outputlines = commands.getoutput(sloccountcmd).split('\n')

        sloc = 0
        lang = 'unknown'
        for l in outputlines:
            # If there is not 'top_dir', then ignore line
            if '\ttop_dir\t' in l:
                sloc, lang, unused1, unused2 = l.split('\t')

            # If no line with 'top_dir' is found, that means
            # that SLOC is 0 and lang is unknown
        
        return sloc, lang

    def __get_CMetrics(self,filename):
        """Measures McCabe's complexity, Halstead's complexity,
        comment and blank lines, using the 'metrics' package by Brian
        Renaud, stored in the Libresoft's subversion repository."""
        
        # This package contains three different tools
        # kdsi, hasltead and mccabe

        # Running kdsi
        kdsicmd = "kdsi "+filename
        outputtext = commands.getoutput(kdsicmd)
        # Get rid of all the spaces and get a list
        output_values = [x for x in outputtext.split(' ') if '' != x]
        # sloc will be ignored, but it is also generated by the tool
        sloc,blank_lines,comment_lines,comment_number,filename = output_values

        # Running halstead
        halsteadcmd = "halstead "+filename
        outputtext = commands.getoutput(halsteadcmd)
        values = outputtext.split('\t')
        try:
            filename, halstead_length, halstead_volume, halstead_level, halstead_md = values
        except ValueError:
            halstead_length = -1
            halstead_volume = -1
            halstead_level = -1
            halstead_md = -1

        # Running mccabe
        mccabecmd = "mccabe "+filename
        # The output of this tool is multiline (one line per function)
        outputlines = commands.getoutput(mccabecmd).split('\n')
        mccabe_total = 0
        mccabe_values = []
        mccabe = 0
        returns = 0
        nfunctions = 0
        for l in outputlines:
            values = l.split('\t')
            mccabe_ok = False
            try:
                if 4 == len(values):
                    mccabe = int(values[-2])
                    nfunctions += 1
                    mccabe_ok = True
                else:
                    mccabe = -1
            except ValueError:
                # If values[-2] or values[-1] is not actually a number
                mccabe = 0
                nfunctions -= 1
                mccabe_ok = False

            if mccabe_ok:
                mccabe_values.append(mccabe)

        # There is a mccabe value for each function
        # This calculates some summary statistics for that set of
        # values
                
        mccabe_sum = sum(mccabe_values)
        if 1 <= nfunctions:
            mccabe_mean = mccabe_sum / nfunctions
        else:
            mccabe_mean = -1
            
        mccabe_min = min(mccabe_values)
        mccabe_max = max(mccabe_values)

        # Calculate median
        mccabe_values.sort()
        if 1 == nfunctions:
            mccabe_median = mccabe_mean
        elif 2 <= nfunctions:
            if nfunctions & 1:
                mccabe_median = mccabe_values[n // 2]
            else:
                mccabe_median = (mccabe_values[n // 2 - 1] + mccabe_values[n // 2]) / 2
        else:
            mccabe_median = -1
        
        # Everything finished
        # Let's return all the needed values
        values = {
                  'lblank'          : blank_lines,
                  'lcomment'        : comment_lines,
                  'ncomment'        : comment_number,
                  'halstead_length' : halstead_length,
                  'halstead_vol'    : halstead_volume,
                  'halstead_level'  : halstead_level,
                  'halstead_md'     : halstead_md,
                  'mccabe_sum'      : mccabe_sum,
                  'mccabe_min'      : mccabe_min,
                  'mccabe_max'      : mccabe_max,
                  'mccabe_mean'     : mccabe_mean,
                  'mccabe_median'   : mccabe_median,
                  'nfunctions'      : nfunctions,
                  }

        return values

    
register_extension("Metrics",Metrics)        
