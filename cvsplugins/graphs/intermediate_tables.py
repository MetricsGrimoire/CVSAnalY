# Copyright (C) 2006 Libresoft
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
#           Alvaro Navarro  <anavarro@gsyc.escet.urjc.es>

"""
Create intermediate tables. (very useful for cvsanaly-web)

@author:       Gregorio Robles / Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex/anavarro@gsyc.escet.urjc.es
"""

import pycvsanaly.config_files as cfmodule

config_serverDateError_where = ''

def db_module(module):
        """
        Given the natural module name (string) it returns the module name
        that is used in the database. For different purposes, database
        table names cannot contain certain characters

        @type module: string
        @param :

        @rtype: string
        @return:
        """

        moduleName = module.replace('-', '_minus_')
        moduleName = moduleName.replace('+', '_plus_')
        moduleName = moduleName.replace('@', '_at_')
        moduleName = moduleName.replace('.', '_dot_')
        moduleName = moduleName.replace(':', '_ddot_')
        moduleName = moduleName.replace(' ', '_space_')
        moduleName = moduleName.replace('  ', '_doblespace_')

        return moduleName
 
def filesInAtticModules(db, where = ""):
    """
    Returns the number of files it has in the Attic for modules

    @type  where: string
    @param where: additional conditions to the SQL WHERE clause
                  (by default: empty)

    @rtype: dictionary
    @return: number of files in the Attic for a module.
             the key is the module_id, and the value the number of files in the Attic
    """

    returnDict = {}

    if where:
        where = " AND " + where

    resultRow = db.querySQL("COUNT(DISTINCT(file_id)), module_id",
                        "log",
                        "inAttic='1'" + where,
                        "module_id", "module_id")

    for resultTuple in resultRow:
        returnDict[resultTuple[1]] = resultTuple[0]

    return returnDict

def filesInAtticCommiters(db,where = ""):
    """
    Returns the number of files it has in the Attic by commiters

    @type  where: string
    @param where: additional conditions to the SQL WHERE clause
                  (by default: empty)

    @rtype: dictionary
    @return: number of files in the Attic for a commiter.
             the key is the commiter_id, and the value the number of files in the Attic
    """

    returnDict = {}

    if where:
        where = " AND " + where

    resultRow = db.querySQL("COUNT(DISTINCT(file_id)), commiter_id",
                        "log",
                        "inAttic='1'" + where,
                        "commiter_id", "commiter_id")

    for resultTuple in resultRow:
        returnDict[resultTuple[1]] = resultTuple[0]

    return returnDict

def intermediate_table_commiters(db):
    """
    Creates an intermediate Database table with statistical results
    for all commiters in the database
    the database structure is not that clean -due to other means- that it
    should be for this purpose, so this is maybe the best way to solve it
    """

    print "Calculating commiter statistical data "
    config_serverDateError_where = ''

    moduleList = db.doubleIntStr2list(db.querySQL('module_id, module', 'modules'))
    for moduleRow in moduleList:
        module = db_module(moduleRow[1])

        for fileType in cfmodule.config_files_names:
            inAtticFilesDict = filesInAtticCommiters(db, "filetype='" + str(cfmodule.config_files_names.index(fileType)) + "'")

            if not config_serverDateError_where:
                AND = ''
            else:
                AND = ' AND '

            query  = 'commiter_id, COUNT(*) AS commits, SUM(plus) AS plus, SUM(minus) AS minus, COUNT(DISTINCT(file_id)) '
            query += 'AS sum_files, SUM(inAttic) AS inAtticCommits, SUM(external) AS external, SUM(cvs_flag) AS cvs_flag,'
            query += 'MIN(date_log) AS first, MAX(date_log) AS last'

            where  = "module_id='" + str(moduleRow[0]) + "' AND filetype='"
            where += str(cfmodule.config_files_names.index(fileType)) + "' " + AND + config_serverDateError_where

            resultRow = db.querySQL(query, "log", where, "commiter_id", "commiter_id")

            if resultRow:
                for resultTuple in resultRow:
                    try:
                        inAttic = inAtticFilesDict[resultTuple[0]]
                    except KeyError:
                        inAttic = 0
                    query  = "INSERT INTO cvsanal_temp_commiters (commiter_id, module_id, commits, plus, "
                    query += "minus, files, filetype, inAtticFiles, inAtticCommits, external, cvs_flag, first_commit, last_commit) "
                    query += " VALUES ('" + str(resultTuple[0]) + "', '" + str(moduleRow[0]) + "','"
                    query += resultTuple[1] + "', '"
                    query += resultTuple[2] + "', '" + resultTuple[3] + "', '" + resultTuple[4] + "', '" + str(cfmodule.config_files_names.index(fileType))
                    query += "', '" + str(inAttic) + "', '" + resultTuple[5] + "', '" + resultTuple[6] + "', '" + resultTuple[7] + "', '"
                    query += resultTuple[8] + "', '" + resultTuple[9] + "');\n"

                    db.insertData(query)

def intermediate_table_commiters_id(db):

    print "Calculating statistical data for commiters_id"

    db.insertData("DROP TABLE IF EXISTS cvsanal_commiters_id;")
    db.insertData("create table cvsanal_commiters_id as select * from commiters;")


def intermediate_table_fileTypes(db):

    print "Calculating fileType statistical data "
    index =-1
    for fileType in cfmodule.config_files_names:
        index+=1
        db.insertData("INSERT INTO cvsanal_fileTypes (fileType_id, fileType) VALUES ('" + str(index) + "', '" + fileType + "');\n")

def intermediate_table_modules(db):

    print "Calculating statistical data for modules"
    moduleList = db.querySQL('module_id, module', 'modules')
    moduleDict = {}

    for moduleRow in moduleList:
        module_id = moduleRow[0]
        module = moduleRow[1]
        moduleDict[module_id] = module

        module = db_module(module)
        db.insertData("INSERT INTO cvsanal_temp_inequality (module_id) VALUES ('" + str(module_id) + "');\n")

    for fileType in cfmodule.config_files_names:
        if not config_serverDateError_where:
            AND = ''
        else:
            AND = ' AND '

        resultRow = db.querySQL ('module_id, COUNT(DISTINCT(commiter_id)) AS commiters, COUNT(*) AS commits, SUM(plus) AS plus, SUM(minus) AS minus, COUNT(DISTINCT(file_id)) AS files, SUM(external) AS external, SUM(cvs_flag) AS flag, SUM(inattic) AS inAtticCommits, MIN(date_log) AS first_commit, MAX(date_log) AS last_commit','log', "filetype='" + str(cfmodule.config_files_names.index(fileType)) + "'" + AND + config_serverDateError_where, 'module_id', 'module_id')

        inAtticFilesDict = filesInAtticModules(db, "filetype='" + str(cfmodule.config_files_names.index(fileType)) + "'")

        if resultRow:
            for resultTuple in resultRow:
                try:
                    inAttic = inAtticFilesDict[resultTuple[0]]
                except KeyError:
                    inAttic = 0

                query = "INSERT INTO cvsanal_temp_modules (module_id, module, commiters, commits, plus, minus, files, external, cvs_flag, filetype, inAtticCommits, inAtticFiles, first_commit, last_commit) "
                query += " VALUES ('" + resultTuple[0] + "', '" + moduleDict[resultTuple[0]] + "', '" + resultTuple[1] + "', '" + resultTuple[2] + "', '" + resultTuple[3] + "', '" + resultTuple[4]
                query += "', '" + resultTuple[5] + "', '" + resultTuple[6] + "', '" + resultTuple[7] + "', '" + str(cfmodule.config_files_names.index(fileType)) + "', '" + resultTuple[8] + "', '"
                query += str(inAttic) + "', '" + resultTuple[9] + "', '" + resultTuple[10] + "');\n"

                db.insertData(query)

