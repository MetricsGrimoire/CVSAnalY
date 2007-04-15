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
# $Id: cvsanal_graph_evolution.py,v 1.2 2005/04/29 10:58:41 anavarro Exp $

"""
Creates evolution analysis graphs for repository, modules and commiters

@author:       Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex@gsyc.escet.urjc.es
"""

import os, time
from intermediate_tables import db_module, first_commit, first_commit_commiter

# Directory where evolution graphs will be located
config_graphsDirectory = 'evolution/'


# See a gnuplot tutorial at
# http://www.cs.uni.edu/Help/gnuplot/
    
def file_plot(outputFile, listValues, title='title', xlabel ='xlabel', ylabel='ylabel', listDescriptions = [], dataStyle = 'linespoints'):
	"""
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly
	
	output = open(config_graphsDirectory + outputFile + ".gnuplot", 'w')
	output.write('set title "' + title + '"' + "\n")
	output.write('set xlabel "'+ xlabel +'"' + "\n")
	output.write('set autoscale' + "\n") # let gnuplot determine ranges
#	output.write('set label "yield point" at 1, 2' + "\n") # set label on the plot
#	output.write('set key 0.01,100') # set key
#	output.write('set timefmt "%d/%m/%y\t%H%M"' + "\n")
#	output.write('set xdata time' + "\n")
#	output.write('set xrange [ "1/6/02":"1/11/02" ]' + "\n")
#	output.write('set format x "%d/%m/%y"' + "\n")
#	output.write('set xrange [20:500]' + "\n")
#	output.write('set yrange [0:]' + "\n")
	output.write('set ylabel "'+ ylabel +'"' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize 0.7' + "\n")
#	output.write('set logscale y' + "\n")
	output.write('set terminal png' + "\n")
	output.write('set output "' + config_graphsDirectory + outputFile + '.png"' + "\n")

	string = 'plot '
	i = 1
	for description in listDescriptions:
		i+=1
		string += '"' + config_graphsDirectory + outputFile + '.dat" using 1:' + str(i) + ' title \'' + description + '\', ' 
	string = string[:-2] + "\n"
	output.write(string)
	output.close()

	# Write data into data file
	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for value in listValues:
		string = ''
		for i in range (0, len(value)):
			if value[i] >= 0:
				string += str(value[i]) + "\t"
		output.write(string + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + outputFile + ".gnuplot")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + ".gnuplot")

def modules_in_time(db, param, value):
	"""
	if the given parameter is:
	COUNT(*)                --> number of commits
	COUNT(DISTINCT(file))   --> number of files
	COUNT(DISTINCT(commiter_id))   --> number of commiters
	SUM(plus - minus)       --> number of Lines Of Code	
	"""
	result = db.doubleStrInt2list(db.querySQL('module,module_id', 'modules'))

	for module in result:
		print "Creating graph for " + module[0]
		moduleName = db_module(module[0])
		start = first_commit(db, "log","module_id = " + str(module[1]))
		if start:
			year = int(start[0:4])
			month = int(start[5:7])
			day = int(start[8:10])
			begin = time.mktime((year, month, day,0,0,0,0,0,0))
			i = 1
			commitsInTimeList = []
			while begin + i * 7 * 24 * 3600 < time.mktime(time.localtime()):
				point = begin + i * 7 * 24 * 3600
			#	print str(time.gmtime(point)[0]) + " " + str(time.gmtime(point)[1]) + " " + str(time.gmtime(point)[2])
				count = db.querySQL(param, 'log', "date_log < '" + str(time.gmtime(point)[0]) + "-" + str(time.gmtime(point)[1]) + "-" + str(time.gmtime(point)[2]) + "' AND module_id='" +  str(module[1]) + "'")

#				print count
				if count[0][0] == None:
					commitsInTimeList.append([0,0])
				else:
					commitsInTimeList.append([i, int(count[0][0])])
				i += 1

			file_plot(value + '_in_time_for_module_' + module[0], commitsInTimeList, 'Evolution in time of the number of ' + value + ' in module ' + module[0], 'time (in weeks)', value, [value + '_in_time_for_' + module[0]])


def commiters_in_time(db, param, value):
	"""
	if the given parameter is:
	SUM(commits)            --> number of commits
	SUM(plus - minus)       --> number of Lines Of Code	
	"""
	result = db.querySQL('commiter_id, commiter', 'cvsanal_commiters_id')

	for commiter in result:
		print "Creating graph for " + commiter[1]
		start = first_commit_commiter(db, commiter[0])
		if start:
			year = int(start[0:4])
			month = int(start[5:7])
			day = int(start[8:10])
			begin = time.mktime((year, month, day,0,0,0,0,0,0))
			i = 1
			commitsInTimeList = []
			while begin + i * 4 * 7 * 24 * 3600 < time.mktime(time.localtime()):
				point = begin + i * 4 * 7 * 24 * 3600
				print str(point)
#				print "date < '" + str(time.gmtime(point)[0]) + "-" + str(time.gmtime(point)[1]) + "-" + str(time.gmtime(point)[2]) + "'"
				count = db.querySQL(param, 'log', "date_log < '" + str(time.gmtime(point)[0]) + "-" + str(time.gmtime(point)[1]) + "-" + str(time.gmtime(point)[2]) + "' AND commiter_id='" + commiter[0] + "'")

#				print count
				if count[0][0] == None:
					commitsInTimeList.append([0,0])
				else:
					commitsInTimeList.append([i, int(count[0][0])])
				i += 1

			file_plot(value + '_in_time_for_commiter_' + commiter[1], commitsInTimeList, 'Evolution in time of the number of ' + value + ' for commiter ' + commiter[1], 'time (in months)', value, [value + '_in_time_for_' + commiter[1]])


def months_from_first_item(dateList):
	"""
	Given a list of dates in order (from older to newer),
	returns a list where all dates are the number of months since
	the first entry
	"""
	import time

	outputList = []

	referenceTuple = time.strptime(dateList[0], '%Y-%m-%d %H:%M:%S')
	#referenceTuple = time.strptime(dateList[0], '%Y-%m-%d')
	index = 1
	for item in dateList:
		index +=1
		itemTuple = time.strptime(item, '%Y-%m-%d %H:%M:%S')
		#itemTuple = time.strptime(item, '%Y-%m-%d')
		months = (itemTuple[0] - referenceTuple[0]) * 12 + (itemTuple[1] - referenceTuple[1]) + (itemTuple[2] - referenceTuple[2] + 0.0)/30
		outputList.append(months)

	return outputList

def mergeFirstAndLastList(firstList, lastList):
	"""
	gets two lists with data
	listA: (1, 2, 3)
	listB: (2, 3, 5)
	returns one single list with data prepared for gnuplot
	number of dates before a given month
	outputList(1, 3, 5, 5, 6)
	"""

	outputList = []
	maximum = lastList[-1]
	for index in range(0, int(maximum+2)):
		first = len([element for element in firstList if element<=index])
		last = len([element for element in lastList if element<=index])
		outputList.append([index, first, last])
	return outputList

def repository_in_time(db):
	"""
	"""

	# Looking for first commits
	firstList = db.uniqueresult2list(db.querySQL('MIN(first_commit) AS first',
					       'cvsanal_temp_modules',
					       '',
					       'first',
					       'module'))
	startingDate = firstList[0]
	firstList = months_from_first_item(firstList)

	# Looking for last commits
	lastList = db.uniqueresult2list(db.querySQL('MAX(last_commit) AS last',
					       'cvsanal_temp_modules',
					       '',
					       'last',
					       'module'))
	# We enter the first commit for any module for referect
	# and therefore remove the last entry
	lastList.insert(0, startingDate)
	lastList.pop()

	lastList = months_from_first_item(lastList)

	finalList = mergeFirstAndLastList(firstList,lastList)

	file_plot('repository_first_and_last', finalList, 'Number of modules in time', 'months', 'modules', ['Number of modules (first commit)', 'Number of inactive modules (last commit)'])

def plot(db):
	"""
	"""

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	print "Creating several evolution graphs for the whole repository"

	repository_in_time(db)

	print "Creating several evolution graphs for modules"

	modules_in_time(db, 'COUNT(*)', 'commits')
	modules_in_time(db, 'COUNT(DISTINCT(file_id))', 'files')
	modules_in_time(db, 'COUNT(DISTINCT(commiter_id))', 'commiters')
	modules_in_time(db, 'SUM(plus - minus)', 'LOCs')

	print "Creating several evolution graphs for commiters"
		
	commiters_in_time(db, 'COUNT(*)','commits')
	commiters_in_time(db, 'COUNT(DISTINCT(file_id))','files')
	commiters_in_time(db, 'SUM(plus)-SUM(minus)','LOCs')
	commiters_in_time(db, 'COUNT(DISTINCT(module_id))','modules')

