#!/usr/bin/python2.2
# vim: set expandtab tabstop=4 shiftwidth=4:
# +----------------------------------------------------------------------+
# |          CVSAnalY-web: Web interface for the CVS Analysis Tool       |
# +----------------------------------------------------------------------+
# |                http://libresoft.dat.escet.urjc.es                    |
# +----------------------------------------------------------------------+
# |    Copyright (c) 2003 Universidad Rey Juan Carlos (Madrid, Spain)    |
# +----------------------------------------------------------------------+
# | This program is free software. You can redistribute it and/or modify |
# | it under the terms of the GNU General Public License as published by |
# | the Free Software Foundation; either version 2 or later of the GPL.  |
# +----------------------------------------------------------------------+
# | Authors:                                                             |
# |          Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
# +----------------------------------------------------------------------+
#
# $Id: cvsanal_graph_generations.py,v 1.2 2005/04/20 22:42:30 anavarro Exp $

from config import *
from db import *
import os, time

# Directory where evolution graphs will be located
config_graphsDirectory = config_graphsDirectory + 'generations/'

def most_active_commiters(dbtable, time_start, time_slots, commiter_slots, interval):
	"""
	Returns a list with the 10% (+1) most active commiters
	in a given period of time
	(really speaking it is a list of lists)
	Returns also a list with the number of commits in a time_slot
	"""
	total_commits = []
	most_actives = []
	end = time_start	
	for i in range(0,time_slots):		
		total_commits.append(0)

	i = 0
	while i < time_slots:
		i += 1
		list = []
		most_actives_temp = []
		start = end
		end += interval
		where = ""
		# KDE-specific code
#		dbtable_temp = dbtable.replace("_log", "")
#		dbtable_kde = dbtable + ", " + dbtable.replace("log", "commiters")
#		where = "AND " + dbtable_temp + "_commiters.commiter_id=" + dbtable_temp + "_log.commiter_id AND commiter!='kulow'"
#		result2 = querySQL('DISTINCT(' + dbtable_temp + '_commiters.commiter_id), COUNT(*) AS count', dbtable_kde, "date >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'" + where, 'count DESC', 'commiter_id')

		# Excluding po files
		# Uncomment this line and set not_po to '' to
		# include translation files
		not_po = " AND file not like 'po/%' "

		result2 = querySQL('DISTINCT(commiter_id), COUNT(*) AS count', dbtable, "date_log >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'" + not_po, 'count DESC', 'commiter_id')
		list = doubleresult2list(result2)

		# get most active commiters
		j = 0
		while j < (len(list)/commiter_slots +1) and len(list) > 0:
			j+=1
			most_actives_temp.append(list[j-1][0])

		most_actives.append(most_actives_temp)
		# get total number of commits
		for item in list:
			total_commits[i-1] += int(item[1])

	return most_actives, total_commits

def commits_most_actives(dbtable, most_actives, interval, time_start, time_slots):
	"""
	Returns a list with the number of commits of the most active
	developers during a given slot (an item in the list corresponds
	to the number of commits during that slot)
	"""

	i = 0
	end = time_start
	slots = []
	while i < time_slots:
		i += 1
		start = end
		end += interval
		slots_temp = []
		for slot in most_actives:
			where = ""
			flag = 1
			for commiter in slot:
				if flag:
					where = where + "AND (commiter_id='" + str(commiter) + "' "
					flag = 0
				else:
					where = where + " OR commiter_id='" + str(commiter) + "' "
			if where:
				where += ")"

			# Excluding po files
			# Uncomment this line and set not_po to '' to
			# include translation files
			not_po = " AND file not like 'po/%' "

			result3 = querySQL('COUNT(*) AS count', dbtable, "date_log >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "' " + where + not_po)
			slots_temp.append(uniqueresult2int(result3))
		slots.append(slots_temp)
	return slots

def activity_to_files(dbtable, slots, total_commits, time_slots, file_append):
	"""
	Prints the activity in the slots into files
	Generates three different files:
	*.dat -> number of commits by top commiters in any given slot
	*-sum.dat -> aggregated number of commits by top commiters
	*-per.dat -> percentage of commits by top commiters in any given slot
	"""

	total_slot = []
	for i in range(0,time_slots):
		total_slot.append(0)
	total_slot_percentage = []
	for i in range(0,time_slots):
		total_slot_percentage.append(0)

	# Write data into data file
	output = open(config_graphsDirectory + dbtable + file_append + ".dat", 'w')
	output2 = open(config_graphsDirectory + dbtable + "-sum" + file_append + ".dat", 'w')
	output3 = open(config_graphsDirectory + dbtable + "-per" + file_append + ".dat", 'w')
	line = "0"
	for i in range(0,time_slots):
		line = line + "\t0"
	output.write(line + "\n")
	output2.write(line + "\n")
	output3.write(line + "\n")
	
	j = 1
	for slot in slots:
#		print slot
                line = str(j)
		line2 = str(j)
		for slice in slot:
			line = line + "\t" + str(slice)
			if total_commits[j-1] != 0:
				line2 = line2 + "\t" + str((100 * slice)/ total_commits[j-1])
			else: line2 = line2 + "\t0"
		output.write(line + "\n")
		output3.write(line2 + "\n")
		for i in range(0,time_slots):
			total_slot[i] += int(slot[i])
#		print total_slot
                line = str(j)
		for slice in total_slot:
			line = line + "\t" + str(slice)
		output2.write(line + "\n")
		j += 1
	output.close()
	output2.close()
	output3.close()


def print_most_actives(dbtable, most_actives):
	"""
	Prints the most_actives list with the most actives commiters
	into a file named after dbtable with the append -dev.dat
	"""
	output = open(config_graphsDirectory + dbtable + "-dev.dat", 'w')
	line = ""
	for rowlist in most_actives:
		for row in rowlist:
			line = line + "\t" + str(row)
		line = line + "\n"
	output.write(line)
	output.close()

	
def file_plot(outputFile, time_slots, percentage_of_commiters, file_append='', title_appended='', xlabel ='Intervals (time) - 0: Project start - 10: today', ylabel='Number of Commits', dataStyle = 'linespoints'):
	"""
	"""

	title2 = 'Evolution of commits in time for top commiters' + title_appended
	output = open(config_graphsDirectory + outputFile + file_append + ".gnuplot", 'w')
	output.write('set title "' + title2 + '"' + "\n")
	output.write('set xlabel "'+ xlabel +'"' + "\n")
	output.write('set autoscale' + "\n") # let gnuplot determine ranges
	output.write('set yrange [0:]' + "\n")
	output.write('set ylabel "'+ ylabel +'"' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize .6' + "\n")
#	output.write('set terminal postscript eps' + "\n")
#	output.write('set output "' + outputFile + file_append + '.eps"' + "\n")
	output.write('set terminal png' + "\n")
	output.write('set output "' + config_graphsDirectory + outputFile + file_append + '.png"' + "\n")	
	# An individual entry for any slot (with reference to the column
	# and title)
	i=0
	string = ''
	while i < time_slots:
		i=i+1
		string = string + '"' + config_graphsDirectory + outputFile + file_append + '.dat" using 1:' + str(i+1) + ' title "Main developers in time slot number ' + str(i) + '", ' 

	output.write('plot ' + string[0:-2] + "\n")
#	output.write('set terminal postscript eps' + "\n")
#	output.write('set output "' + outputFile + file_append + '.eps"' + "\n")
	output.write('plot ' + string[0:-2] + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + outputFile + file_append + ".gnuplot")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + file_append + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + file_append + ".gnuplot")


def evolution_in_time(dbtable, percentage_of_commiters = 10, time_slots = 10):
	"""
	Given some configuration parameters as input (module, number
	of percentage of commiters that will correspond to the most active
	and number of time slots in which the project will be divided in time)
	returns a set of files that contain the information in several ways
	(by slots, aggregated, by percentage) in textual and visual way

	This method calls mainly other submethods that handle different
	subtasks
	"""
	
	commiter_slots = 100/percentage_of_commiters
	time_start = time.mktime(time.strptime(first_commit(dbtable), '%Y-%m-%d %H:%M:%S'))
	time_finish =  time.mktime(time.gmtime())
	interval = (time_finish - time_start) / time_slots

	most_actives, total_commits = most_active_commiters(dbtable, time_start, time_slots, commiter_slots, interval)
	print_most_actives(dbtable, most_actives)
	slots = commits_most_actives(dbtable, most_actives, interval, time_start, time_slots)

	file_append = '_' + str(time_slots) + '_' + str(percentage_of_commiters)
	activity_to_files(dbtable, slots, total_commits, time_slots, file_append)

	file_plot(dbtable, time_slots, percentage_of_commiters, file_append, '(by number of commits')
	file_plot(dbtable, time_slots, percentage_of_commiters, '-sum' + file_append, '(aggregated)')
	file_plot(dbtable, time_slots, percentage_of_commiters, '-per' + file_append, 'by percentage for each time interval')	


def graph_generations():
	"""
	"""

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	print "Creating generational graphs..."

	# Getting modules out of database
	moduleList = uniqueresult2list(querySQL('module', 'modules'))

	for module in moduleList:
		for number_of_slots in config_slots:
			for threshold in config_thresholds:
				print 'Working on ' + module + '. Threshold: ' + str(threshold) + '. Number of slots: ' + str(number_of_slots)
				moduleName = db_module(module)
				evolution_in_time(moduleName + '_log', threshold, number_of_slots)


# # # # # # # # # # #
#    Main program   #
# # # # # # # # # # #

if __name__ == '__main__':

	graph_generations()
	db.close()
