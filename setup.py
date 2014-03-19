# -*- coding: utf-8 -*-
# Copyright (C) 2006 Alvaro Navarro Clemente
# Copyright (C) 2007-2011  GSyC/LibreSoft, Universidad Rey Juan Carlos
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
# Authors : Alvaro Navarro <anavarro@gsyc.escet.urjc.es>
#           Luis Cañas Díaz <lcanas@libresoft.es>

"""
Installer

@author:       Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import os
import sys

from setuptools import setup


def generate_changelog():
    from subprocess import Popen, PIPE
    from tempfile import mkstemp

    fd, filename = mkstemp(dir=os.getcwd())

    print "Creating ChangeLog"
    cmd = [
        "git", "log", "-M", "-C", "--name-status", "--date=short", "--no-color"
    ]
    pipe = Popen(cmd, stdout=PIPE).stdout

    buff = pipe.read(1024)
    while buff:
        os.write(fd, buff)
        buff = pipe.read(1024)
    os.close(fd)

    os.rename(filename, "ChangeLog")

# Check dependencies
deps = ['repositoryhandler >= 0.3']

#pkg_check_modules (deps)

if sys.argv[1] == 'sdist':
    generate_changelog()

from pycvsanaly2._config import *

setup(name=PACKAGE,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      install_requires=deps,
      url="http://projects.libresoft.es/projects/cvsanaly/wiki/",
      packages=['pycvsanaly2', 'pycvsanaly2.extensions'],
      data_files=[('share/man/man1', ['help/cvsanaly2.1'])],
      scripts=["cvsanaly2"])
