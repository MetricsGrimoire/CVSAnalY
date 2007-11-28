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
from signal import SIGINT

class CommandError (Exception):

    def __init__ (self, msg, returncode = None):
        Exception.__init__ (self, msg)
        self.returncode = returncode

class Command:

    def __init__ (self, command, cwd = None, env = None):
        self.cmd = command
        self.cwd = cwd
        self.env = env

    def run (self, parser_out_func = None, parser_error_func = None, stdin = None):
        kws = { 'close_fds': True,
                'stdin'    : subprocess.PIPE,
                'stdout'   : subprocess.PIPE,
                'stderr'   : subprocess.PIPE,
                'env'      : os.environ.copy ()
        }

        if self.cwd is not None:
            kws['cwd'] = self.cwd

        if self.env is not None:
            kws['env'].update (self.env)

        try:
            p = subprocess.Popen (self.cmd, **kws)
        except OSError, e:
            raise CommandError (str (e))


        if stdin is not None:
            p.stdin.write (stdin)
        
        read_set = [p.stdout, p.stderr]
        
        out_data = err_data = ''
        try:
            while read_set:
                rlist, wlist, xlist = select.select (read_set, [], [])

                if p.stdout in rlist:
                    out_chunk = os.read (p.stdout.fileno (), 1024)
                    if out_chunk == '':
                        p.stdout.close ()
                        read_set.remove (p.stdout)
                    out_data += out_chunk
                    
                    while '\n' in out_data:
                        pos = out_data.find ('\n')
                        if parser_out_func is not None:
                            parser_out_func (out_data[:pos + 1])
                        else:
                            sys.stdout.write (out_data[:pos + 1])
                        out_data = out_data[pos + 1:]
        
                if p.stderr in rlist:
                    err_chunk = os.read (p.stderr.fileno (), 1024)
                    
                    if err_chunk == '':
                        p.stderr.close ()
                        read_set.remove (p.stderr)
                    err_data += err_chunk
                    
                    while '\n' in err_data:
                        pos = err_data.find ('\n')
                        if parser_error_func is not None:
                           parser_error_func (err_data[:pos + 1])
                        else:
                            sys.stderr.write (out_data[:pos + 1])
                        err_data = err_data[pos + 1:]
        
                select.select ([],[],[],.1) # give a little time for buffers to fill
                
        except KeyboardInterrupt:
            try:
                os.kill (p.pid, SIGINT)
            except OSError:
                pass

        if p.wait () != 0:
            raise CommandError ('Error running %s' % self.cmd, p.returncode)


if __name__ == '__main__':
    # Valid command without cwd
    cmd = Command (['ls', '-l'])
    cmd.run ()

    # Valid command with cwd
    cmd = Command (['ls', '-lh'], '/')
    cmd.run ()

    # Invalid command
    cmd = Command ('invalid')
    try:
        cmd.run ()
    except CommandError, e:
        print 'Command not found (%s)' % (str (e))

