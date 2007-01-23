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
# $Id: cvsanal_graph_global.py,v 1.2 2005/04/29 00:01:16 anavarro Exp $

"""
Creates global analysis graphs for the repository using gnuplot

@author:       Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex@gsyc.escet.urjc.es
"""

from config import *
from config_files import *
import os, time, math

# Directory where evolution graphs will be located
config_graphsDirectory = config_graphsDirectory + 'global/'


# See a gnuplot tutorial at
# http://www.cs.uni.edu/Help/gnuplot/
    
def file_plot(outputFile,
	      listValues,
	      title='title',
	      xlabel ='xlabel',
	      ylabel='ylabel',
	      listDescriptions = [],
	      dataStyle = 'linespoints'):
	"""
	Given an output file name, a (multidimensional) list of values and
	some parameters to describe the data, it plots it by means of
	the gnuplot tool.

	It uses command-line arguments, creating a file for the data
	(.dat) and another one for the gnuplot instructions (.gnuplot).
	Once the PNG file is generated, it removes the .dat and .gnuplot file

	@type  outputFile: string 
	@param outputFile: Name of the output file (the config_graphsDirectory)
	                   and the .gnuplot extension will be appended
	@type  listValues: list 
	@param listValues: List with the values that will be plotted. This
	                   list can be multidimensional, so that many
			   values can be plotted at once. This function
			   automatically writes the order in the first
			   column of the data file
	@type  title: string
	@param title: Title of the gnuplot graph
	@type  xlabel: string 
	@param xlabel: Label of the X axis
	@type  ylabel: string
	@param ylable: Label of the Y axis
	@type  listDescription: list
	@param listDescription: Description of the values given in
	                        listValues. Should have the same dimensions
				as listValues
	@type  dataStyle: string 
	@param dataStyle: Style of the data as it will be plotted in gnuplot
	                  Can be of several types. See gnuplot manual for
			  more details
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly
	
	output = open(config_graphsDirectory + outputFile + ".gnuplot", 'w')
	output.write('set title "' + title + ' (log-log)"' + "\n")
	output.write('set xlabel "'+ xlabel +' (log)"' + "\n")
	output.write('set autoscale' + "\n") # let gnuplot determine ranges
#	output.write('set label "yield point" at 1, 2' + "\n") # set label on the plot
#	output.write('set key 0.01,100') # set key
#	output.write('set timefmt "%d/%m/%y\t%H%M"' + "\n")
#	output.write('set xdata time' + "\n")
#	output.write('set xrange [ "1/6/02":"1/11/02" ]' + "\n")
#	output.write('set format x "%d/%m/%y"' + "\n")
#	output.write('set xrange [20:500]' + "\n")
	output.write('set yrange [0:]' + "\n")
	output.write('set ylabel "'+ ylabel +' (log)"' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize 1.2' + "\n")
#	output.write('set logscale y' + "\n")
	output.write('set terminal png' + "\n")
	output.write('set output "' + config_graphsDirectory + outputFile + '.png"' + "\n")
	string = 'plot '
	i = 1
	for description in listDescriptions:
		i+=1
		string += '"' + config_graphsDirectory + outputFile + '.dat" using 1:' + str(i) + ' title \'' + description + ' (log) \', ' 
	string = string[:-2] + "\n"
	output.write(string)
	output.close()

	# Write data into data file
	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for value in listValues:
		string = str(math.log(value[0]))
		for i in range (1, len(value)):
			if value[i] > 0:
				string += "\t" + str(math.log(value[i]))
		output.write(string + "\n")
#		output.write(str(value[0]) + "\t" + str(value[1]) + "\n")
	output.close()

	if os.path.getsize(config_graphsDirectory + outputFile + ".dat") != 0:
		# Execute gnuplots' temporary file
		os.system('gnuplot ' + config_graphsDirectory + outputFile + ".gnuplot")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + ".gnuplot")


def modules_by_commits(filetype=''):
	"""

	@type  : string 
	@param : If filetype is given, then only commits for that filetype
	         are considered

	@rtype: list
	@return: Number of commits per module
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('commits', 'cvsanal_temp_modules', filetype, 'commits DESC')
	return singleresult2list(result)


def modules_by_commiters(filetype=''):
	"""
	
	@type  : string 
	@param : If filetype is given, then only commiters for that filetype
	         are considered

	@rtype: list
	@return:  Number of commiters per module
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('commiters', 'cvsanal_temp_modules', filetype, 'commiters DESC')
	return singleresult2list(result)


def modules_by_files(filetype=''):
	"""


	@type  : string 
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype:  list
	@return: Number of files per module
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('files', 'cvsanal_temp_modules', filetype, 'files DESC')
	return singleresult2list(result)


def modules_by_plus(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return:  Number of aggregated lines per module
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('plus', 'cvsanal_temp_modules', filetype, 'plus DESC')
	return singleresult2list(result)


def modules_by_minus(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of removed lines per module
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('minus', 'cvsanal_temp_modules', filetype, 'minus DESC')
	return singleresult2list(result)


def modules_by_changes(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of aggregated, removed and changed lines per module
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('plus, minus, abs(plus-minus)', 'cvsanal_temp_modules', filetype, '(plus-minus) DESC')
	return tripleresult2orderedlist(result)


def commiter_by_modules(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of modules per commiter
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('COUNT(module_id) AS count', 'cvsanal_temp_commiters', filetype, 'count DESC', 'commiter_id')
	return singleresult2list(result)


def commiter_by_commits(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of commits per commiter
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('commits', 'cvsanal_temp_commiters', filetype, 'commits DESC', 'commiter_id')
	return singleresult2list(result)


def commiter_by_files(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of files per commiter
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('files', 'cvsanal_temp_commiters', filetype, 'files DESC', 'commiter_id')
	return singleresult2list(result)


def commiter_by_plus(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of aggregated lines per commiter
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('plus', 'cvsanal_temp_commiters', filetype, 'plus DESC', 'commiter_id')
	return singleresult2list(result)


def commiter_by_minus(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: Number of removed lines per commiter
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('minus', 'cvsanal_temp_commiters', filetype, 'minus DESC', 'commiter_id')
	return singleresult2list(result)


def commiter_by_changes(filetype=''):
	"""

	@type  : string
	@param : If filetype is given, then only files for that filetype
	         are considered

	@rtype: list
	@return: number of aggregated, removed and changed lines per commiter
	"""	
	if filetype:
		filetype = "filetype='" + filetype + "'"
	result = querySQL('plus, minus, abs(plus-minus)', 'cvsanal_temp_commiters', filetype, 'abs(plus-minus) DESC', 'commiter_id')
	return tripleresult2orderedlist(result)


def graph_global(db, config_graphsDirectory="graphs"):
	"""
	"""

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	print "Creating some general (global) statistics"

	# Commits
	file_plot('modules_by_commits', \
		   modules_by_commits(), \
		   'Modules by number of commits', \
		   'modules', \
		   'commits', \
		   ['Modules by number of commits'])

	for filetype in config_files_names:
		file_plot('modules_by_commits_' + filetype, \
			   modules_by_commits(str(config_files_names.index(filetype))), \
			   'Modules by number of ' + filetype + ' commits', \
			   'modules', \
			   filetype + ' commits', \
			   ['Modules by number of ' + filetype + ' commits'])

	# Commiters
	file_plot('modules_by_commiters', \
			modules_by_commiters(), \
			'Modules by number of commiters', \
			'modules', \
			'commiters', \
			['Modules by number of commiters'])
			
	for filetype in config_files_names:
		file_plot('modules_by_commiters_' + filetype,\
				modules_by_commiters(str(config_files_names.index(filetype))), \
				'Modules by number of ' + filetype + ' commiters', \
				'modules', \
				filetype + ' commiters', \
				['Modules by number of ' + filetype + ' commiters'])

	# Files
	file_plot('modules_by_files', modules_by_files(), 'Modules by number of files', 'modules', 'files', ['Modules by number of files'])

#	file_plot('modules_by_plus', modules_by_plus(), 'Modules by number of added lines', 'modules', 'added lines', ['Modules by aggregated lines'])
#	file_plot('modules_by_minus', modules_by_minus(), 'Modules by number of removed lines', 'modules', 'removed lines', ['Modules by removed lines'])
	file_plot('modules_by_changes', modules_by_changes(), 'Modules by number of changes', 'modules', 'changed lines', ['Aggregated lines', 'Removed lines', 'Final lines (absolute)'])
	
	file_plot('commiter_by_commits', commiter_by_commits(), 'Commiters by number of commits', 'commiters', 'commits', ['Commiters by number of commits'])
	file_plot('commiter_by_modules', commiter_by_modules(), 'Commiters by number of modules', 'commiters', 'modules', ['Commiters by number of modules'])
	file_plot('commiter_by_files', commiter_by_files(), 'Commiters by number of files', 'commiters', 'files', ['Commiters by number of files'])
#	file_plot('commiter_by_plus', commiter_by_plus(), 'Commiters by number of added lines', 'commiters', 'added lines', ['Commiters by number of aggregated lines'])
#	file_plot('commiter_by_minus', commiter_by_minus(), 'Commiters by number of removed lines', 'commiters', 'removed lines', ['Commiters by number of removed lines'])
	file_plot('commiter_by_changes', commiter_by_changes(), 'Commiters by number of changes', 'commiters', 'changed lines', ['Aggregated lines', 'Removed lines', 'Final lines (absolute)'])

if __name__ == '__main__':

	graph_global()
