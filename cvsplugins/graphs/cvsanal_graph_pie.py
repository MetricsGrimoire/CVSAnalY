#!/usr/bin/python
# vim: set expandtab tabstop=4 shiftwidth=4:
# +----------------------------------------------------------------------+
# |                CVSAnalY: CVS and SVN Analysis Tool                   |
# +----------------------------------------------------------------------+
# |                http://libresoft.dat.escet.urjc.es                    |
# +----------------------------------------------------------------------+
# |   Copyright (c) 2002-4 Universidad Rey Juan Carlos (Madrid, Spain)   |
# +----------------------------------------------------------------------+
# | This program is free software. You can redistribute it and/or modify |
# | it under the terms of the GNU General Public License as published by |
# | the Free Software Foundation; either version 2 or later of the GPL.  |
# +----------------------------------------------------------------------+
# | Authors:                                                             |
# |          Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
# +----------------------------------------------------------------------+
# 
# $Id: cvsanal_graph_pie.py,v 1.4 2005/06/02 17:24:32 anavarro Exp $

"""
This module generates pie graphs with the importance of the different
file types (for the whole repository, each module and each commiter)

@author:       Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex@gsyc.escet.urjc.es
"""

from config import *
from config_files import *
from db import *
import os, time

# Directory where evolution graphs will be located
config_graphsDirectory = config_graphsDirectory + 'pie/'

def ploticus_pie(outputFile, listValues):
	"""
	Gets a list with values (and description of the values) and outputs
	a ploticus graph into PNG format

	@type  outputFile: string
	@param outputFile: Name of the output file (without path and extension)
	@type  listValues: list
	@param listValues: List with the values for the pie graph
	                   [integer, description]
	"""
	
	output = open(config_graphsDirectory + outputFile + ".ploticus", 'w')
	output.write('ploticus  -prefab pie  data=' + config_graphsDirectory + outputFile + '.dat  delim=tab values=1  labels=2  colorfld=3 legend=yes radius=1.2 -png -o ' + config_graphsDirectory + outputFile + '.png')
	output.close()

	# Write data into data file
	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for value in listValues:
		output.write(str(value[0]) + "\t" + value[1] + "\t" + config_colorDict[value[1]] + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('sh ' + config_graphsDirectory + outputFile + ".ploticus")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + ".ploticus")


def filetype_commiter_pie():
	"""
	returns a tuple with commiter name and a list with two fields per item:
	LOCs and filetype
	"""

	result = querySQL('commiter_id', 'cvsanal_commiters_id')

	print "traza1"
	for commiter in result:
		
		filetypeList = doubleIntStr2list(querySQL('SUM(ctc.commits), cf.filetype',
							  'cvsanal_temp_commiters ctc, cvsanal_fileTypes cf',
							  "ctc.filetype=cf.fileType_id AND ctc.commiter_id='" + commiter[0] + "'",
							  'cf.filetype','cf.filetype'))
		name = uniqueresult2list(querySQL("commiter","commiters","commiter_id='" + commiter[0] + "'"))
		ploticus_pie('commiter_' + name[0], filetypeList)


def filetype_module_pie():
	"""
	returns a tuple with module name and a list with two fields per item:
	LOCs and filetype
	"""

	result = querySQL('module', 'modules')

	for module in result:
		filetypeList = doubleIntStr2list(querySQL('SUM(ctm.commits), cf.filetype',
							  'cvsanal_temp_modules ctm, cvsanal_fileTypes cf',
							  "ctm.filetype=cf.fileType_id AND module='" + module[0] + "'",
							  'cf.filetype',
							  'cf.filetype'))
		ploticus_pie('module_' + module[0], filetypeList)


def filetype_repository_pie():
	"""
	returns a tuple with repository name and a list with two fields per item:
	LOCs and filetype
	"""

	resultList = doubleIntStr2list(querySQL('SUM(ctm.commits), cf.filetype',
					    'cvsanal_temp_modules ctm, cvsanal_fileTypes cf',
					    'ctm.filetype=cf.fileType_id',
					    'cf.filetype',
					    'cf.filetype'))

	ploticus_pie('cvsanal_repository', resultList)


def graph_pie():
	"""
	"""

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	print "Creating file type pies for the whole repository"
	filetype_repository_pie()
	print "Creating file type pies for modules"
	filetype_module_pie()
	print "Creating file type pies for commiters"
	filetype_commiter_pie()


if __name__ == '__main__':
	"""
	This is just for making the function callable from the
	command line. Try '--help' for more information on this.
	"""
	import sys
	from getargv import getopts

	# Getting command line arguments

	myargs = getopts(sys.argv)
	if myargs.has_key('-h') or myargs.has_key('--help'):
		print ""
		print "    Usage:"
		print "    python cvsanal_graph_pie.py"
		print ""
		print "    if not given, the optional command line values are taken from config.py"
		sys.exit(1)

	# Calling the log function

	graph_pie()
	db.close()
