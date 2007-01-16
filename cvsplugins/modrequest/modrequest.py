# Copyright (C) 2006 Gregorio Robles
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
# Authors : Gregorio Robles <grex@gsyc.escet.urjc.es>

"""
This module extracts modification requests from the logs table.
The algorithm used is a sliding window algorithm described in:

'Mining CVS repositories, the softChange experience'
by Daniel M. German
International Workshop on Mining Software Repositories
http://msr.uwaterloo.ca/papers/German.pdf

Watch out! We do not implement the same comment added by the developer
during commit yet!

@author:       Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex@gsyc.escet.urjc.es
"""

import time

#delta1 = 600
#delta2 = 45

delta1 = 300
delta2 = 15

def modrequest(db):

    print "Calculating Modification Request"
    
    # get the number of commiters
    numCommiters = db.uniqueresult2int(db.querySQL('COUNT(*)', 'commiters'))

    MRList = []
    modrequest_id = 0
    for commiter_id in range(0,numCommiters+1):
        commitList = db.doubleIntStr2list(db.querySQL('commit_id, date_log', 'log', "commiter_id=" + str(commiter_id), 'date_log'))
        time_first = 0
        MRtempList = []
        for (commit_id, date_log) in commitList:
            time_log = time.mktime(time.strptime(date_log, '%Y-%m-%d %H:%M:%S'))
            if not time_first:
                time_first = time_log
                time_previous = time_log
            if  time_log - time_first <= delta1 and time_log - time_previous <= delta2:
                MRtempList.append(commit_id)
            else:
                time_first = time_log
                MRList.append(MRtempList)
                MRtempList = [commit_id]
            time_previous = time_log
        MRList.append(MRtempList)

        for commitList in MRList:
            modrequest_id += 1
            for index in range(len(commitList)):
                #print "INSERT INTO cvsanal_modrequest (request_id, commit_id) VALUES (" + str(modrequest_id) + ", " + str(commitList[index]) + ");\n"
                db.insertData("INSERT INTO cvsanal_modrequest (request_id, commit_id) VALUES (" + str(modrequest_id) + ", " + str(commitList[index]) + ");\n")
        MRList = []

# To run it from the command line:
#import database as dbmodule
#conection = "mysql://user:passwd@localhost/database"
#db = dbmodule.Database(conection)
#modrequest(db)
