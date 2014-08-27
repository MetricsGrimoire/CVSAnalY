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
# Authors :
#       Israel Herraiz <herraiz@gsyc.escet.urjc.es>
#       Carlos Garcia Campos  <carlosgc@gsyc.escet.urjc.es>

# Description
# -----------
# This extension calculates some metrics for all the different
# versions of all the files stored in the control version system.
#

from pycvsanaly2.Database import (SqliteDatabase, MysqlDatabase, TableAlreadyExists, statement)
from pycvsanaly2.extensions import Extension, register_extension, ExtensionRunError
from pycvsanaly2.Config import Config
from pycvsanaly2.utils import printdbg, printerr, printout, remove_directory, uri_to_filename
from pycvsanaly2.FindProgram import find_program
from pycvsanaly2.profile import profiler_start, profiler_stop
from pycvsanaly2.Command import Command, CommandError, CommandRunningError
from repositoryhandler.backends import RepositoryCommandError
from repositoryhandler.backends.watchers import CAT
from tempfile import mkdtemp, NamedTemporaryFile
from FileRevs import FileRevs
from Jobs import JobPool, Job
from xml.sax import handler as xmlhandler, make_parser
from signal import SIGTERM
import os
import re


class ProgramNotFound(Extension):
    def __init__(self, program):
        self.program = program


class Measures:
    def __init__(self):
        self.__dict__ = {
            'lang': 'unknown',
            'loc': None,
            'sloc': None,
            'ncomment': None,
            'lcomment': None,
            'lblank': None,
            'nfunctions': None,
            'mccabe_max': None,
            'mccabe_min': None,
            'mccabe_sum': None,
            'mccabe_mean': None,
            'mccabe_median': None,
            'halstead_length': None,
            'halstead_vol': None,
            'halstead_level': None,
            'halstead_md': None,
        }

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def getattrs(self):
        return self.__dict__.keys()

    def set_error(self):
        keys = self.__dict__.keys()
        keys.remove('lang')
        for key in keys:
            self.__dict__[key] = -1


class FileMetrics:
    def __init__(self, path, lang='unknown', sloc=0):
        self.path = path
        self.lang = lang
        self.sloc = sloc

    def get_LOC(self):
        """Measures LOC using Python file functions"""

        fileobj = open(self.path, 'r')
        loc = len(fileobj.readlines())
        fileobj.close()

        return loc

    def get_SLOCLang(self):
        return self.sloc, self.lang

    def get_CommentsBlank(self):
        raise NotImplementedError

    def get_HalsteadComplexity(self):
        raise NotImplementedError

    def get_MccabeComplexity(self):
        raise NotImplementedError

    def _get_mccabe_stats(nfunctions, mccabe_values):
        # There is a mccabe value for each function
        # This calculates some summary statistics for that set of
        # values
        mccabe_sum = sum(mccabe_values)
        if nfunctions >= 1:
            mccabe_mean = mccabe_sum / nfunctions

        mccabe_min = min(mccabe_values)
        mccabe_max = max(mccabe_values)

        # Calculate median
        mccabe_values.sort()
        if nfunctions == 1:
            mccabe_median = mccabe_mean
        elif nfunctions >= 2:
            n = len(mccabe_values)
            if nfunctions & 1:
                mccabe_median = mccabe_values[n // 2]
            else:
                mccabe_median = (mccabe_values[n // 2 - 1] + mccabe_values[n // 2]) / 2

        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median

    _get_mccabe_stats = staticmethod(_get_mccabe_stats)


class FileMetricsC(FileMetrics):
    """Measures McCabe's complexity, Halstead's complexity,
    comment and blank lines, using the 'metrics' package by Brian
    Renaud, stored in the Libresoft's subversion repository."""

    kdsi = None
    halstead = None
    mccabe = None

    def get_CommentsBlank(self):
        if self.kdsi is None:
            kdsi = find_program('kdsi')
            if kdsi is None:
                raise ProgramNotFound('kdsi')
            self.kdsi = kdsi
        else:
            kdsi = self.kdsi

        # Running kdsi
        cmd = Command([kdsi, self.path], env={'LC_ALL': 'C'})
        try:
            outputtext = cmd.run()
        except CommandError, e:
            if e.error:
                printerr('Error running kdsi: %s', (e.error,))
            raise e
        except CommandRunningError, e:
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running kdsi: %s', (e.error,))
            raise e
        # Get rid of all the spaces and get a list
        output_values = [x for x in outputtext.split(' ') if '' != x]
        # sloc will be ignored, but it is also generated by the tool
        dummy, blank_lines, comment_lines, comment_number, dummy = output_values

        return comment_number, comment_lines, blank_lines

    def get_HalsteadComplexity(self):
        if self.halstead is None:
            halstead = find_program('halstead')
            if halstead is None:
                raise ProgramNotFound('halstead')
            self.halstead = halstead
        else:
            halstead = self.halstead

        # Running halstead
        cmd = Command([halstead, self.path], env={'LC_ALL': 'C'})
        try:
            outputtext = cmd.run()
        except CommandError, e:
            if e.error:
                printerr('Error running halstead: %s', (e.error,))
            raise e
        except CommandRunningError, e:
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running halstead: %s', (e.error,))
            raise e

        values = outputtext.split('\t')

        filename = values[0]
        try:
            halstead_length = int(values[1])
        except:
            halstead_length = None
        try:
            halstead_volume = int(values[2])
        except:
            halstead_volume = None
        try:
            halstead_level = float(values[3].replace(',', '.'))
            if str(halstead_level) == str(float('inf')) \
                    or str(halstead_level) == str(float('nan')):
                halstead_level = None
        except:
            halstead_level = None
        try:
            halstead_md = int(values[4])
        except:
            halstead_md = None

        return halstead_length, halstead_volume, halstead_level, halstead_md

    def get_MccabeComplexity(self):
        if self.mccabe is None:
            mccabe = find_program('mccabe')
            if mccabe is None:
                raise ProgramNotFound('mccabe')
            self.mccabe = mccabe
        else:
            mccabe = self.mccabe

        # Running mccabe
        cmd = Command([mccabe, '-n', self.path], env={'LC_ALL': 'C'})
        # The output of this tool is multiline (one line per function)
        try:
            outputlines = cmd.run().split('\n')
        except CommandError, e:
            if e.error:
                printerr('Error running mccabe: %s', (e.error,))
            raise e
        except CommandRunningError, e:
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running mccabe: %s', (e.error,))
            raise e

        mccabe_values = []
        nfunctions = 0
        mccabe_sum = mccabe_min = mccabe_max = mccabe_mean = mccabe_median = None
        for l in outputlines:
            values = l.split('\t')
            if len(values) != 5:
                continue

            try:
                mccabe = int(values[-2])
            except:
                mccabe = 0

            nfunctions += 1
            mccabe_values.append(mccabe)

        if mccabe_values:
            mccabe_sum, mccabe_min, mccabe_max, \
                mccabe_mean, mccabe_median = self._get_mccabe_stats(nfunctions, mccabe_values)
        else:
            nfunctions = None

        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median, nfunctions


class FileMetricsPython(FileMetrics):
    patterns = {}
    patterns['numComments'] = re.compile("^[ \b\t]+([0-9]+)[ \b\t]+numComments$")
    patterns['mccabe'] = re.compile("^[ \b\t]+([0-9]+)[ \b\t]+(.*)$")

    pymetrics = None

    def __init__(self, path, lang='unknown', sloc=0):
        FileMetrics.__init__(self, path, lang, sloc)

    def __ensure_pymetrics(self):
        if self.pymetrics is not None:
            return

        self.pymetrics = find_program('pymetrics')
        if self.pymetrics is None:
            raise ProgramNotFound('pymetrics')

    def get_CommentsBlank(self):
        self.__ensure_pymetrics()

        cmd = Command([self.pymetrics, '-C', '-S', '-i', 'simple:SimpleMetric', self.path], env={'LC_ALL': 'C'})
        try:
            outputlines = cmd.run().split('\n')
        except CommandError, e:
            if e.error:
                printerr('Error running pymetrics: %s', (e.error,))
            raise e
        except CommandRunningError, e:
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running pymetrics: %s', (e.error,))
            raise e

        comment_number = comment_lines = blank_lines = None
        for line in outputlines:
            m = self.patterns['numComments'].match(line)
            if m:
                comment_lines = m.group(1)
                continue

        return comment_number, comment_lines, blank_lines

    def get_MccabeComplexity(self):
        self.__ensure_pymetrics()

        cmd = Command([self.pymetrics, '-C', '-S', '-B', '-i', 'mccabe:McCabeMetric', self.path], env={'LC_ALL': 'C'})
        try:
            outputlines = cmd.run().split('\n')
        except CommandError, e:
            if e.error:
                printerr('Error running pymetrics: %s', (e.error,))
            raise e
        except CommandRunningError, e:
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running pymetrics: %s', (e.error,))
            raise e

        mccabe_values = []
        nfunctions = 0
        mccabe_sum = mccabe_min = mccabe_max = mccabe_mean = mccabe_median = None
        for line in outputlines:
            m = self.patterns['mccabe'].match(line)
            if m:
                nfunctions += 1
                try:
                    mccabe = int(m.group(1))
                except:
                    mccabe = 0
                mccabe_values.append(mccabe)

        if mccabe_values:
            mccabe_sum, mccabe_min, mccabe_max, \
                mccabe_mean, mccabe_median = self._get_mccabe_stats(nfunctions, mccabe_values)
        else:
            nfunctions = None

        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median, nfunctions


class FileMetricsCCCC(FileMetrics):
    # Abstract class

    cccc_lang = None
    cccc = None

    class XMLMetricsHandler(xmlhandler.ContentHandler):

        def __init__(self):
            self.comment_lines = 0
            self.nfunctions = 0
            self.mccabe_values = []

            self.current = None

        def startElement(self, name, attributes):
            if name == 'project_summary':
                self.current = name
            elif name == 'lines_of_comment' and self.current == 'project_summary':
                self.comment_lines = int(attributes['value'])
            elif name == 'module':
                self.current = name
                self.nfunctions += 1
            elif name == 'McCabes_cyclomatic_complexity' and self.current == 'module':
                self.mccabe_values.append(int(attributes['value']))

        def endElement(self, name):
            if name == 'project_summary' or name == 'module':
                self.current = None

    def __init__(self, path, lang='unknown', sloc=0):
        FileMetrics.__init__(self, path, lang, sloc)

        self.handler = None

    def __ensure_handler(self):
        if self.handler is not None:
            return

        if self.cccc is None:
            cccc = find_program('cccc')
            if cccc is None:
                raise ProgramNotFound('cccc')
            self.cccc = cccc
        else:
            cccc = self.cccc

        tmpdir = mkdtemp()

        command = [cccc, '--outdir=%s' % tmpdir, '--lang=%s' % self.cccc_lang, self.path]
        cmd = Command(command, env={'LC_ALL': 'C'})
        try:
            cmd.run()
        except CommandError, e:
            if e.error:
                printerr('Error running cccc: %s', (e.error,))
            remove_directory(tmpdir)
            raise e
        except CommandRunningError, e:
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running cccc: %s', (e.error,))
            remove_directory(tmpdir)
            raise e

        self.handler = FileMetricsCCCC.XMLMetricsHandler()
        fd = open(os.path.join(tmpdir, 'cccc.xml'), 'r')

        parser = make_parser()
        parser.setContentHandler(self.handler)
        parser.feed(fd.read())

        fd.close()

        remove_directory(tmpdir)

    def get_CommentsBlank(self):
        self.__ensure_handler()

        return None, self.handler.comment_lines, None

    def get_MccabeComplexity(self):
        self.__ensure_handler()

        mccabe_sum = mccabe_min = mccabe_max = mccabe_mean = mccabe_median = None
        nfunctions = self.handler.nfunctions
        if self.handler.mccabe_values:
            mccabe_sum, mccabe_min, mccabe_max, \
                mccabe_mean, mccabe_median = self._get_mccabe_stats(self.handler.nfunctions, self.handler.mccabe_values)
        else:
            nfunctions = None

        return mccabe_sum, mccabe_min, mccabe_max, mccabe_mean, mccabe_median, nfunctions


class FileMetricsCPP(FileMetricsCCCC):
    cccc_lang = 'c++'


class FileMetricsJava(FileMetricsCCCC):
    cccc_lang = 'java'


_metrics = {
    "unknown": FileMetrics,
    "ansic": FileMetricsC,
    "python": FileMetricsPython,
    "cpp": FileMetricsCPP,
    "java": FileMetricsJava
}

sloccount = find_program('sloccount')


def create_file_metrics(path):
    """Measures SLOC and identifies programming language using SlocCount"""

    sloc = 0
    lang = 'unknown'

    if sloccount is not None:
        profiler_start("Running sloccount %s", (path,))
        tmpdir = mkdtemp()
        scmd = [sloccount, '--wide', '--details', '--datadir', tmpdir, path]
        cmd = Command(scmd, env={'LC_ALL': 'C'})
        try:
            outputlines = cmd.run().split('\n')
            remove_directory(tmpdir)
        except CommandError, e:
            profiler_stop("Running sloccount %s", (path,), True)
            remove_directory(tmpdir)
            if e.error:
                printerr('Error running sloccount: %s', (e.error,))
            raise e
        except CommandRunningError, e:
            profiler_stop("Running sloccount %s", (path,), True)
            remove_directory(tmpdir)
            pid = cmd.get_pid()
            if pid:
                os.kill(pid, SIGTERM)
            printerr('Error running sloccount: %s', (e.error,))
            raise e

        for l in outputlines:
            # If there is not 'top_dir', then ignore line
            if '\ttop_dir\t' in l:
                sloc, lang, unused1, unused2 = l.split('\t')

                # If no line with 'top_dir' is found, that means
                # that SLOC is 0 and lang is unknown
        profiler_stop("Running sloccount %s", (path,), True)

    fm = _metrics.get(lang, FileMetrics)
    return fm(path, lang, sloc)


class MetricsJob(Job):
    def __init__(self, id_counter, file_id, commit_id, path, rev, failed):
        self.id_counter = id_counter
        self.file_id = file_id
        self.commit_id = commit_id
        self.path = path
        self.rev = rev
        self.failed = failed

    def __measure_file(self, fm, measures, checkout_path, rev):
        printdbg("Measuring %s @ %s", (checkout_path, rev))

        profiler_start("[LOC] Measuring %s @ %s", (checkout_path, rev))
        try:
            measures.loc = fm.get_LOC()
        except Exception, e:
            printerr('Error running loc for %s@%s. Exception: %s', (checkout_path, rev, str(e)))
            measures.loc = -1
        profiler_stop("[LOC] Measuring %s @ %s", (checkout_path, rev), True)

        profiler_start("[SLOC] Measuring %s @ %s", (checkout_path, rev))
        try:
            measures.sloc, measures.lang = fm.get_SLOCLang()
        except ProgramNotFound, e:
            printout('Program %s is not installed. Skipping sloc metric', (e.program, ))
        except Exception, e:
            printerr('Error running sloc for %s@%s. Exception: %s', (checkout_path, rev, str(e)))
            measures.sloc = measures.lang = - 1
        profiler_stop("[SLOC] Measuring %s @ %s", (checkout_path, rev), True)

        profiler_start("[CommentsBlank] Measuring %s @ %s", (checkout_path, rev))
        try:
            measures.ncomment, measures.lcomment, measures.lblank = fm.get_CommentsBlank()
        except NotImplementedError:
            pass
        except ProgramNotFound, e:
            printout('Program %s is not installed. Skipping CommentsBlank metric', (e.program, ))
        except Exception, e:
            printerr('Error running CommentsBlank for %s@%s. Exception: %s', (checkout_path, rev, str(e)))
            measures.ncomment = measures.lcomment = measures.lblank = -1
        profiler_stop("[CommentsBlank] Measuring %s @ %s", (checkout_path, rev), True)

        profiler_start("[HalsteadComplexity] Measuring %s @ %s", (checkout_path, rev))
        try:
            measures.halstead_length, measures.halstead_vol, \
                measures.halstead_level, measures.halstead_md = fm.get_HalsteadComplexity()
        except NotImplementedError:
            pass
        except ProgramNotFound, e:
            printout('Program %s is not installed. Skipping halstead metric', (e.program, ))
        except Exception, e:
            printerr('Error running HalsteadComplexity for %s@%s. Exception: %s', (checkout_path, rev, str(e)))
            measures.halstead_length = measures.halstead_vol = measures.halstead_level = measures.halstead_md = -1
        profiler_stop("[HalsteadComplexity] Measuring %s @ %s", (checkout_path, rev), True)

        profiler_start("[MccabeComplexity] Measuring %s @ %s", (checkout_path, rev))
        try:
            measures.mccabe_sum, measures.mccabe_min, measures.mccabe_max, \
                measures.mccabe_mean, measures.mccabe_median, \
                measures.nfunctions = fm.get_MccabeComplexity()
        except NotImplementedError:
            pass
        except ProgramNotFound, e:
            printout('Program %s is not installed. Skipping mccabe metric', (e.program, ))
        except Exception, e:
            printerr('Error running MccabeComplexity for %s@%s. Exception: %s', (checkout_path, rev, str(e)))
            measures.mccabe_sum = measures.mccabe_min = measures.mccabe_max = \
                measures.mccabe_mean = measures.mccabe_median = measures.nfunctions = -1
        profiler_stop("[MccabeComplexity] Measuring %s @ %s", (checkout_path, rev), True)

    def run(self, repo, repo_uri):
        def write_file(line, fd):
            fd.write(line)
        
        self.measures = Measures()
        
        #skip this if self.path is None, this can happen in new versions
        if self.path is None:
            printerr("No path for file %d in commit '%s'", (self.file_id, self.rev))
            return
        
        repo_type = repo.get_type()
        if repo_type == 'cvs':
            # CVS paths contain the module stuff
            uri = repo.get_uri_for_path(repo_uri)
            module = uri[len(repo.get_uri()):].strip('/')

            if module != '.':
                path = self.path[len(module):].strip('/')
            else:
                path = self.path.strip('/')
        else:
            path = self.path.strip('/')

        suffix = ''
        filename = os.path.basename(self.path)
        ext_ptr = filename.rfind('.')
        if ext_ptr != -1:
            suffix = filename[ext_ptr:]

        fd = NamedTemporaryFile('w', suffix=suffix)
        wid = repo.add_watch(CAT, write_file, fd.file)

        if repo_type == 'git':
            retries = 0
        else:
            retries = 3

        done = False
        failed = False
        while not done and not failed:
            try:
                repo.cat(os.path.join(repo_uri, path), self.rev)
                done = True
            except RepositoryCommandError, e:
                if retries > 0:
                    printerr("Command %s returned %d (%s), try again", (e.cmd, e.returncode, e.error))
                    retries -= 1
                    fd.file.seek(0)
                elif retries == 0:
                    failed = True
                    printerr("Error obtaining %s@%s. Command %s returned %d (%s)",
                             (self.path, self.rev, e.cmd, e.returncode, e.error))
            except Exception, e:
                failed = True
                printerr("Error obtaining %s@%s. Exception: %s", (self.path, self.rev, str(e)))

        repo.remove_watch(CAT, wid)
        fd.file.close()

        if failed:
            self.measures.set_error()
        else:
            try:
                fm = create_file_metrics(fd.name)
                self.__measure_file(fm, self.measures, fd.name, self.rev)
            except Exception, e:
                printerr("Error creating FileMetrics for %s@%s. Exception: %s", (fd.name, self.rev, str(e)))
                self.measures.set_error()

        fd.close()

    def get_id(self):
        return self.id_counter

    def get_measures(self):
        return self.measures

    def get_file_id(self):
        return self.file_id

    def get_commit_id(self):
        return self.commit_id

    def is_failed(self):
        return self.failed


class Metrics(Extension):
    deps = ['FileTypes']

    # Insert query
    __insert__ = 'INSERT INTO metrics (id, file_id, commit_id, lang, sloc, loc, ncomment, ' + \
                 'lcomment, lblank, nfunctions, mccabe_max, mccabe_min, mccabe_sum, mccabe_mean, ' + \
                 'mccabe_median, halstead_length, halstead_vol, halstead_level, halstead_md) ' + \
                 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    MAX_METRICS = 100
    INTERVAL_SIZE = 1000

    def __init__(self):
        self.db = None
        self.config = Config()
        self.metrics = []

    def __create_table(self, cnn):
        cursor = cnn.cursor()

        if isinstance(self.db, SqliteDatabase):
            import sqlite3

            try:
                cursor.execute("CREATE TABLE metrics (" +
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
                               "halstead_length integer," +
                               "halstead_vol integer," +
                               "halstead_level double," +
                               "halstead_md integer" +
                               ")")
            except sqlite3.OperationalError:
                cursor.close()
                raise TableAlreadyExists
            except:
                raise
        elif isinstance(self.db, MysqlDatabase):
            import _mysql_exceptions

            try:
                cursor.execute("CREATE TABLE metrics (" +
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
                               "halstead_length integer," +
                               "halstead_vol integer," +
                               "halstead_level double," +
                               "halstead_md integer," +
                               "FOREIGN KEY (file_id) REFERENCES tree(id)," +
                               "FOREIGN KEY (commit_id) REFERENCES scmlog(id)" +
                               ") ENGINE=MyISAM" +
                               " CHARACTER SET=utf8")
            except _mysql_exceptions.OperationalError, e:
                if e.args[0] == 1050:
                    cursor.close()
                    raise TableAlreadyExists
                raise
            except:
                raise

        cnn.commit()
        cursor.close()

    def __get_metrics(self, cursor, repoid):
        query = "select m.file_id, m.commit_id from metrics m, files f " + \
                "where m.file_id = f.id and repository_id = ?"
        cursor.execute(statement(query, self.db.place_holder), (repoid,))
        return [(res[0], res[1]) for res in cursor.fetchall()]

    def __get_metrics_failed(self, cursor, repoid):
        query = "select m.file_id, m.commit_id from metrics m, files f " + \
                "where m.file_id = f.id and repository_id = ? and " + \
                "(sloc = -1 or loc = -1 or " + \
                "ncomment = -1 or lcomment = -1 or " + \
                "lblank = -1 or nfunctions = -1 or " + \
                "mccabe_max = -1 or mccabe_min = -1 or mccabe_sum = -1 or " + \
                "mccabe_mean = -1 or mccabe_median = -1 or " + \
                "halstead_length = -1 or halstead_vol = -1 or " + \
                "halstead_level = -1 or halstead_md = -1)"

        cursor.execute(statement(query, self.db.place_holder), (repoid,))
        return [(res[0], res[1]) for res in cursor.fetchall()]

    def __insert_many(self, cursor):
        if not self.metrics:
            return
        cursor.executemany(statement(self.__insert__, self.db.place_holder), self.metrics)
        self.metrics = []

    def __process_finished_jobs(self, job_pool, write_cursor, unlocked=False):
        if unlocked:
            job = job_pool.get_next_done_unlocked()
        else:
            job = job_pool.get_next_done()

        while job is not None:
            id_counter = job.get_id()
            measures = job.get_measures()
            file_id = job.get_file_id()
            commit_id = job.get_commit_id()

            if job.is_failed():
                query = "update metrics set lang=?, sloc=?, loc=?, " + \
                        "ncomment=?, lcomment=?, lblank=?, nfunctions=?, " + \
                        "mccabe_max=?, mccabe_min=?, mccabe_sum=?, mccabe_mean=?, mccabe_median=?, " + \
                        "halstead_length=?, halstead_vol=?, halstead_level=?, halstead_md=? " + \
                        "where file_id = ? and commit_id = ?"

                write_cursor.execute(statement(query, self.db.place_holder),
                                     (measures.lang, measures.sloc, measures.loc,
                                      measures.ncomment, measures.lcomment, measures.lblank, measures.nfunctions,
                                      measures.mccabe_max, measures.mccabe_min, measures.mccabe_sum,
                                      measures.mccabe_mean,
                                      measures.mccabe_median, measures.halstead_length, measures.halstead_vol,
                                      measures.halstead_level, measures.halstead_md, file_id, commit_id))
            else:
                self.metrics.append((id_counter, file_id, commit_id, measures.lang, measures.sloc, measures.loc,
                                     measures.ncomment, measures.lcomment, measures.lblank, measures.nfunctions,
                                     measures.mccabe_max, measures.mccabe_min, measures.mccabe_sum,
                                     measures.mccabe_mean,
                                     measures.mccabe_median, measures.halstead_length, measures.halstead_vol,
                                     measures.halstead_level, measures.halstead_md))
            if unlocked:
                job = job_pool.get_next_done_unlocked()
            else:
                job = job_pool.get_next_done(0.5)

    def run(self, repo, uri, db):
        profiler_start("Running Metrics extension")

        self.db = db

        cnn = self.db.connect()
        read_cursor = cnn.cursor()
        write_cursor = cnn.cursor()

        id_counter = 1
        metrics = metrics_failed = []

        try:
            path = uri_to_filename(uri)
            if path is not None:
                repo_uri = repo.get_uri_for_path(path)
            else:
                repo_uri = uri

            read_cursor.execute(statement("SELECT id from repositories where uri = ?", db.place_holder), (repo_uri,))
            repoid = read_cursor.fetchone()[0]
        except NotImplementedError:
            raise ExtensionRunError("Metrics extension is not supported for %s repositories" % (repo.get_type()))
        except Exception, e:
            raise ExtensionRunError("Error creating repository %s. Exception: %s" % (repo.get_uri(), str(e)))

        try:
            self.__create_table(cnn)
        except TableAlreadyExists:
            cursor = cnn.cursor()
            if not self.config.metrics_all:
                # HEAD, remove the previous content for the repository
                # FIXME: we could probably improve this case
                query = "DELETE m.* from metrics m, files f " + \
                        "where f.id = m.file_id and " + \
                        "f.repository_id = ?"
                cursor.execute(statement(query, db.place_holder), (repoid,))
                cnn.commit()

            cursor.execute(statement("SELECT max(id) from metrics", db.place_holder))
            id = cursor.fetchone()[0]
            if id is not None:
                id_counter = id + 1

            cursor.close()
        except Exception, e:
            raise ExtensionRunError(str(e))

        if id_counter > 1:
            metrics = self.__get_metrics(read_cursor, repoid)
            metrics_failed = self.__get_metrics_failed(read_cursor, repoid)

        job_pool = JobPool(repo, path or repo.get_uri(), queuesize=self.MAX_METRICS)

        # Get code files to discard all other files in case of metrics-all
        query = "select f.id from file_types ft, files f " + \
                "where f.id = ft.file_id and " + \
                "ft.type in ('code', 'unknown') and " + \
                "f.repository_id = ?"
        read_cursor.execute(statement(query, db.place_holder), (repoid,))
        code_files = [item[0] for item in read_cursor.fetchall()]

        n_metrics = 0
        fr = FileRevs(db, cnn, read_cursor, repoid)

        for revision, commit_id, file_id, action_type, composed in fr:
            if file_id not in code_files:
                continue

            # Ignore actions that do not alter metric values
            if action_type in ('D', 'V'):
                continue

            failed = False

            if (file_id, commit_id) in metrics_failed:
                printdbg("%d@%d is already in the database, but it failed, try again", (file_id, commit_id))
                failed = True
            elif (file_id, commit_id) in metrics:
                printdbg("%d@%d is already in the database, skip it", (file_id, commit_id))
                continue

            try:
                relative_path = fr.get_path(repo, path or repo.get_uri())
            except AttributeError, e:
                if self.config.metrics_noerr:
                    printerr("Error getting path for file %d@%d: %s", (file_id, commit_id, str(e)))
                else:
                    raise e

            if composed:
                rev = revision.split("|")[0]
            else:
                rev = revision

            printdbg("Path for %d at %s -> %s", (file_id, rev, relative_path))

            if repo.get_type() == 'svn' and relative_path == 'tags':
                printdbg("Skipping file %s", (relative_path,))
                continue

            job = MetricsJob(id_counter, file_id, commit_id, relative_path, rev, failed)
            job_pool.push(job)
            id_counter += 1
            n_metrics += 1

            if n_metrics >= self.MAX_METRICS:
                self.__process_finished_jobs(job_pool, write_cursor)
                profiler_start("Inserting results in db")
                self.__insert_many(write_cursor)
                cnn.commit()
                profiler_stop("Inserting results in db")
                n_metrics = 0

        job_pool.join()
        self.__process_finished_jobs(job_pool, write_cursor, True)

        profiler_start("Inserting results in db")
        self.__insert_many(write_cursor)
        cnn.commit()
        profiler_stop("Inserting results in db")

        read_cursor.close()
        write_cursor.close()
        cnn.close()

        profiler_stop("Running Metrics extension", delete=True)


register_extension("Metrics", Metrics)
