#!/usr/bin/python2.2
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
# $Id: cvsanal_graph_filetype_correlation.py,v 1.3 2005/05/11 10:55:07 anavarro Exp $

from config import *
from config_files import *
from db import *
import os, time, Image

# Directory where evolution graphs will be located
config_graphsDirectory = config_graphsDirectory + 'filetype/'

def ploticus(module, time_slots):
	"""
	Prints the ploticus file and runs it by means of a shell command
	"""

	for i in range(1, time_slots+1):
		ploticus = open(config_graphsDirectory + module + '_' + str(i) + '.ploticus', 'w')
		ploticus.write('#set SYM = "radius=0.1 shape=square style=filled"\n\n')
		ploticus.write('#proc page\n')
		ploticus.write('backgroundcolor: black\n')
		ploticus.write('color: white\n\n')
		ploticus.write('// get data..\n')
		ploticus.write('#proc getdata\n')
		ploticus.write('file: ' + config_graphsDirectory + module + '_' + str(i) + '.dat\n\n')
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
		ploticus.write('yaxis.stubdetails: adjust=0.0,0\n')
		ploticus.write('xrange: 1 7\n')
		ploticus.write('yrange: 1 8\n')
		ploticus.write('xaxis.location: max+0.8\n')
		ploticus.write('xaxis.stubs: list documentatin\\nimages\\ntranslations\\nui\\nmultimedia\\ndevevelopment\\nunknown\\n\n')
		ploticus.write('xaxis.stubvert: yes\n')
		ploticus.write('xaxis.tics: none\n')
		ploticus.write('xaxis.axisline: none\n')
		ploticus.write('xaxis.label: Module ' + module + ' (' + str(i) + ')\n')
		ploticus.write('xaxis.labeldetails: size=21 style=B align=C adjust=0.1,0.4\n\n')
		ploticus.write('// set up legend entries for color gradients..\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=yellow @SYM\n')
		ploticus.write('label: more than 80%\n')
		ploticus.write('tag: 80\n\n')
		ploticus.write('#proc legendentry\n')
	       	ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=red @SYM\n')
		ploticus.write('label: > 50%\n')
		ploticus.write('tag: 50\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=lightpurple @SYM\n')
		ploticus.write('label: > 20%\n')
		ploticus.write('tag: 20\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=blue @SYM\n')
		ploticus.write('label: > 0%\n')
		ploticus.write('tag: 1\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=gray(0.4) @SYM\n')
		ploticus.write('label: 0%\n')
		ploticus.write('tag: 0\n\n')
		ploticus.write('#proc legendentry\n')
		ploticus.write('sampletype: symbol\n')
		ploticus.write('details: fillcolor=black @SYM\n')
		ploticus.write('label: None\n')
		ploticus.write('tag: -1\n\n')
		ploticus.write('// loop through the data fields\n')
		ploticus.write('#set FLD = 2\n')
		ploticus.write('#for GROUP in A,B,C,D,E,F,G\n') # 
		ploticus.write('  #set XLOC = $arith(@FLD-1)\n')
		ploticus.write('  #proc scatterplot\n')
		ploticus.write('  xlocation: @XLOC(s)\n')
		ploticus.write('  yfield: 1\n')
		ploticus.write('  symrangefield: @FLD\n')
		ploticus.write('  #set FLD = $arith( @FLD+1 )\n')
		ploticus.write('#endloop\n\n')
		ploticus.write('#proc legend\n')
		ploticus.write('location: min+1.1 min-0.2\n')
		ploticus.write('format: multipleline\n')
		ploticus.write('sep: 0.2\n')
		ploticus.write('outlinecolors: yes\n')
		ploticus.close()

		os.system('ploticus -png /' + config_graphsDirectory + module +  '_' + str(i) + '.ploticus -o ' + config_graphsDirectory + module + '_' + str(i) + '.png')
#		os.system('rm ' + config_graphsDirectory + module + '_' + str(i) + '.dat')
#		os.system('rm ' + config_graphsDirectory + module + '_' + str(i) + '.ploticus')

#	os.system('gifsicle --delay=5 --loop ' + config_graphsDirectory + module + '_*.png > ' + config_graphsDirectory + module + '.png')
#	os.system('rm ' + config_graphsDirectory + module + '_*.png')

def sumDict(dictionary):
	"""
	Sum all values of a dictionary
	"""

	sum = 0
	for element in dictionary:
		sum += dictionary[element]
	return sum

def correlateDicts(dict1, dict2):
	"""
	Correlates dict1 with dict2
	Note that correlateDicts(dict1,dict2) != correlateDicts(dict2,dict1)
	"""

	if not dict1 or not dict2:
		return (-1, -1)
	
	common_elements = 0
	common_values = 0
	for element in dict1:
		if element in dict2:
			common_elements+=1
			common_values += dict1[element]

	common_elements_normalized = 100 * (common_elements+0.0) / len(dict1)

	divisor = sumDict(dict1)
	if divisor != 0:
		common_values_normalized = 100 * (common_values + 0.0) / divisor
	else:
		common_values_normalized = 0
		
	return (int(common_elements_normalized), int(common_values_normalized))

def printMatrix(module, list, slot):
	"""
	"""

	data = open(config_graphsDirectory + module + '_' + str(slot) + '.dat', 'w')

# 	string='\t'
# 	for element in config_files_names:
# 		string += element[0:4] + '\t'
# 	data.write(string + '\n')

	column=0
	line=0
	string = config_files_names[line] + '\t'
	for tuples in list:
		column+=1
		if column < len(config_files_names):
			string += str(tuples[1]) + '\t'
		else:
			string += str(tuples[1])
			data.write(string + '\n')
			column = 0
			line +=1
			if line < len(config_files_names):
				string = config_files_names[line] + '\t'
	data.close()

def correlateFileTypes(module, time_start, time_slots, interval):
	"""
	"""

	end = time_start
	moduleName = db_module(module)

	i = 0
	while i < time_slots:
		i += 1
		dictList = []
		matrixList = []
		start = end
		end += interval

		for fileType in config_files_names:
			result = querySQL('commiter_id, COUNT(DISTINCT(request_id))',
					  'log, cvsanal_modrequest',
					  "log.commit_id=cvsanal_modrequest.commit_id AND cvs_flag=0 AND fileType=" + str(config_files_names.index(fileType)) + " AND date_log >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'",
					  'commiter_id',
					  'commiter_id')
			dictList.append(doubleresult2dict(result))

		index1 = -1
		for dict1 in dictList:
			index1 +=1
			index2 = -1
			for dict2 in dictList:
				index2 +=1
				# diagonal is ommited for obvious reasons
				# (it will be always 100%)
				if index1 == index2:
					matrixList.append((-1,-1))
				else:
					matrixList.append(correlateDicts(dict1, dict2))
		
		printMatrix(module, matrixList, i)

def pngs2animatedgif(module, time_slots):
	"""
	From a series of PNG files, creates an animated GIF
	"""

	for index in range(1, time_slots +1):
		try:
			im = Image.open(config_graphsDirectory + module + "_" + str(index) + ".png")
		except IOError:
			print "Error opening " + config_graphsDirectory + module + "_" + str(index) + ".png"
		im.save(config_graphsDirectory + module + "_" + str(index) + ".gif", "GIF")


	# Create whirlgif script that transforms gif to animated gif
	# TODO: this should be really another function
	output = open(config_graphsDirectory + module + ".whirlgif", 'w')
	output.write('#! /bin/sh \n')
	output.write('whirlgif -globmap -background 5 -loop 0 -trans 5 \\\n')
	output.write('-disp back -o ' + config_graphsDirectory + module + '-animated.gif \\\n')
	output.write('-time 250 ' + config_graphsDirectory + module + '_1.gif \\\n')
	for index in range(2, 10):
		output.write('-time 120 ' + config_graphsDirectory + module + '_' + str(index) + '.gif \\\n')
	output.write('-time 200 ' + config_graphsDirectory + module + '_10.gif \n')
	output.write('exit\n')
	output.close()

	# Execute gnuplots' temporary file
	os.system('sh ' + config_graphsDirectory + module + ".whirlgif")

	# Delete temporary files
#	os.system('rm ' + config_graphsDirectory + module + ".whirlgif")
#	os.system('rm ' + config_graphsDirectory + module + "_*.gif")
#	os.system('rm ' + config_graphsDirectory + module + "_*.png")
	

def graph_filetype_correlation():
	"""
	"""

        time_slots = 10
	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	# For the whole repository
	print "Creating filetype correlation heat map for the whole repository" 
	time_start = time.mktime(time.strptime('1997-04-09 00:00:00', '%Y-%m-%d %H:%M:%S'))
	time_finish =  time.mktime(time.strptime('2005-04-21 00:00:00', '%Y-%m-%d %H:%M:%S'))
	interval = (time_finish - time_start) / time_slots
	correlateFileTypes('repository', time_start, time_slots, interval)
	ploticus('repository', time_slots)
	pngs2animatedgif('repository', time_slots)
	
	# Getting modules out of database
	moduleList = uniqueresult2list(querySQL('module', 'modules'))

	for module in moduleList:
		print "Creating filetype correlation heat map for " + module
		moduleName = db_module(module)
                time_start = time.mktime(time.strptime(first_commit(moduleName + '_log'), '%Y-%m-%d %H:%M:%S'))
                time_finish =  time.mktime(time.gmtime())
                interval = (time_finish - time_start) / time_slots
		correlateFileTypes(module, time_start, time_slots, interval)
		ploticus(module, time_slots)
		pngs2animatedgif(module, time_slots)
		
if __name__ == '__main__':

	graph_filetype_correlation()
	db.close()
