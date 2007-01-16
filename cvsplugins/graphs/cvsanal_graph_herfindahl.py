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
# $Id: cvsanal_graph_herfindahl.py,v 1.2 2005/04/20 22:42:30 anavarro Exp $

from config import *
from db import *
import os, time

# Directory where evolution graphs will be located
config_graphsDirectory = config_graphsDirectory + 'inequality/'

def file_plot(module, title='title', xlabel ='xlabel', ylabel='ylabel', dataStyle = 'linespoints', label = ''):
	"""
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly
	
	output = open(config_graphsDirectory + module + ".gnuplot", 'w')
	output.write('set title "Herfindahl index in time for module ' + module + '"' + "\n")
	output.write('set xlabel "Time intervals from first commit' + "\n")
#	output.write('set label "' + label +'" at 5,1750' + "\n") # set label on the plot
	output.write('set key 80,700' + "\n") # set key
	output.write('set xrange [0:100]' + "\n")
	output.write('set yrange [0:10000]' + "\n")
	output.write('set ylabel "Herfindahl index"' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize 0.5' + "\n")
	output.write('set terminal png' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-herfindahl.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:2 title \'Aggregated Herfindahl index for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:3 title \'Herfindahl index (last 10 intervals) for ' + module + '\'' + "\n")
	output.close()
	
	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + module + ".gnuplot")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + module + ".dat")
	os.system('rm ' + config_graphsDirectory + module + ".gnuplot")

def herfindahl2db(module, herfindahl):
	"""
	"""

	# Looking for the module id
	result = querySQL('module_id', 'modules', "module='" + module + "'")
	db.query("UPDATE cvsanal_temp_inequality SET herfindahl = '" + str(herfindahl) + "' WHERE module_id = '" + str(result[0][0]) + "'")

def calculateHerfindahl(module, moduleName, time_start, time_slots, interval):
	"""
	"""

	output = open(config_graphsDirectory + module + '.dat', 'w')

	i = 0
	start = time_start
	end = time_start
	while i < time_slots:
		i += 1
		list = []
		if i > 9:
			start = end - 9*interval
		else:
			start = time_start
		end += interval
		where = ""
		# KDE-specific code
#		moduleName_kde = moduleName + "_log, " + moduleName + "_commiters"
#		where = "AND " + moduleName + "_commiters.commiter_id=" + moduleName + "_log.commiter_id AND commiter!='kulow'"
#		commitList = querySQL('COUNT(*) AS count', moduleName + '_log', "date >'" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'" + where, 'count', 'commiter_id')

		# Aggregated index
		commitList = querySQL('COUNT(*) AS count', 'log', "date_log > '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time_start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'count', 'commiter_id')
		total = 0
		herfindahl_agg = 0
		for commits in commitList:
			herfindahl_agg += pow(int(commits[0]), 2)
			total += int(commits[0])
		if total == 0:
			herfindahl_agg = 0
		else:
			herfindahl_agg = 10000 * herfindahl_agg / (pow(total,2))
		herfindahl2db(module, herfindahl_agg)

		# Delta index
		commitList = querySQL('COUNT(*) AS count', 'log', "date_log > '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'count', 'commiter_id')
		total = 0
		herfindahl = 0
		for commits in commitList:
			herfindahl += pow(int(commits[0]), 2)
			total += int(commits[0])
		if total == 0:
			herfindahl = 0
		else:
			herfindahl = 10000 * herfindahl / (pow(total,2))
		
		output.write(str(i) + '\t' + str(herfindahl_agg)  + '\t' + str(herfindahl) + '\n')
	output.close()

def graph_herfindahl():
	"""
	"""
	
	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)
	time_slots = 100
	# Getting modules out of database
	moduleList = uniqueresult2list(querySQL('module', 'modules'))

	print "Calculating the Herfindahl-Hirschfeld index"

	for module in moduleList:
		print "Working with " + module
		moduleName = db_module(module)
                time_start = time.mktime(time.strptime(first_commit(moduleName + '_log'), '%Y-%m-%d %H:%M:%S'))
                time_finish =  time.mktime(time.gmtime())
                interval = (time_finish - time_start) / time_slots
		calculateHerfindahl(module, moduleName, time_start, time_slots, interval)
		file_plot(module)

if __name__ == '__main__':
	graph_herfindahl()
	db.close()
