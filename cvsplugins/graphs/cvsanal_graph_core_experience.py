#!/usr/bin/python2.2
# vim: set expandtab tabstop=4 shiftwidth=4:
# +----------------------------------------------------------------------+
# |                     CVSAnal: CVS Analysis Tool                       |
# +----------------------------------------------------------------------+
# |                http://libresoft.dat.escet.urjc.es                    |
# +----------------------------------------------------------------------+
# |   Copyright (c) 2002-3 Universidad Rey Juan Carlos (Madrid, Spain)   |
# +----------------------------------------------------------------------+
# | This program is free software. You can redistribute it and/or modify |
# | it under the terms of the GNU General Public License as published by |
# | the Free Software Foundation; either version 2 or later of the GPL.  |
# +----------------------------------------------------------------------+
# | Authors:                                                             |
# |          Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
# +----------------------------------------------------------------------+
# 
# $Id: cvsanal_graph_core_experience.py,v 1.2 2005/04/20 22:42:30 anavarro Exp $

from config import *
from db import *
from cvsanal_graph_inequality import atkinsonF
import os, time

# Directory where evolution graphs will be located
config_graphsDirectory = config_graphsDirectory + 'core/'

def file_plot(module, time_slots, delta_time = 'Months', title='title', xlabel ='xlabel', ylabel='ylabel', dataStyle = 'linespoints', label = ''):
	"""
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly
	
	output = open(config_graphsDirectory + module + "_" + delta_time + ".gnuplot", 'w')
	output.write('set xlabel "' + delta_time + ' from first commit' + "\n")
#	output.write('set label "' + label +'" at 5,1750' + "\n") # set label on the plot
#	output.write('set key 5,20' + "\n") # set key
	output.write('set xrange [0:' + time_slots + ' ]' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize 0.5' + "\n")
	output.write('set terminal png' + "\n")

	output.write('set title "Accumulted experience in the core group for module ' + module + '"' + "\n")
#	output.write('set yrange [0:100]' + "\n")
	output.write('set ylabel "Accumulated experience"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + "_" + delta_time + '.dat" using 1:2 title \'Accumuluted core group experience for ' + module + '\', "' + config_graphsDirectory + module + "_" + delta_time + '.dat" using 1:3 title \'Number of core group developers ' + module + '\'' + "\n")

	output.close()
	
	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + module + "_" + delta_time + ".gnuplot")

	# Delete temporary files
 	os.system('rm ' + config_graphsDirectory + module + "_" + delta_time + ".dat")
 	os.system('rm ' + config_graphsDirectory + module + "_" + delta_time + ".gnuplot")


def mycmp(a, b):
    """
    Used to sort the elements of a list
    elements with bigger value are put first
    """
    return cmp(b[0], a[0])

def gettingCore(atkinson, commitsAndCommiterList):
	"""
	"""

	coreList = []
	commitsAndCommiterList.sort(cmp)
	max = round(atkinson * len(commitsAndCommiterList))
	for i in range(0, max):
		commitsAndCommiterList.pop()
	for item in commitsAndCommiterList:
		coreList.append(item[1])
	return coreList

def inHistoricalCoreList(newList, historicalList):
	"""
	
	"""
	newInCoreList = []
	for item in newList:
		flag = 0
		for oldCoreList in historicalList:
			if item in oldCoreList:
				flag = 1
		if not flag:
			newInCoreList.append(item)
	return newInCoreList
	

def timeToCore(newInCoreList, moduleName, date, interval, interval_length):
	"""
	"""

	for commiter_id in newInCoreList:
		result = querySQL('MIN(date_log)', 'log', "commiter_id='" + str(commiter_id) + "' AND " + config_serverDateError_where)
# Probably this query is more efficient:
#SELECT first_commit FROM cvsanal_temp_commiters, modules, evolution_commiters WHERE modules.module_id=cvsanal_temp_commiters.module_id AND evolution_commiters.commiter=cvsanal_temp_commiters.commiter AND evolution_commiters.commiter_id='160' AND modules.module='evolution';
		start = result[0][0]
		begin = time.mktime((int(start[0:4]), int(start[5:7]), int(start[8:10]), int(start[11:13]), int(start[14:16]),0,0,0,0))

		fraction = (date-begin)/interval_length
		print 'Interval: ' + str(interval) + '\t Commiter: ' + str(commiter_id) + '\t Time to core: ' + str(fraction)

def accumulatedExperience(historicalList):
	"""
	Calculates the accumulated experience out of the
	list of core-groups in time
	"""
	alreadyDict = {}
	list = []
	for coreGroupList in historicalList:
		sum = 0
		number = 0
		for commiter in coreGroupList:
			if commiter in alreadyDict:
				alreadyDict[commiter] +=1
			else:
				alreadyDict[commiter]=0
			number +=1
			sum += alreadyDict[commiter]
		list.append([sum, number])
	return list

def browseInTime(module, moduleName, time_start, time_slots, interval, delta_time):
	"""
	"""

	i = 0
	start = time_start
	end = time_start
	HistoricalCoreList = []
	while i < time_slots:
		i += 1
		commitList = []
		start = end
		end += interval

		# Delta index
		list = doubleresult2list(querySQL('COUNT(*) AS count, commiter_id', 'log', "date_log > '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'count', 'commiter_id'))

		total_commits = 0
		total_commiters = 0
		for item in list:
			commitList.append(item[0])
		for commits in commitList:
			total_commits += int(commits)
			total_commiters += 1
		if total_commiters == 0:
			atkinson = 0
		else:
			atkinson = atkinsonF(commitList, total_commiters, total_commits)

		coreList = gettingCore(atkinson, list)
#		newInCoreList = inHistoricalCoreList(coreList, HistoricalCoreList)
#		timeToCore(newInCoreList, moduleName, end, i, interval)
		HistoricalCoreList.append(coreList)
		

	experienceList = accumulatedExperience(HistoricalCoreList)
	output = open(config_graphsDirectory + module + "_" + delta_time + '.dat', 'w')
	num = 0
	for item in experienceList:
		num +=1
		output.write(str(num)
			     + '\t' + str(item[0])  + '\t' + str(item[1]) + '\n')

	output.close()


def core_experience():
	"""
	"""
	
	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	# Getting modules out of database
	moduleList = uniqueresult2list(querySQL('module', 'modules'))

	print "Calculating time to core"

	for module in moduleList:
		print "Working with " + module
		moduleName = db_module(module)
                time_start = time.mktime(time.strptime(first_commit(moduleName + '_log'), '%Y-%m-%d %H:%M:%S'))
                time_finish =  time.mktime(time.gmtime())

		# Calculating it for monthly time slots
                months = (time_finish - time_start) / (30*24*3600)
		time_slots = round(months)
		interval = (time_finish - time_start) / time_slots
		browseInTime(module, moduleName, time_start, time_slots, interval, 'months')
		file_plot(module, time_slots, 'months')

		# Calculating it for trimester time slots
                trimesters = (time_finish - time_start) / (92*24*3600)
		time_slots = round(months)
		interval = (time_finish - time_start) / time_slots
		browseInTime(module, moduleName, time_start, time_slots, interval, 'trimester')
		file_plot(module, time_slots, 'trimester')



if __name__ == '__main__':
	core_experience()
	db.close()
