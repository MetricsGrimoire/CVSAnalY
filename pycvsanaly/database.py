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
# Authors : 
#       Alvaro Navarro <anavarro@gsyc.escet.urjc.es>
#       Gregorio Robles <grex@gsyc.escet.urjc.es>

"""
This module contains a basic SQL wrapper

@authors:      Alvaro Navarro and Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      anavarro,grex@gsyc.escet.urjc.es
"""

import os
import time
import sys
import connectionfactory as cf
import getpass
import re

class Database:

    def __init__(self, driver):

        server = ''
        user = ''
        pwd = ''
        db = ''
        module = ''

        # Based on SQLdb parser
        match=re.match('([^:]*)://(.*)/([^\?]*)\?*(.*)', driver)
        if match:
            gps = match.groups()
            server = ''
            user = ''
            pwd = ''
            db = ''

            if len(gps) >= 1:
                module = gps[0]

            if len(gps) >= 2:

                mid = gps[1]
                if mid.find('@') >= 0:
                    upwd, server = mid.split('@')
                    if mid.find(":") >= 0:
                        user, pwd = upwd.split(':')
                else:
                    if mid.find(':') >= 0:
                        user, pwd = mid.split(':')
                    else:
                        server = mid
            if len(gps) >= 3:

                db = gps[2]
        else:
            print "Error (internal), bad url for database connection"

        self.username = user
        self.password = pwd
        self.hostname = server
        self.database = db
        self.module = module

        self.__connection = None
        self.__connection = cf.ConnectionFactory.create_connector(module)
        try:
            self.__connection.connect(user=self.username, passwd=self.password, host=self.hostname, db=self.database)
        except:
            print ("Error in connection: username/password incorrect or database doesn't exist")
            self.create_user()
            self.__connection.connect(self.username, self.password, self.hostname, self.database)

    def connect(self, user='', password='', hostname='', database=''):
        """
        method that establishes a new database connection

        @type  user: string
        @param user: user name
        @type  password: string
        @param password: user's password
        @type  hostname: string
        @param hostname: host which contains database server
        @type  database: string
        @param database: name of the database
        """

        self.__connection.connect(self.username, self.password, self.hostname, self.database)
 
    def querySQL(self, select, tables, where='', order='', group=''):
        """
        Singleton method to access the database
        Input is the query (given by several parameters)
        Output is a row (of rows)

        @type  select: string 
        x@param select: Fields to select
        @type  tables: string
        @param tables: Database tables involved in this query
        @type  where: string
        @param where: Where clause (optional; default: not used)
        @type  order: string
        @param order: Order clause (optional; default: not used)
        @type  group: string
        @param group: Group clause (optional; default: not used)
        """

        if order and where and group:
            query = "SELECT " + select + " FROM " + tables + " WHERE " + where  + " GROUP BY " + group + " ORDER BY " + order
        elif order and where:
            query = "SELECT " + select + " FROM " + tables + " WHERE " + where + " ORDER BY " + order
        elif order and group:
            query = "SELECT " + select + " FROM " + tables + " GROUP BY " + group + " ORDER BY " + order
        elif order:
            query = "SELECT " + select + " FROM " + tables + " ORDER BY " + order
        elif where:
            query = "SELECT " + select + " FROM " + tables + " WHERE " + where
        else:
            query = "SELECT " + select + " FROM " + tables


        r = self.__connection.execute(query)

        try:
            row = r.fetch_row(0)
        except AttributeError:
            sys.exit("Unknown error with SQL server")

        return row


    def executeSQLRaw(self, query):
        """
        Raw SQL execute to the database
        Input is the query (in SQL)
        Output is a tuple of rows (rows are also tuples)
        
        """

        r = self.__connection.execute(query)

        # Dirty trick to avoid raising an exception when nothing
        # is returned by the query -jgb
        #try:
        #    row = r.fetch_row(0)
        #except AttributeError:
        #    print("Unknown error with sql server")

        row = r.fetch_row(0)
        return row


    def singleresult2list(self,row):
        """
        Takes as input a row of rows (as outputed by the querySQL method)
        and returns a list of lists as result

        @type row: tuple
        @param row: tuple of tuples with the SQL results as returned by the querySQL method
                    Only the first item of the rows in the row are considered

        @rtype: list
        @return:  Contains two items: first item is the rank and
                  the second one the result in the row
        """
        list = []
        i = 0
        for item in row:
                i += 1
                list.append([i, int(item[0])])
        return list


    def tripleresult2orderedlist(self,row):
        """
        Takes as input a row of rows (as outputed by the querySQL method)
        and returns a list of lists as result

        @type row: tuple
        @param row: Tuple of tuples with the SQL results as returned by the querySQL method
                    Only the first item of the rows in the row are considered

        @rtype: list
        @return: Contains fouritems: first item is the rank and
                 the second one the first item in the subtuple
                 the third one is the second item in the subtuple
                 the fourth one is the third item in the subtuple
        """
        list = []
        i = 0
        for item in row:
                i += 1
                list.append([i, int(item[0]), int(item[1]), int(item[2])])
        return list

    def doubleresult2list(self,row):
        """
        Takes as input a row of rows (as outputed by the querySQL method)
        and returns a list of lists as result

        @type row: tuple of tuples
        @param row: Tuple of tuples with the SQL results as returned by the querySQL method

        @rtype: list of lists
        @return: Each list contains two items: first item is the first
                 element of the row and second item the second one
        """
        list = []
        if row:
                for item in row:
                        list.append([int(item[0]), int(item[1])])
        return list

    def doubleresult2dict(self,row):
        """
        Takes as input a row of rows with two items (as outputed by the qureySQL method)
        and returns a dictionary: first element is the key, the second one
        the value (integer)

        @type row:
        @param row:

        @rtype: dict
        @return:
        """
        dict = {}
        if row:
                for item in row:
                        dict[item[0]] = int(item[1])
        return dict


    def doubleIntStr2list(self,row):
        """
        Takes as input a row of rows with two items (as outputed by the qureySQL method)
        and returns a list of lists: first item is the first element of the row and second item the second one
        FIXME: this is annoying. I should do some refactoring in order to have
        appropriate functions and not a lot of functions that do almost the same :(

        @type row:
        @param row:

        @rtype: list
        @return:
        """
        list = []
        if row:
                for item in row:
                        list.append([int(item[0]), item[1]])
        return list

    
    def doubleStrInt2list(self,row):
        """
        Takes as input a row of rows with two items (as outputed by the qureySQL method)
        and returns a list of lists: first item is the first element of the row and second item the second one
        FIXME: this is annoying. I should do some refactoring in order to have
        appropriate functions and not a lot of functions that do almost the same :(

        @type row:
        @param row:

        @rtype: list
        @return:
        """
        list = []
        if row:
                for item in row:
                        list.append([item[0], int(item[1])])
        return list


    def uniqueresult2list(self,row):
        """
        Takes as input a row of rows (as outputed by the querySQL method)
        and returns a list with the results
        Only the first item of the rows in the row are considered

        @type row:
        @param row:

        @rtype: list
        @return:
        """
        list = []
        for item in row:
                list.append(item[0])
        return list

    def uniqueresult2int(self,row):
        """
        Takes as input a row with a single row (as sometimes outputed by
        the querySQL method)
        and returns an integer

        @type row:
        @param row:

        @rtype: int
        @return:
        """
        return int(row[0][0])


    def close(self):
        """
        Closes actual connection
        """

        self.__connection.close()

    def get_tables(self):
        """
        Get a list of tables which start with 'annotate' prefix
        Very useful to crate graphs instead of calculate them

        return: python list with all tables
        """
        query = "SHOW TABLES"
        r = self.__connection.execute(query)

        row = r.fetch_row(0)
        tables = []
        for r in row:
            tables.append(r)

        return tables

    def create_table(self, table_name, table_format):
        """
        Creates a table.

        @type  table_name: string
        @param table_name: name of the table
        @type  table_format: dictionary
        @param table_format: key of each field is the name of the column (string).
        The value of each field is the type of each column (string).
        If key is 'Primary Key' the value of the field is the primary key of the table.
        """

        sql_code = "DROP TABLE IF EXISTS " + str(table_name) + ";\n"
        self.__connection.execute(sql_code)

        sql_code = "CREATE TABLE IF NOT EXISTS "+table_name+" (\n"
        prim_key_code = ""

        for k in table_format.keys():
            if k.lower() == "primary key":
                prim_key_code = "    PRIMARY KEY ("+table_format[k]+")\n"
            else:
                sql_code += "    "+k+" "+table_format[k]+",\n"

        if prim_key_code != "":
            sql_code += prim_key_code
        else:
            sql_code = sql_code.rstrip(",\n")+"\n"

        sql_code += ");\n\n"

        r = self.__connection.execute(sql_code)


    def create_user(self, user='', password='', hostname='', database=''):
        """
        Create User. Connection needs to have privileges
        """

        admin_user =  raw_input ("MySQL admin username: ")
        admin_password = getpass.getpass("MySQL admin password: ")
        try:

            query  = "GRANT ALL ON "+str(self.database)
            query += ".* TO " + str(self.username) + "@" + str(self.hostname)
            query += " IDENTIFIED BY \""+str(self.password)+"\";\n"

            connaux = cf.ConnectionFactory.create_connector(self.module)
            connaux.connect(admin_user, admin_password, self.hostname)
            connaux.execute(query)
            connaux.close()

            self.create_database()
        except StandardError:
            sys.exit("Error: Cannot create user")

    def create_database(self, database=''):
        """
        Try to create new database
        assumes that we have privileges to create new one
        and try to drop database with the normal user
        """

        if database:
            name = database
        else:
            name = self.database

        try:
            co = cf.ConnectionFactory.create_connector(self.module)
            co.connect(self.username, self.password, self.hostname)

            query = "DROP DATABASE IF EXISTS " + str(name) + ";\n"
            co.execute(query)

            query = "CREATE DATABASE " + str(name) + ";\n"
            co.execute(query)

            query = "USE " + str(name) + ";\n"
            co.execute(query)

            co.close()

        except StandardError:
            print "WARNING: unable to create database. User " + self.username + " doesn't have privileges"
            self.create_user()


    def insertData(self,sqlcode):
         r = self.__connection.execute(sqlcode)

