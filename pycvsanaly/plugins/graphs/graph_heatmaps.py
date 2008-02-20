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
# $Id: cvsanal_graph_heatmaps.py,v 1.2 2005/05/11 10:55:07 anavarro Exp $

"""
Generates heatmap images with the commiter activity in each period of time
for any given module. Therefore the whole life of the module is divided
in equally-large periods of time.

@author:       Gregorio Robles
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      grex@gsyc.escet.urjc.es
"""

import os, time
import intermediate_tables as intmodule

# Directory where evolution graphs will be located
config_graphsDirectory = 'heatmaps/'

def commiterListAndDict(row):
	"""
	Given a tuple of tuples with information on commiters and
	their first commit returns a tuple (that contains a list and
	a dictionary) with this information ordered

	@type  row: tuple of tuples
	@param row: each tuple contains following information:
	            | commiter | commiter_id | MIN(date) ORDERED

	@rtype: tuple of (list, dictionary)
	@return: List with all commiters ordered by their first commit and
	         dictionary that transforms order into commiter_id
	"""
	
	list = []
	d = {}
	i = 0
	for item in row:
		list.append(item[0])
		i +=1
		d[item[1]] = i
	return list, d
	

def commitersRepository(db, time_start, time_slots, interval):
	"""
	Returns a list with the contribution of commiters
	in a given period of time
	"""
	
	commiters = []
	end = time_start

	result = db.querySQL('commiters.commiter, commiters.commiter_id, MIN(log.date_log) AS min',\
			  'log, commiters', \
			  'log.commiter_id = commiters.commiter_id', \
			  'min',\
			  'commiters.commiter_id')
	
	commiterList, commiterDict = commiterListAndDict(result)
	commiters.append(db.uniqueresult2list(result))

	i = 0
	while i < time_slots:
		i += 1
		list = []
		start = end
		end += interval

		# Excluding po files
		# Uncomment this line and set not_po to '' to
		# include translation files
		result2 = db.querySQL('commiter_id, COUNT(*)', 'log, files', "date_log >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND files.file_id = log.file_id AND files.name not like 'po/%' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'commiter_id', 'commiter_id')

		list = db.doubleresult2list(result2)

		# get total number of commits
		total_commits = 0
		for item in list:
			total_commits += int(item[1])

		commiters_temp = []
		for item in range(0, len(commiters[0])):
			commiters_temp.append(0)

		# Avoiding division by zero error
		if total_commits == 0:
			total_commits = 1

		for item in list:
			commiters_temp[int(commiterDict[str(item[0])])-1] = (int(round(100*float(item[1])/total_commits + 0.4999)))
			# 0.4999 has been added in order to round to
			# the next integer (not 0.5 to make 0 commits not 1%)
		commiters.append(commiters_temp)

	return commiters


def commiters(db, moduleName, time_start, time_slots, interval):
	"""
	Returns a list with the contribution of commiters
	in a given period of time
	"""
	
	commiters = []
	end = time_start

	result = db.querySQL('commiters.commiter, commiters.commiter_id, MIN(log.date_log) AS min',\
			  'log, commiters', \
			  'log.commiter_id = commiters.commiter_id AND log.module_id=' + str(moduleName),\
			  'min',\
			  'commiters.commiter_id')
	
	commiterList, commiterDict = commiterListAndDict(result)
	commiters.append(db.uniqueresult2list(result))

	i = 0
	while i < time_slots:
		i += 1
		list = []
		start = end
		end += interval

		# Excluding po files
		# Uncomment this line and set not_po to '' to
		# include translation files
		result2 = db.querySQL('commiter_id, COUNT(*)', 'log, files', "log.module_id = '" + str(moduleName) + "' AND date_log >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND files.file_id = log.file_id AND files.name not like 'po/%' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'commiter_id', 'commiter_id')

		list = db.doubleresult2list(result2)

		# get total number of commits
		total_commits = 0
		for item in list:
			total_commits += int(item[1])

		commiters_temp = []
		for item in range(0, len(commiters[0])):
			commiters_temp.append(0)

		# Avoiding division by zero error
		if total_commits == 0:
			total_commits = 1

		for item in list:
			commiters_temp[int(commiterDict[str(item[0])])-1] = (int(round(100*float(item[1])/total_commits + 0.4999)))
			# 0.4999 has been added in order to round to
			# the next integer (not 0.5 to make 0 commits not 1%)
		commiters.append(commiters_temp)

	return commiters

def commiterList2file(list, time_slots='10'):
	"""
	Prints commiter list into file(s)
	There is a file for every 25 commiters in order to
	avoid getting a too small ploticus graph
	"""

	number_of_files = len(list[0])/25

	for file in range (1, number_of_files+1):
		data = open(config_graphsDirectory + str(file) + '.dat', 'w')
		for i in range(0, 25):
			string = ""
			for j in range(0, time_slots +1):
				string += str(list[j][i+(file-1)*25]) + "\t"
			data.write(string + '\n')
		data.close()

	data  = open(config_graphsDirectory + str(number_of_files + 1) + '.dat', 'w')
	for i in range(0, len(list[0]) - 25*number_of_files):
		string = ""
		for j in range(0, time_slots +1):
			string += str(list[j][i+25*number_of_files]) + "\t"
		data.write(string + '\n')
	data.close()

	return len(list[0]), number_of_files+1


def ploticus(module, number_of_dev, number_of_files):
	"""
	Prints the ploticus file and runs it by means of a shell
	"""

	for file in range(1, number_of_files + 1):
		ploticus = open(config_graphsDirectory + str(file) + '.ploticus', 'w')
		ploticus.write('#set SYM = "radius=0.1 shape=square style=filled"\n\n')
		ploticus.write('#proc page\n')
		ploticus.write('backgroundcolor: black\n')
		ploticus.write('color: white\n\n')
		ploticus.write('// get data..\n')
		ploticus.write('#proc getdata\n')
		ploticus.write('file: ' + config_graphsDirectory + str(file) + '.dat\n\n')
		ploticus.write('// set up plotting area..\n')
		ploticus.write('#proc areadef\n')
		ploticus.write('rectangle: 1 1.5 2 2\n')
		ploticus.write('autowidth 0.20 0.20 3.0\n')
		ploticus.write('autoheight 0.29 0.29 5.8\n')
		ploticus.write('yscaletype: categories\n')
		ploticus.write('ycategories: datafield=1\n')
		ploticus.write('yaxis.stubs: usecategories\n')
		ploticus.write('yaxis.tics: none\n')
		ploticus.write('yaxis.axisline: none\n')
		ploticus.write('yaxis.stubdetails: adjust=0.2,0\n')
		ploticus.write('xrange: 0 9\n')
		if file != number_of_files:
			ploticus.write('yrange: 1 26\n')
		else:
			ploticus.write('yrange: 1 ' + str(number_of_dev%25 +1) + '\n')
		ploticus.write('xaxis.location: max+0.2\n')
		ploticus.write('xaxis.stubs: list 0\\n1\\n2\\n3\\n4\\n5\\n6\\n7\\n8\\n9\n')
		ploticus.write('xaxis.tics: none\n')
		ploticus.write('xaxis.axisline: none\n')
		if number_of_files == 1:
			ploticus.write('xaxis.label: Module ' + module + '\n')
		else:
			ploticus.write('xaxis.label: Module ' + module + ' (' + str(file) +'/'+ str(number_of_files) + ')\n')
		ploticus.write('xaxis.labeldetails: size=21 style=B align=C adjust=0.1,0.4\n\n')
		ploticus.write('// set up legend entries for color gradients..\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=yellow @SYM\n')
		ploticus.write('label: more than 50%\n')
		ploticus.write('tag: 50\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=orange @SYM\n')
		ploticus.write('label: > 20%\n')
		ploticus.write('tag: 20\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=red @SYM\n')
		ploticus.write('label: > 10%\n')
		ploticus.write('tag: 10\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=lightpurple @SYM\n')
		ploticus.write('label: > 5%\n')
		ploticus.write('tag: 5\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=blue @SYM\n')
		ploticus.write('label: > 2%\n')
		ploticus.write('tag: 2\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=gray(0.4) @SYM\n')
		ploticus.write('label: at least 1 commit\n')
		ploticus.write('tag: 0.000001\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=black @SYM\n')
		ploticus.write('label: None\n')
		ploticus.write('tag: 0\n\n')
		ploticus.write('// loop through the data fields\n')
		ploticus.write('#set FLD = 2\n')
		ploticus.write('#for GROUP in A,B,C,D,E,F,G,H,I,J\n') # depends on the number of timeslots
		ploticus.write('  #set XLOC = $arith(@FLD-1)\n')
		ploticus.write('  #proc scatterplot\n')
		ploticus.write('  xlocation: @XLOC(s)\n')
		ploticus.write('  yfield: 1\n')
		ploticus.write('  symrangefield: @FLD\n')
		ploticus.write('  #set FLD = $arith( @FLD+1 )\n')
		ploticus.write('#endloop\n\n')
		if file == number_of_files:
			ploticus.write('#proc legend\n')
			ploticus.write('location: min+1.1 min-0.2\n')
			ploticus.write('format: multipleline\n')
			ploticus.write('sep: 0.2\n')
			ploticus.write('outlinecolors: yes\n')
		ploticus.close()

		os.system('ploticus -png /' + config_graphsDirectory + str(file) + '.ploticus -o ' + config_graphsDirectory + module + '___' + str(file) + '.png 2')

def plot(db):

        time_slots = 10
	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	# Getting heatmap for the whole repository
	print "Creating heat map for the whole repository"
	time_start = time.mktime(time.strptime('1997-04-09 00:25:19', '%Y-%m-%d %H:%M:%S'))
	time_finish = time.mktime(time.strptime('2007-04-21 00:01:05', '%Y-%m-%d %H:%M:%S'))
	interval = (time_finish - time_start) / time_slots
	commitersList = commitersRepository(db, time_start, time_slots, interval)
        number_of_dev, number_of_files = commiterList2file(commitersList, time_slots)
	ploticus("whole repository", number_of_dev, number_of_files)


	# Getting modules out of database
	moduleList = db.doubleStrInt2list(db.querySQL('module,module_id', 'modules'))

	for module in moduleList:
		print "Creating heat map for " + module[0]
                time_start = time.mktime(time.strptime(intmodule.first_commit(db,'log',"module_id = " + str(module[1])), '%Y-%m-%d %H:%M:%S'))
                time_finish = time.mktime(time.gmtime())
                interval = (time_finish - time_start) / time_slots
		commiterList = commiters(db, module[1], time_start, time_slots, interval)
		number_of_dev, number_of_files = commiterList2file(commiterList, time_slots)
		ploticus(module[0], number_of_dev, number_of_files)

