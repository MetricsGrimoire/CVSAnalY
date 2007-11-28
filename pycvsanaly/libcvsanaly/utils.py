# Copyright (C) 2007 LibreSoft
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
#       Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>

import os
import tempfile

from FindProgram import find_program
from Command import Command, CommandError

class Gnuplot:

    def __init__ (self):
        self.gnuplot = find_program ('gnuplot')
        assert self.gnuplot is not None, "Gnuplot command not found in PATH"

        self.plots = []
        self.data = ""

        self.termninal = 'png'
        self.title = None
        self.x_title = None
        self.y_title = None
        self.data_style = 'lines'

    def set_output (self, output):
        self.output = output

    def set_terminal (self, terminal):
        self.terminal = terminal
        
    def set_title (self, title):
        self.title = title

    def set_style_data (self, style):
        self.data_style = style

    def append_data (self, data):
        self.data += " ".join ([str (i) for i in data])
        self.data += "\n"

    def __build_input (self):
        retval = ""
        if self.title is not None:
            retval += "set title '%s'\n" % (self.title)
        retval += "set autoscale\n"
        retval += "set style data %s\n" % (self.data_style)
        retval += "set terminal %s\n" % (self.terminal)
        retval += "set output '%s'\n" % (self.output)

        retval += "plot "
        i = 0
        for pfile, c1, c2, title, style in self.plots:
            if i > 0:
                retval += ","
            retval += "'%s' using %d:%d " % (pfile.name, c1, c2)
            if title is not None:
                retval += "t '%s' " % (title.encode ('utf-8'))
            if style is not None:
                retval += "with %s " % (style)
            i += 1

        retval += "\n"
        retval += "quit\n"

        return retval

    def plot (self):
        cmd = [self.gnuplot]

        stdin = self.__build_input ()
        
        command = Command (cmd)
        try:
            command.run (stdin = stdin)
        except CommandError, e:
            if not os.path.exists (self.output):
                raise

    def add_plot (self, c1, c2, title = None, style = None):
        data_file = tempfile.NamedTemporaryFile ()
        data_file.file.write (self.data)
        data_file.file.flush ()
        self.plots.append ((data_file, c1, c2, title, style))
        self.data = ""


if __name__ == '__main__':
    gp = Gnuplot ()
    gp.set_terminal ('svg')
    gp.set_output ("/tmp/out.svg")
    for i in range (10):
        gp.append_data ((i, i * 5))
    gp.add_plot (1, 2)

    for i in range (10):
        gp.append_data ((i, i * 10))
    gp.add_plot (1, 2)

    gp.plot ()
