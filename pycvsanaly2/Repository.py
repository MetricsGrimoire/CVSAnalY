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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#


class Commit:
    def __init__(self):
        self.__dict__ = {'revision': None,
                         'committer': None,
                         'date': None,
                         'date_tz': None,
                         'author': None,
                         'author_date': None,
                         'author_date_tz': None,
                         'actions': [],
                         'branch': None,
                         'tags': None,
                         'message': "",
                         'composed_rev': False,
                         'parents': []}

    def __getinitargs__(self):
        return ()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __eq__(self, other):
        return isinstance(other, Commit) and self.revision == other.revision

    def __ne__(self, other):
        return not isinstance(other, Commit) or self.revision != other.revision


# Action types
# A Add
# M Modified
# D Deleted
# V moVed (Renamed)
# C Copied
# R Replaced

class Action:
    def __init__(self):
        self.__dict__ = {'type': None,
                         'branch_f1': None,
                         'branch_f2': None,
                         'f1': None,
                         'f2': None,
                         'rev': None}

    def __getinitargs__(self):
        return ()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __eq__(self, other):
        return isinstance(other, Action) and \
            self.type == other.type and \
            self.f1 == other.f1 and \
            self.f2 == other.f2 and \
            self.branch_f1 == other.branch_f1 and \
            self.branch_f2 == other.branch_f2 and \
            self.rev == other.rev

    def __ne__(self, other):
        return not isinstance(other, Action) or \
            self.type != other.type or \
            self.f1 != other.f1 or \
            self.f2 != other.f2 or \
            self.branch_f1 != other.branch_f1 or \
            self.branch_f2 != other.branch_f2 or \
            self.rev != other.rev


class Person:
    def __init__(self):
        self.__dict__ = {'name': None,
                         'email': None}

    def __getinitargs__(self):
        return ()

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__.update(dict)

    def __getattr__(self, name):
        return self.__dict__[name]

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __eq__(self, other):
        return isinstance(other, Person) and self.name == other.name

    def __ne__(self, other):
        return not isinstance(other, Person) or self.name != other.name


if __name__ == '__main__':
    from cPickle import dump, load
    import datetime

    c = Commit()
    c.revision = '25'
    c.committer = 'carlosgc'
    c.date = datetime.datetime.now()
    c.message = "Modified foo files"

    for i in range(5):
        a = Action()
        a.type = 'M'
        a.branch = 'trunk'
        a.f1 = '/trunk/foo-%d' % (i + 1)
        a.rev = '25'

        c.actions.append(a)

    f = open("/tmp/commits", "wb")
    dump(c, f, -1)
    f.close()

    f = open("/tmp/commits", "rb")
    commit = load(f)
    f.close()

    print "Commit"
    print "rev: %s, committer: %s, date: %s" % (commit.revision, commit.committer, commit.date)
    if commit.author is not None:
        print "Author: %s, date: %s" % (commit.author, commit.author_date)
    print "files: ",
    for action in commit.actions:
        print "%s %s " % (action.type, action.f1),
        if action.f2 is not None:
            print "(%s: %s) on branch %s" % (action.f2, action.rev, commit.branch or action.branch)
        else:
            print "on branch %s" % (commit.branch or action.branch)
    print "Message"
    print commit.message
