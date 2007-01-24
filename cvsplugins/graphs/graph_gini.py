#!/usr/bin/python
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

import os, time

# Directory where evolution graphs will be located
config_graphsDirectory = 'gini/'

def file_plot(outputFile, listValues, title='title', xlabel ='xlabel', ylabel='ylabel', dataStyle = 'linespoints', label = ''):
	"""
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly

	output = open(config_graphsDirectory + outputFile + ".gnuplot", 'w')
	output.write('set title "Lorenz curve for module ' + title + '"' + "\n")
	output.write('set xlabel "Number of developers: ' + xlabel + ' (normalized to 1)' + "\n")
	output.write('set label "Gini coefficient (normalized): ' + label +'" at 0.088,0.82' + "\n")
	output.write('set key 0.4,0.96' + "\n")
	output.write('set xrange [0:1]' + "\n")
	output.write('set yrange [0:1]' + "\n")
	output.write('set ylabel "Number of total commits: '+ ylabel  + ' (normalized to 1)"' + '"' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n")
	output.write('set pointsize 1.35' + "\n")
	output.write('set terminal png' + "\n")
	output.write('set output "' + config_graphsDirectory + outputFile + '.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + outputFile + '.dat" using 1:2 title \'Lorenz curve for ' + title + '\' , "' + config_graphsDirectory + outputFile + '.dat" using 1:3 title \'Line of perfect equality\'' + "\n")
	output.close()

	# Write data into data file
	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for value in listValues:
		output.write(str(value[0]) + "\t" + str(value[1]) + "\t" + str(value[0]) + "\n")
	output.close()

	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + outputFile + ".gnuplot 2> /dev/null")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
	os.system('rm ' + config_graphsDirectory + outputFile + ".gnuplot"
)
def file_plotAllInOne(outputFile, listValues, title='', xlabel ='', ylabel='', dataStyle = 'linespoints'):
	"""
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly

	output = open(config_graphsDirectory + outputFile + ".gnuplot", 'w')
	output.write('set title "Lorenz curve for module ' + title + '"' + "\n")
	output.write('set xlabel "Developers (normalized to 1)' + "\n")
	output.write('set key 0.4,0.96' + "\n") # set key
	output.write('set xrange [0:1]' + "\n")
	output.write('set yrange [0:1]' + "\n")
	output.write('set ylabel "Number of commits (normalized to 1)"' + '"' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize 0.5' + "\n")
	output.write('set terminal png' + "\n")
	output.write('set output "' + config_graphsDirectory + outputFile + '.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + outputFile + '.dat" using 1:2 title \'Lorenz curve for the ' + title + ' project\' , "' + config_graphsDirectory + outputFile + '.dat" using 1:3 title \'Line of perfect equality\'' + "\n")
	output.close()

	# Write data into data file
	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	for value in listValues:
		output.write(str(value[0]) + "\t" + str(value[1]) + "\t" + str(value[0]) + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + outputFile + ".gnuplot 2> /dev/null")

	# Delete temporary files
#	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
#	os.system('rm ' + config_graphsDirectory + outputFile + ".gnuplot")

def file_plotAllInOneB(outputFile, listOfLists, title='', xlabel ='', ylabel='', dataStyle = 'linespoints'):
	"""
	"""
	
	output = open(config_graphsDirectory + outputFile + ".ploticus", 'w')
	output.write("// Specify some data using proc getdata\n")
	output.write("#proc getdata\n")
	output.write("file: " + config_graphsDirectory + outputFile + ".dat\n\n")
	output.write("// set up the plotting area using proc areadef\n")
	output.write("#proc areadef\n")
	output.write("  rectangle: 0.5 0.5 7 7\n")
	output.write("  xrange: 0 1\n")
	output.write("  yrange: 0 1\n")
	output.write("  frame: yes\n\n")
	output.write("// set up an X axis using proc xaxis\n")
	output.write("#proc xaxis\n")
	output.write("  grid: color=black\n")
	output.write("  stubs incremental 0.25 1\n")
	output.write("  stubrange: 0 1\n\n")
	output.write("// set up a Y axis using proc yaxis\n")
	output.write("#proc yaxis\n")
	output.write("  grid: color=black\n")
	output.write("  stubs incremental 0.25 1\n")
	output.write("  stubrange: 0 1\n\n")
	output.write("// Do perfect inequality curve using proc lineplot\n")
	output.write("#proc lineplot\n")
	output.write("  xfield: 1\n")
	output.write("  yfield: 1\n")
	output.write("  linedetails: color=green width=1\n\n")
	i = 0
	for list in listOfLists:
		output.write("// Do curve using proc lineplot\n")
		output.write("#proc lineplot\n")
		i+=1
		output.write("  xfield: " + str(i) + "\n")
		i+=1
		output.write("  yfield: " + str(i) + "\n")
		output.write("  linedetails: color=" + getColor(len(list)) + " width=0.5\n\n")
	output.close()

	# Write data into data file
 
	output = open(config_graphsDirectory + outputFile + ".dat", 'w')
	max = 0
	for list in listOfLists:
		if max < len(list):
			max = len(list)
	i=0
	while i < max:
		j=0
		string = ""
		while j < len(listOfLists):
			try:
				string += str(listOfLists[j][i][0]) + "\t" + str(listOfLists[j][i][1]) + "\t"
			except IndexError:
				string += "1\t" + "1\t"
			j+=1
		i+=1
		output.write(string + "\n")
	output.close()

	# Execute ploticus' temporary file
	os.system('ploticus -png ' + config_graphsDirectory + outputFile + '.ploticus -o ' + config_graphsDirectory + outputFile + ".png")
	# Delete temporary files
#	os.system('rm ' + config_graphsDirectory + outputFile + ".dat")
#	os.system('rm ' + config_graphsDirectory + outputFile + ".ploticus")

def getColor(listLength):
	"""
	given a number (the length of the list,
	returns a color (string)
	"""

	if listLength < 3:
		return 'darkblue'
	elif listLength < 6:
		return 'blue'
	elif listLength < 12:
		return 'purple'
	elif listLength < 33:
		return 'green'
	elif listLength < 50:
		return 'orange'
	else:
		return 'red'

def giniInput(db, input):
	"""
	Extracts the data from the database and outputs
	it in a file named after the variable input
	in the polygini.pl input format
	"""

	print "Calculating gini coefficients"
	GiniInput = open(config_graphsDirectory + input, 'w')

	result = db.doubleStrInt2list(db.querySQL('module,module_id', 'modules'))
	for module in result:
		commitList = db.querySQL('COUNT(*) AS count', 'log', 'module_id=' + str(module[1]), 'count', 'commiter_id')
		if commitList:
			string =  module[0]
		for commits in commitList:
			string += "," + str(commits[0])
		if commitList:
			GiniInput.write(string + '\n')
	GiniInput.close()

def giniOutput(input, output):
	"""
	Runs polygini.pl on the input file and returns
	its output in output
	"""

	os.system("/usr/bin/polygini.pl -precision 5 -lorenz -ntiles 4 -id -comment copy -zeromsg -count -sum < " + config_graphsDirectory + "gini.in > " + config_graphsDirectory + output)

def lorenzAllInOne(input):
	"""
	Creates one lorenz graph for all projects
	"""

	print "Making unique Lorenz graph for all projects"
	GiniOutput = open(config_graphsDirectory + input, 'r')
	values = [[0,0]]
	while 1:
		line = GiniOutput.readline()
		if not line:
			break
		elementList = line.split(',')
		i = 0
		values.append([0,0])
		for element in range(4, int(elementList[2])+4):
			i+=1
			values.append([float(i)/int(elementList[2]), elementList[element]])
	file_plotAllInOne ('all', values, "Lorentz curve")


def lorenzAllInOneB(input):
	"""
	Creates one lorenz graph for all projects
	"""

	print "Making unique Lorenz graph for all projects"
	GiniOutput = open(config_graphsDirectory + input, 'r')
	listOfLists = []
	while 1:
		line = GiniOutput.readline()
		if not line:
			break
		elementList = line.split(',')

		i = 0
		values = [[0,0]]
		for element in range(4, int(elementList[2])+4):
			i+=1
			values.append([float(i)/int(elementList[2]), elementList[element]])
		listOfLists.append(values)

	file_plotAllInOneB ('all', listOfLists, "Lorentz curve")


def lorenz(input):
	"""
	Creates the lorenz graph out of the file with gini coefficients
	"""

	print "Making Lorenz graphs"
	GiniOutput = open(config_graphsDirectory + input, 'r')
	while 1:
		line = GiniOutput.readline()
		if not line:
			break
		elementList = line.split(',')
		if int(elementList[2]) == 1:
			giniNormalized = 1.0
		else:
			giniNormalized = float(elementList[1]) * float(elementList[2]) / (int(elementList[2]) -1)
		i = 0
		values = [[0,0]]
		for element in range(4, int(elementList[2])+4):
			i+=1
			values.append([float(i)/int(elementList[2]), elementList[element]])

		file_plot(elementList[0],
                        values,
                        elementList[0],
                        elementList[2],
                        elementList[3],
                        'linespoints',
                        elementList[1] + ' (' + str(giniNormalized) +')')

def gini2db(db, input):
	"""
	Inserting gini coefficient to database
	"""

	print "Inserting normalized Gini coefficients into database"
	GiniOutput = open(config_graphsDirectory + input, 'r')
	while 1:
		line = GiniOutput.readline()
		if not line:
			break
		elementList = line.split(',')
		if int(elementList[2]) == 1:
			giniNormalized = 1.0
		else:
			giniNormalized = float(elementList[1]) * float(elementList[2]) / (int(elementList[2]) -1)

		eu = (1-float(elementList[1]))/(1+float(elementList[1]))

		# Looking for the module id
		result = db.querySQL ('module_id', 'modules', "module='" + elementList[0] + "'")
                moduleName = result[0][0]
		db.insertData ("UPDATE cvsanal_temp_inequality SET gini ='" + str(elementList[1]) + "' WHERE module_id = '" + moduleName + "'")
		db.insertData ("UPDATE cvsanal_temp_inequality SET concentration='" + str(giniNormalized) + "' WHERE module_id = '" + moduleName + "'")
		db.insertData ("UPDATE cvsanal_temp_inequality SET eu='" + str(eu) + "' WHERE module_id = '" + moduleName + "'")

def graph_gini(db):

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	giniInput(db, 'gini.in')
	giniOutput('gini.in', 'gini.out')
	lorenz('gini.out')
	gini2db(db, 'gini.out')

def graph_giniAllInOne(db):
	"""
	The same as graph_gini, but all the modules lorenz curves are displayed
	in an unique figure
	"""

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)

	giniInput(db, 'gini.in')
	giniOutput('gini.in', 'gini.out')
	lorenzAllInOneB('gini.out')

def plot (db):
	graph_gini (db)
	graph_giniAllInOne (db)

