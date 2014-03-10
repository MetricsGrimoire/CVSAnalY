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
import errno
from signal import SIGINT, SIGTERM


class CommandError(Exception):
    def __init__(self, cmd, returncode, error=None):
        self.cmd = cmd
        self.returncode = returncode
        self.error = error

    def __str__(self):
        return "Command '%s' returned non-zero exit status %d" % (self.cmd, self.returncode)


class CommandRunningError(Exception):
    def __init__(self, cmd, error):
        self.cmd = cmd
        self.error = error

    def __str__(self):
        return "Error during execution of command %s" % (self.cmd)


class CommandTimeOut(Exception):
    '''Timeout running command'''


class Command:
    SELECT_TIMEOUT = 2

    def __init__(self, command, cwd=None, env=None, error_handler_func=None):
        self.cmd = command
        self.cwd = cwd
        self.env = env
        self.error_handler_func = error_handler_func

        self.process = None

    def set_error_handler(self, error_handler_func):
        self.error_handler_func = error_handler_func

    def _read(self, fd, buffsize):
        while True:
            try:
                return os.read(fd, buffsize)
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                else:
                    raise

    def _write(self, fd, s):
        while True:
            try:
                return os.write(fd, s)
            except OSError, e:
                if e.errno == errno.EINTR:
                    continue
                else:
                    raise

    def _read_from_pipes(self, stdin=None, out_data_cb=None, err_data_cb=None, timeout=None):
        p = self.process

        read_set = [p.stdout, p.stderr]
        write_set = []

        p.stdin.flush()
        if stdin is not None:
            write_set.append(p.stdin)

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
                    rlist, wlist, xlist = select.select(read_set, write_set, [], self.SELECT_TIMEOUT)
                except select.error, e:
                    # Ignore interrupted system call, reraise anything else
                    if e.args[0] == errno.EINTR:
                        continue
                    raise

                if rlist == wlist == []:
                    if err_data:
                        handled = False
                        if self.error_handler_func is not None:
                            handled = self.error_handler_func(self, err_data)
                        if not handled:
                            raise CommandRunningError(self.cmd, err_data)
                    if timeout is not None:
                        elapsed += self.SELECT_TIMEOUT
                        if elapsed >= timeout:
                            os.kill(p.pid, SIGTERM)
                            p.wait()
                            self.process = None
                            raise CommandTimeOut
                elif timeout is not None:
                    # reset timeout
                    elapsed = 0.0

                if p.stdin in wlist:
                    bytes_written = self._write(p.stdin.fileno(), buffer(stdin, input_offset, 512))
                    input_offset += bytes_written
                    if input_offset >= len(stdin):
                        p.stdin.close()
                        write_set.remove(p.stdin)

                if p.stdout in rlist:
                    out_chunk = self._read(p.stdout.fileno(), 1024)
                    if out_chunk == "":
                        p.stdout.close()
                        read_set.remove(p.stdout)

                    if out_data_cb is None:
                        out_data += out_chunk
                    else:
                        out_data_cb[0](out_chunk, out_data_cb[1])

                if p.stderr in rlist:
                    err_chunk = self._read(p.stderr.fileno(), 1024)

                    if err_chunk == "":
                        p.stderr.close()
                        read_set.remove(p.stderr)

                    if err_data_cb is None:
                        err_data += err_chunk
                    else:
                        err_data_cb[0](err_chunk, err_data_cb[1])

            if out_data_cb and out_data_cb[1]:
                out_data_cb[0]("", out_data_cb[1], True)

            if err_data_cb and err_data_cb[1]:
                err_data_cb[0]("", err_data_cb[1], True)

        except KeyboardInterrupt:
            try:
                os.kill(p.pid, SIGINT)
            except OSError:
                pass

        ret = p.wait()
        self.process = None

        return out_data, err_data, ret

    def _run_with_callbacks(self, stdin=None, parser_out_func=None, parser_error_func=None, timeout=None):
        out_func = err_func = None

        def out_cb(out_chunk, out_data_l, flush=False):
            out_data = out_data_l[0]
            out_data += out_chunk
            while '\n' in out_data:
                pos = out_data.find('\n')
                parser_out_func(out_data[:pos + 1])
                out_data = out_data[pos + 1:]

            if flush and out_data != "":
                parser_out_func(out_data)
                out_data_l[0] = ""
            else:
                out_data_l[0] = out_data

        def err_cb(err_chunk, err_data_l, flush=False):
            err_data = err_data_l[0]
            err_data += err_chunk
            while '\n' in err_data:
                pos = err_data.find('\n')
                parser_error_func(err_data[:pos + 1])
                err_data = err_data[pos + 1:]

            if flush and err_data != "":
                parser_out_func(err_data)
                err_data_l[0] = ""
            else:
                err_data_l[0] = err_data

        if parser_out_func is not None:
            out_data = [""]
            out_func = (out_cb, out_data)

        if parser_error_func is not None:
            err_data = [""]
            err_func = (err_cb, err_data)

        return self._read_from_pipes(stdin, out_func, err_func, timeout)

    def _get_process(self):
        if self.process is not None:
            return self.process

        kws = {'close_fds': True,
               'stdout': subprocess.PIPE,
               'stderr': subprocess.PIPE,
               'stdin': subprocess.PIPE,
               'env': os.environ.copy()
               }

        if self.cwd is not None:
            kws['cwd'] = self.cwd

        if self.env is not None:
            kws['env'].update(self.env)

        self.process = subprocess.Popen(self.cmd, **kws)

        return self.process

    # We keep this only for backwards compatibility,
    # but it doesn't make sense, since both run and run_sync
    # have been always synchronous
    def run_sync(self, stdin=None, timeout=None):
        return self.run(stdin, None, None, timeout)

    def run(self, stdin=None, parser_out_func=None, parser_error_func=None, timeout=None):
        self._get_process()

        if parser_out_func is None and parser_error_func is None:
            out, err, ret = self._read_from_pipes(stdin, timeout=timeout)
        else:
            out, err, ret = self._run_with_callbacks(stdin, parser_out_func, parser_error_func, timeout)

        if ret != 0:
            raise CommandError(self.cmd, ret, err)

        if parser_out_func is None:
            return out

    def input(self, data):
        if self.process is not None:
            self.process.stdin.write(data)

    def get_pid(self):
        try:
            return self.process.pid
        except:
            return None


if __name__ == '__main__':
    # Valid command without cwd
    cmd = Command(['ls', '-l'])
    cmd.run()

    # Valid command with cwd
    def out_func(line):
        print "LINE: %s" % (line)

    cmd = Command(['ls', '-lh'], '/')
    cmd.run(parser_out_func=out_func)

    # Invalid command
    cmd = Command('invalid')
    try:
        cmd.run()
    except Exception, e:
        print 'Command not found (%s)' % (str(e))

    # Command returning non-zero
    cmd = Command(['diff', '/etc/passwd', '/etc/group'])
    try:
        cmd.run_sync()
    except CommandError, e:
        print "Error running command. Error: %s" % (e.error)

    cmd = Command(['cat', '/foo'])
    try:
        cmd.run_sync()
    except CommandError, e:
        print "Error running command. Error: %s" % (e.error)

    # Run sync
    cmd = Command(['ls'], '/tmp/')
    print cmd.run_sync()

    def error_handler(cmd, data):
        cmd.input('p\n')
        return True

    cmd = Command(['svn', 'info', 'https://svn.apache.org/repos/asf/activemq/trunk'])
    cmd.set_error_handler(error_handler)
    print cmd.run()

    # Timeout
    cmd = Command(['sleep', '100'])
    try:
        cmd.run(timeout=2)
    except CommandTimeOut:
        pass
