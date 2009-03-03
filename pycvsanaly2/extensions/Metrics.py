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
#       Carlos Garcia Campos  <carlosgc@gsyc.escet.urjc.es>

# Description
# -----------
# This extension calculates some metrics for all the different
# versions of all the files stored in the control version system.
#

from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists,
                                  statement, DBFile)
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.Config import Config
from pycvsanaly2.utils import printdbg, printerr, printout, remove_directory
from pycvsanaly2.FindProgram import find_program
from pycvsanaly2.profile import profiler_start, profiler_stop
from tempfile import mkdtemp
from FilePaths import FilePaths
from xml.sax import handler as xmlhandler, make_parser
import os
import commands
import re

class Repository:

    class SkipFileException (Exception):
        '''Raised when the file has not been checked out because
        it should be skipped'''
    
    def __init__ (self, db, cursor, repo, uri, rootdir):
        self.db = db
        self.cursor = cursor
        self.repo = repo
        self.repo_uri = uri
        self.rootdir = rootdir
        
        cursor.execute (statement ("SELECT id from repositories where uri = ?", db.place_holder), (uri,))
        self.repo_id = cursor.fetchone ()[0]
        
    def get_repo_id (self):
        return self.repo_id
        
    def checkout (self, path, rev):
        raise NotImplementedError

class SVNRepository (Repository):

    def __init__ (self, db, cursor, repo, uri, rootdir):
        Repository.__init__ (self, db, cursor, repo, uri, rootdir)
        self.tops = {}
        
        self.repo.checkout ('.', self.rootdir, newdir=".", rev='0')

    def checkout (self, path, rev):
        root = self.repo_uri.replace (self.repo.get_uri (), '').strip ('/')

        if not os.path.isdir (os.path.join (self.rootdir, root)):
            roots = root.split ('/')

            for i, dummy in enumerate (roots):
                rpath = '/'.join (roots[:i + 1])
                self.repo.update (os.path.join (self.rootdir, rpath), rev=rev, force=True)
        
        path = path.replace (root, '')
        top = path.strip ('/').split ('/')[0]
        
        # skip tags dir
        if top == 'tags':
            raise Repository.SkipFileException
        
        last_rev = self.tops.get (top, 0)
        if last_rev != rev:
            self.repo.update (os.path.join (self.rootdir, root, top), rev=rev, force=True)
            self.tops[top] = rev

class CVSRepository (Repository):

    def __init__ (self, db, cursor, repo, uri, rootdir):
        Repository.__init__ (self, db, cursor, repo, uri, rootdir)

    def checkout (self, path, rev):
        self.repo.checkout (path, self.rootdir, rev=rev)

        
def create_repository (db, cursor, repo, uri, rootdir):
    if repo.get_type () == 'svn':
        return SVNRepository (db, cursor, repo, uri, rootdir)
    elif repo.get_type () == 'cvs':
        return CVSRepository (db, cursor, repo, uri, rootdir)
    else:
        raise NotImplementedError

class ProgramNotFound (Extension):

    def __init__ (self, program):
        self.program = program

class Measures:

    def __init__ (self):
        self.__dict__ = {
            'lang'           : 'unknown',
            'loc'            : None,
            'sloc'           : None,
            'ncomment'       : None,
            'lcomment'       : None,
            'lblank'         : None,
            'nfunctions'     : None,
            'mccabe_max'     : None,
            'mccabe_min'     : None,
            'mccabe_sum'     : None,
            'mccabe_mean'    : None,
            'mccabe_median'  : None,
            'halstead_length': None,
            'halstead_vol'   : None,
            'halstead_level' : None,
            'halstead_md'    : None,
        }

    def __getattr__ (self, name):
        return self.__dict__[name]

    def __setattr__ (self, name, value):
        self.__dict__[name] = value

    def getattrs (self):
        return self.__dict__.keys ()

class FileMetrics:

    def __init__ (self, path, lang='unknown', sloc=0):
        self.path = path
        self.lang = lang
        self.sloc = sloc
    
    def get_LOC (self):
        """Measures LOC using Python file functions"""
        
        fileobj = open (self.path, 'r')
        loc = len (fileobj.readlines ())
        fileobj.close ()
        
        return loc

    def get_SLOCLang (self):
        return self.sloc, self.lang

    def get_CommentsBlank (self):
        raise NotImplementedError

    def get_HalsteadComplexity (self):
        raise NotImplementedError

    def get_MccabeComplexity (self):
        raise NotImplementedError

    def _get_mccabe_stats (nfunctions, mccabe_values):
        # There is a mccabe value for each function
        # This calculates some summary statistics for that set of
        # values
        mccabe_sum = sum (mccabe_values)
        if nfunctions >= 1:
            mccabe_mean = mccabe_sum / nfunctions
            
        mccabe_min = min (mccabe_values)
        mccabe_max = max (mccabe_values)

        # Calculate median
        mccabe_values.sort ()
        if nfunctions == 1:
            mccabe_median = mccabe_mean
        elif nfunctions >= 2:
            n = len (mccabe_values)
            if nfunctions & 1:
                mccabe_median = mccabe_values[n // 2]
            else:
                mccabe_median = (mccabe_values[n // 2 - 1] + mccabe_values[n // 2]) / 2

        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median
    
    _get_mccabe_stats = staticmethod (_get_mccabe_stats)
    
class FileMetricsC (FileMetrics):
    """Measures McCabe's complexity, Halstead's complexity,
    comment and blank lines, using the 'metrics' package by Brian
    Renaud, stored in the Libresoft's subversion repository."""
    
    def get_CommentsBlank (self):
        kdsi = find_program ('kdsi')
        if kdsi is None:
            raise ProgramNotFound ('kdsi')
        
        # Running kdsi
        kdsicmd = kdsi + " " + self.path
        outputtext = commands.getoutput (kdsicmd)
        # Get rid of all the spaces and get a list
        output_values = [x for x in outputtext.split (' ') if '' != x]
        # sloc will be ignored, but it is also generated by the tool
        dummy, blank_lines, comment_lines, comment_number, dummy = output_values

        return comment_number, comment_lines, blank_lines

    def get_HalsteadComplexity (self):
        halstead = find_program ('halstead')
        if halstead is None:
            raise ProgramNotFound ('halstead')
        
        # Running halstead
        halsteadcmd = halstead + " " + self.path
        outputtext = commands.getoutput (halsteadcmd)
        values = outputtext.split ('\t')

        filename = values[0]
        try:
            halstead_length = int (values[1])
        except:
            halstead_length = None
        try:
            halstead_volume = int (values[2])
        except:
            halstead_volume = None
        try:
            halstead_level = float (values[3].replace (',', '.'))
            if str (halstead_level) == str (float ('inf')) \
                or str (halstead_level) == str (float ('nan')):
                    halstead_level = None
        except:
            halstead_level = None
        try:
            halstead_md = int (values[4])
        except:
            halstead_md = None

        return halstead_length, halstead_volume, halstead_level, halstead_md

    def get_MccabeComplexity (self):
        mccabe = find_program ('mccabe')
        if mccabe is None:
            raise ProgramNotFound ('mccabe')
        
        # Running mccabe
        mccabecmd = mccabe + " -n " + self.path
        # The output of this tool is multiline (one line per function)
        outputlines = commands.getoutput (mccabecmd).split ('\n')
        mccabe_values = []
        nfunctions = 0
        mccabe_sum = mccabe_min = mccabe_max = mccabe_mean = mccabe_median = None
        for l in outputlines:
            values = l.split ('\t')
            if len (values) != 5:
                continue

            try:
                mccabe = int (values[-2])
            except:
                mccabe = 0
                
            nfunctions += 1
            mccabe_values.append (mccabe)

        if mccabe_values:
            mccabe_sum, mccabe_min, mccabe_max, \
                mccabe_mean, mccabe_median = self._get_mccabe_stats (nfunctions, mccabe_values)
        else:
            nfunctions = None
            
        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median, nfunctions
                

class FileMetricsPython (FileMetrics):

    patterns = {}
    patterns['numComments'] = re.compile ("^[ \b\t]+([0-9]+)[ \b\t]+numComments$")
    patterns['mccabe'] = re.compile ("^[ \b\t]+([0-9]+)[ \b\t]+(.*)$")
    
    def __init__ (self, path, lang='unknown', sloc=0):
        FileMetrics.__init__ (self, path, lang, sloc)

        self.pymetrics = None

    def __ensure_pymetrics (self):
        if self.pymetrics is not None:
            return

        self.pymetrics = find_program ('pymetrics')
        if self.pymetrics is None:
            raise ProgramNotFound ('pymetrics')
        
    def get_CommentsBlank (self):
        self.__ensure_pymetrics ()

        command = self.pymetrics + ' -C -S -i simple:SimpleMetric ' + self.path
        outputlines = commands.getoutput (command).split ('\n')
        comment_number = comment_lines = blank_lines = None
        for line in outputlines:
            m = self.patterns['numComments'].match (line)
            if m:
                comment_lines = m.group (1)
                continue
                
        return comment_number, comment_lines, blank_lines
    
    def get_MccabeComplexity (self):
        self.__ensure_pymetrics ()

        command = self.pymetrics + ' -C -S -B -i mccabe:McCabeMetric ' + self.path
        outputlines = commands.getoutput (command).split ('\n')
        mccabe_values = []
        nfunctions = 0
        mccabe_sum = mccabe_min = mccabe_max = mccabe_mean = mccabe_median = None
        for line in outputlines:
            m = self.patterns['mccabe'].match (line)
            if m:
                nfunctions += 1
                try:
                    mccabe = int (m.group (1))
                except:
                    mccabe = 0
                mccabe_values.append (mccabe)

        if mccabe_values:
            mccabe_sum, mccabe_min, mccabe_max, \
                mccabe_mean, mccabe_median = self._get_mccabe_stats (nfunctions, mccabe_values)
        else:
            nfunctions = None
                
        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median, nfunctions                              

class FileMetricsCCCC (FileMetrics):
    # Abstract class
    
    cccc_lang = None
    
    class XMLMetricsHandler (xmlhandler.ContentHandler):
        
        def __init__ (self):
            self.comment_lines = 0
            self.nfunctions = 0
            self.mccabe_values = []

            self.current = None

        def startElement (self, name, attributes):
            if name == 'project_summary':
                self.current = name
            elif name == 'lines_of_comment' and self.current == 'project_summary':
                self.comment_lines = int (attributes['value'])
            elif name == 'module':
                self.current = name
                self.nfunctions += 1
            elif name == 'McCabes_cyclomatic_complexity' and self.current == 'module':
                self.mccabe_values.append (int (attributes['value']))
                
        def endElement (self, name):
            if name == 'project_summary' or name == 'module':
                self.current = None
    
    def __init__ (self, path, lang='unknown', sloc=0):
        FileMetrics.__init__ (self, path, lang, sloc)

        self.handler = None

    def __ensure_handler (self):
        if self.handler is not None:
            return

        cccc = find_program ('cccc')
        if cccc is None:
            raise ProgramNotFound ('cccc')

        tmpdir = mkdtemp ()
        
        command = cccc + ' --outdir=' + tmpdir + ' --lang=' + self.cccc_lang + ' ' + self.path
        status, dummy = commands.getstatusoutput (command)

        self.handler = FileMetricsCCCC.XMLMetricsHandler ()
        fd = open (os.path.join (tmpdir, 'cccc.xml'), 'r')

        parser = make_parser ()
        parser.setContentHandler (self.handler)
        parser.feed (fd.read ())

        fd.close ()

        remove_directory (tmpdir)

    def get_CommentsBlank (self):
        self.__ensure_handler ()

        return None, self.handler.comment_lines, None

    def get_MccabeComplexity (self):
        self.__ensure_handler ()

        mccabe_sum = mccabe_min = mccabe_max = mccabe_mean = mccabe_median = None
        nfunctions = self.handler.nfunctions
        if self.handler.mccabe_values:
            mccabe_sum, mccabe_min, mccabe_max, \
                mccabe_mean, mccabe_median = self._get_mccabe_stats (self.handler.nfunctions, self.handler.mccabe_values)
        else:
            nfunctions = None
                
        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median, nfunctions                                      
    
class FileMetricsCPP (FileMetricsCCCC):

    cccc_lang = 'c++'

class FileMetricsJava (FileMetricsCCCC):

    cccc_lang = 'java'


_metrics = {
    "unknown" : FileMetrics,
    "ansic"   : FileMetricsC,
    "python"  : FileMetricsPython,
    "cpp"     : FileMetricsCPP,
    "java"    : FileMetricsJava
}
    
def create_file_metrics (path):
    """Measures SLOC and identifies programming language using SlocCount"""

    sloc = 0
    lang = 'unknown'
    
    sloccount = find_program ('sloccount')
    if sloccount is not None:
        sloccountcmd = sloccount + ' --wide --details ' + path
        outputlines = commands.getoutput (sloccountcmd).split ('\n')

        for l in outputlines:
            # If there is not 'top_dir', then ignore line
            if '\ttop_dir\t' in l:
                sloc, lang, unused1, unused2 = l.split ('\t')

            # If no line with 'top_dir' is found, that means
            # that SLOC is 0 and lang is unknown
        
    fm = _metrics.get (lang, FileMetrics)
    return fm (path, lang, sloc)

class Metrics (Extension):

    deps = ['FileTypes']

    # Insert query
    __insert__ = 'INSERT INTO metrics (id, file_id, commit_id, lang, sloc, loc, ncomment, ' + \
                 'lcomment, lblank, nfunctions, mccabe_max, mccabe_min, mccabe_sum, mccabe_mean, ' + \
                 'mccabe_median, halstead_length, halstead_vol, halstead_level, halstead_md) ' + \
                 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    MAX_METRICS = 100

    def __init__ (self):
        self.db = None
        self.config = Config ()
        self.metrics = []
    
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
                cursor.close ()
                raise TableAlreadyExists
            except:
                raise
        elif isinstance (self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute ("CREATE TABLE metrics (" +
                                "id integer primary key not null," +
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
                    cursor.close ()
                    raise TableAlreadyExists
                raise
            except:
                raise
            
        cnn.commit ()
        cursor.close ()

    def __get_metrics (self, cnn):
        cursor = cnn.cursor ()
        cursor.execute (statement ("SELECT file_id, commit_id from metrics", self.db.place_holder))
        metrics = [(res[0], res[1]) for res in cursor.fetchall ()]
        cursor.close ()
        
        return metrics

    def __insert_many (self, cursor):
        if not self.metrics:
            return
        
        cursor.executemany (statement (self.__insert__, self.db.place_holder), self.metrics)
        self.metrics = []
        
    def run (self, repo, uri, db):
        profiler_start ("Running Metrics extension")
        
        self.db = db

        fp = FilePaths (db)
        
        cnn = self.db.connect ()
        id_counter = 1
        metrics = []

        try:
            self.__create_table (cnn)
        except TableAlreadyExists:
            cursor = cnn.cursor ()
            cursor.execute (statement ("SELECT max(id) from metrics", db.place_holder))
            id = cursor.fetchone ()[0]
            if id is not None:
                id_counter = id + 1
            cursor.close ()

            metrics = self.__get_metrics (cnn)
        except Exception, e:
            raise ExtensionRunError (str(e))

        read_cursor = cnn.cursor ()
        write_cursor = cnn.cursor ()

        # Temp dir for the checkouts
        tmpdir = mkdtemp ()

        try:
            rp = create_repository (db, read_cursor, repo, uri, tmpdir)
        except NotImplementedError:
            raise ExtensionRunError ("Metrics extension is not supported for %s repositories" % (repo.get_type ()))
        except Exception, e:
            raise ExtensionRunError ("Error creating repository %s. Exception: %s" % (repo.get_uri (), str (e)))
            
        repoid = rp.get_repo_id ()
            
        # Obtain files and revisions
        
        if self.config.metrics_all:
            query = "select s.rev rev, s.id commit_id, ft.file_id file_id, composed_rev " + \
                    "from scmlog s, actions a, action_files af, file_types ft " + \
                    "where s.id = a.commit_id and a.id = af.action_id and " + \
                    "af.file_id = ft.file_id and ft.type in ('code', 'unknown') " + \
                    "and a.type in ('A', 'M', 'R') and s.repository_id = ? " + \
                    "order by s.id"
        else:
            query = "select s.rev rev, s.id commit_id, head.file_id file_id, composed_rev " + \
                    "from scmlog s, (" + \
                    "select af.action_id action_id, mlog.file_id file_id, mlog.commit_id commit_id " + \
                    "from action_files af, file_types ft, (" + \
                    "select file_id, max(commit_id) commit_id " + \
                    "from action_files group by file_id" + \
                    ") mlog where mlog.file_id = af.file_id " + \
                    "and mlog.commit_id = af.commit_id and " + \
                    "ft.file_id = mlog.file_id and " + \
                    "ft.type in ('code', 'unknown') " + \
                    "and af.action_type in ('A', 'M', 'R')" + \
                    ") head where head.commit_id = s.id " + \
                    "and s.repository_id = ? " + \
                    "order by s.id"

        read_cursor.execute (statement (query, db.place_holder), (repoid,))
        for revision, commit_id, file_id, composed in read_cursor.fetchall ():
            if (file_id, commit_id) in metrics:
                continue
                
            if composed:
                rev = revision.split ("|")[0]
            else:
                rev = revision

            aux_cursor = cnn.cursor ()
            relative_path = fp.get_path (aux_cursor, file_id, commit_id, repoid).strip ("/")
            printdbg ("Path for %d at %s -> %s", (file_id, rev, relative_path))
            aux_cursor.close ()

            if repo.get_type () == 'svn' and relative_path == 'tags':
                printdbg ("Skipping file %s", (relative_path,))
                continue

            try:
                printdbg ("Checking out %s @ %s", (relative_path, rev))
                rp.checkout (relative_path, rev)
            except Repository.SkipFileException:
                printdbg ("Skipping file %s", (relative_path,))
                continue
            except Exception, e:
                printerr ("Error obtaining %s@%s. Exception: %s", (relative_path, rev, str (e)))
            
            checkout_path = os.path.join (tmpdir, relative_path)
            # FIXME: is this still possible?
            if os.path.isdir (checkout_path):
                printdbg ("Skipping file %s", (relative_path,))
                continue

            if not os.path.exists (checkout_path):
                printerr ("Error measuring %s@%s. File not found", (checkout_path, rev))
                continue
                
            fm = create_file_metrics (checkout_path)
                    
            # Measure the file
            printdbg ("Measuring %s @ %s", (checkout_path, rev))
            measures = Measures ()

            profiler_start ("[LOC] Measuring %s @ %s", (checkout_path, rev))
            try:
                measures.loc = fm.get_LOC ()
            except Exception, e:
                printerr ('Error running loc for %s@%s. Exception: %s', (checkout_path, rev, str (e)))
            profiler_stop ("[LOC] Measuring %s @ %s", (checkout_path, rev))

            profiler_start ("[SLOC] Measuring %s @ %s", (checkout_path, rev))
            try:
                measures.sloc, measures.lang = fm.get_SLOCLang ()
            except ProgramNotFound, e:
                printout ('Program %s is not installed. Skipping sloc metric', (e.program, ))
            except Exception, e:
                printerr ('Error running sloc for %s@%s. Exception: %s', (checkout_path, rev, str (e)))
            profiler_stop ("[SLOC] Measuring %s @ %s", (checkout_path, rev))

            profiler_start ("[CommentsBlank] Measuring %s @ %s", (checkout_path, rev))
            try:
                measures.ncomment, measures.lcomment, measures.lblank = fm.get_CommentsBlank ()
            except NotImplementedError:
                pass
            except ProgramNotFound, e:
                printout ('Program %s is not installed. Skipping CommentsBlank metric', (e.program, ))
            except Exception, e:
                printerr ('Error running CommentsBlank for %s@%s. Exception: %s', (checkout_path, rev, str (e)))
            profiler_stop ("[CommentsBlank] Measuring %s @ %s", (checkout_path, rev))

            profiler_start ("[HalsteadComplexity] Measuring %s @ %s", (checkout_path, rev))
            try:
                measures.halstead_length, measures.halstead_vol, \
                    measures.halstead_level, measures.halstead_md = fm.get_HalsteadComplexity ()
            except NotImplementedError:
                pass
            except ProgramNotFound, e:
                printout ('Program %s is not installed. Skipping halstead metric', (e.program, ))
            except Exception, e:
                printerr ('Error running cmetrics halstead for %s@%s. Exception: %s', (checkout_path, rev, str (e)))
            profiler_stop ("[HalsteadComplexity] Measuring %s @ %s", (checkout_path, rev))
                
            profiler_start ("[MccabeComplexity] Measuring %s @ %s", (checkout_path, rev))
            try:
                measures.mccabe_sum, measures.mccabe_min, measures.mccabe_max, \
                    measures.mccabe_mean, measures.mccabe_median, \
                    measures.nfunctions = fm.get_MccabeComplexity ()
            except NotImplementedError:
                pass
            except ProgramNotFound, e:
                printout ('Program %s is not installed. Skipping mccabe metric', (e.program, ))
            except Exception, e:
                printerr ('Error running cmetrics mccabe for %s@%s. Exception: %s', (checkout_path, rev, str(e)))
            profiler_stop ("[MccabeComplexity] Measuring %s @ %s", (checkout_path, rev))

            self.metrics.append ((id_counter, file_id, commit_id, measures.lang, measures.sloc, measures.loc,
                                  measures.ncomment, measures.lcomment, measures.lblank, measures.nfunctions,
                                  measures.mccabe_max, measures.mccabe_min, measures.mccabe_sum, measures.mccabe_mean,
                                  measures.mccabe_median, measures.halstead_length, measures.halstead_vol,
                                  measures.halstead_level, measures.halstead_md))

            if len (self.metrics) >= self.MAX_METRICS:
                profiler_start ("Inserting results in db")
                self.__insert_many (write_cursor)
                cnn.commit ()
                profiler_stop ("Inserting results in db")
                    
            id_counter += 1

        profiler_start ("Inserting results in db")
        self.__insert_many (write_cursor)
        cnn.commit ()
        profiler_stop ("Inserting results in db")

        # Clean tmpdir
        # TODO: how long would this take? 
        remove_directory (tmpdir)

        read_cursor.close ()
        write_cursor.close ()
        cnn.close()
        
        profiler_stop ("Running Metrics extension")

register_extension ("Metrics", Metrics)
