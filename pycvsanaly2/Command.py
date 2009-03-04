# Command.py
#
# Copyright (C) 2007 Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
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

import os
import select
import subprocess
import sys
import errno
from signal import SIGINT, SIGTERM

class CommandError (Exception):

    def __init__ (self, msg, returncode = None):
        Exception.__init__ (self, msg)
        self.returncode = returncode

class CommandRunningError (Exception):
    def __init__ (self, msg, error):
        Exception.__init__ (self, msg)
        self.error = error

class CommandTimeOut (Exception):
    '''Timeout running command'''

class Command:

    SELECT_TIMEOUT = 2
    
    def __init__ (self, command, cwd = None, env = None):
        self.cmd = command
        self.cwd = cwd
        self.env = env

        self.process = None

    def _read (self, fd, buffsize):
        while True:
            try:
                return os.read (fd, buffsize)
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                else:
                    raise

    def _write (self, fd, s):
        while True:
            try:
                return os.write (fd, s)
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                else:
                    raise

    def _read_from_pipes (self, stdin = None, out_data_cb = None, err_data_cb = None, timeout = None):
        p = self.process
        
        read_set = [p.stdout, p.stderr]
        write_set = []

        if stdin is not None:
            p.stdin.flush ()
            write_set.append (p.stdin)
        
        if out_data_cb is None:
            out_data = ""
        else:
            out_data = None

        if err_data_cb is None:
            err_data = ""
        else:
            err_data = None

        if timeout is not None:
            elapsed = 0.0

        input_offset = 0
        try:
            while read_set or write_set:
                try:
                    rlist, wlist, xlist = select.select (read_set, write_set, [], self.SELECT_TIMEOUT)
                except select.error, e:
                    # Ignore interrupted system call, reraise anything else
                    if e.args[0] == errno.EINTR:
                        continue
                    raise

                if rlist == wlist == []:
                    if err_data:
                        raise CommandRunningError ("Error during executioin of %s" % (str (self.cmd)), err_data)
                    if timeout is not None:
                        elapsed += self.SELECT_TIMEOUT
                        if elapsed >= timeout:
                            os.kill (p.pid, SIGTERM)
                            raise CommandTimeOut
                elif timeout is not None:
                    # reset timeout
                    elapsed = 0.0
                    
                if p.stdin in wlist:
                    bytes_written = self._write (p.stdin.fileno (), buffer (stdin, input_offset, 512))
                    input_offset += bytes_written
                    if input_offset >= len (stdin):
                        p.stdin.close ()
                        write_set.remove (p.stdin)
                
                if p.stdout in rlist:
                    out_chunk = self._read (p.stdout.fileno (), 1024)
                    if out_chunk == "":
                        p.stdout.close ()
                        read_set.remove (p.stdout)

                    if out_data_cb is None:
                        out_data += out_chunk
                    else:
                        out_data_cb[0] (out_chunk, out_data_cb[1])
                    
                if p.stderr in rlist:
                    err_chunk = self._read (p.stderr.fileno (), 1024)
                    
                    if err_chunk == "":
                        p.stderr.close ()
                        read_set.remove (p.stderr)

                    if err_data_cb is None:
                        err_data += err_chunk
                    else:
                        err_data_cb[0] (err_chunk, err_data_cb[1])
                    
        except KeyboardInterrupt:
            try:
                os.kill (p.pid, SIGINT)
            except OSError:
                pass

        ret = p.wait ()
        self.process = None
        
        return out_data, err_data, ret

    def _get_process (self):
        if self.process is not None:
            return self.process
        
        kws = { 'close_fds': True,
                'stdout'   : subprocess.PIPE,
                'stderr'   : subprocess.PIPE,
                'stdin'    : subprocess.PIPE,
                'env'      : os.environ.copy ()
        }

        if self.cwd is not None:
            kws['cwd'] = self.cwd

        if self.env is not None:
            kws['env'].update (self.env)

        try:
            self.process = subprocess.Popen (self.cmd, **kws)
        except OSError, e:
            raise CommandError (str (e))

        return self.process
    
    def run_sync (self, stdin = None, timeout = None):
        self.process = self._get_process ()

        out = self._read_from_pipes (stdin, timeout = timeout)[0]
        
        self.process = None

        return out
        
    def run (self, stdin = None, parser_out_func = None, parser_error_func = None, timeout = None):
        self.process = self._get_process ()

        def out_cb (out_chunk, out_data_l):
            out_data = out_data_l[0]
            out_data += out_chunk
            while '\n' in out_data:
                pos = out_data.find ('\n')
                if parser_out_func is not None:
                    parser_out_func (out_data[:pos + 1])
                else:
                    sys.stdout.write (out_data[:pos + 1])
                out_data = out_data[pos + 1:]
            out_data_l[0] = out_data

        def err_cb (err_chunk, err_data_l):
            err_data = err_data_l[0]
            err_data += err_chunk
            while '\n' in err_data:
                pos = err_data.find ('\n')
                if parser_error_func is not None:
                    parser_error_func (err_data[:pos + 1])
                else:
                    sys.stderr.write (err_data[:pos + 1])
                err_data = err_data[pos + 1:]
            err_data_l[0] = err_data
        
        out_data = [""]
        err_data = [""]
        ret = self._read_from_pipes (stdin, (out_cb, out_data), (err_cb, err_data), timeout)[2]

        if ret != 0:
            raise CommandError ('Error running %s' % self.cmd, ret)

if __name__ == '__main__':
    # Valid command without cwd
    cmd = Command (['ls', '-l'])
    cmd.run ()

    # Valid command with cwd
    def out_func (line):
        print "LINE: %s" % (line)
    cmd = Command (['ls', '-lh'], '/')
    cmd.run (parser_out_func = out_func)

    # Invalid command
    cmd = Command ('invalid')
    try:
        cmd.run ()
    except CommandError, e:
        print 'Command not found (%s)' % (str (e))

    # Run sync
    cmd = Command (['ls'], '/tmp/')
    print cmd.run_sync ()

    cmd = Command (['svn', 'info', 'https://svn.apache.org/repos/asf/activemq/trunk'])
    try:
        print cmd.run_sync ()
    except CommandRunningError, e:
        print cmd.run_sync ('p\n')

    # Timeout
    cmd = Command (['sleep', '100'])
    try:
        cmd.run (timeout=2)
    except CommandTimeOut:
        pass
