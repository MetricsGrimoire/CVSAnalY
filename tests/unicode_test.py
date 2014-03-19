#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# Copyright (C) 2012 LibreSoft
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
#       Eduardo Menezes de Morais <companheiro.vermelho@gmail.com>
#
# To execute this test run: "python -m unittest tests.unicode_test" in the root
# of the project

import sys
from pycvsanaly2 import utils

requiredVersion = (2,7)
currentVersion = sys.version_info

if currentVersion >= requiredVersion:
    import unittest
else:
    import unittest2 as unittest


class UnicodeTestCase(unittest.TestCase):

    def testUnicode(self):
        self.assertEqual(u"Hello World", utils.to_unicode(u"Hello World"))

    def testUtf8String(self):
        utf8String = "\xC3\x96\xE1\x9B\x96\x61"
        self.assertEqual(u"\u00d6\u16d6a", utils.to_unicode(utf8String))

    def testAsciiString(self):
        asciiString = "HelloWorld"
        self.assertEqual(u"HelloWorld", utils.to_unicode(asciiString))

    def testLatin1String(self):
        latin1String = "Hell\xf3 W\xe4rld"
        self.assertEqual(u"Helló Wärld", utils.to_unicode(latin1String))

    def testNoString(self):
        """If it is not str or unicode, an error should be raised"""

        self.assertRaises(TypeError, utils.to_unicode, 5)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(UnicodeTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
