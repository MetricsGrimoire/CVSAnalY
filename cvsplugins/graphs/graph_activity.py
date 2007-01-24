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
# $Id: cvsanal_graph_activity.py,v 1.2 2005/04/19 14:36:19 anavarro Exp $

"""


@author:       Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex@gsyc.escet.urjc.es
"""

import os, time

# Directory where evolution graphs will be located
config_graphsDirectory = 'activity/'

weekdayDict = {0: '1_Monday',
	       1: '2_Tuesday',
	       2: '3_Wednesday',
	       3: '4_Thursday',
	       4: '5_Friday',
	       5: '6_Saturday',
	       6: '7_Sunday'
	       }

def ploticus_hour_activity(outputFile, hourList):
	"""
	"""

	output = open(config_graphsDirectory + outputFile + ".ploticus", 'w')
	output.write('ploticus -prefab chron  data=' + config_graphsDirectory + outputFile + '.dat x=1 tab=hour unittype=time xinc="1 hour" nearest=hour  barwidth=0.16  stubfmt=HHA ylbl="# Commits" color=coral -png -o ' + config_graphsDirectory + outputFile + '.png')
	output.close()

	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for hour in hourList:
		output.write(hour + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('sh ' + config_graphsDirectory + outputFile + ".ploticus")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + ".ploticus")


def ploticus_weekDay_activity(outputFile, weekdayList):
	"""
	"""

	output = open(config_graphsDirectory + outputFile + ".ploticus", 'w')
	output.write('ploticus -prefab dist  fld=1  data=' + config_graphsDirectory + outputFile + '.dat  cats=yes  yrange=0 stubvert=yes  barwidth=0.4 ylbl="# Commits" order=natural  -png -o ' + config_graphsDirectory + outputFile + '.png')
	output.close()

	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for weekday in weekdayList:
		output.write(weekday + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('sh ' + config_graphsDirectory + outputFile + ".ploticus")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + ".ploticus")


def dateListSplit(dateList):
	"""
	Gets a list of dates in yyyy-mm-dd HH:MM:SS format and
	returns two lists: one with the HH:MM:SS
	and a second one with the weekdays
	"""

	hourList = []
	weekdayList = []
	# TODO: this is to avoid a ploticus error when handling large data sets
	index = 1
	for item in dateList:
		index+=1
		if index > 100000:
			return (hourList, weekdayList)
		(date, hour) = item.split(' ')
		hourList.append(hour)
		weekdayList.append(weekdayDict[time.strptime(date, '%Y-%m-%d')[6]])
	return (hourList, weekdayList)

def plot(db):
	"""
	"""

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	modulesList = db.uniqueresult2list(db.querySQL('module', 'modules'))

	for module in modulesList:
		dateList = db.uniqueresult2list(db.querySQL('date_log', 'log'))
		(hourList, weekdayList) = dateListSplit(dateList)
		ploticus_hour_activity('hours_' + module, hourList)
		ploticus_weekDay_activity('weekdays_' + module, weekdayList)


