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
# $Id: cvsanal_graph_inequality.py,v 1.3 2005/05/13 11:28:38 anavarro Exp $

import os, time, math

"""
You can find information about all these inequality indexes
in the following web page:
http://poorcity.richcity.org/

The comments I've added to this script are mostly taken from
that source, so refer to it if you are looking for a detailed
view of ineaquality coefficients and redundancy

In general:
* Z = coefficients are 0 =< Z < 1 (they will never reach 1)
* R = redundancies are 0 =< Z < oo
* E = wealth (here commits)
* A = people (here commiters)
* Z is invariante in scale with E and A

* Redundancies give an idea of the urge to distribute
* Redundancies are the difference between two entropies
"""

# Directory where evolution graphs will be located
config_graphsDirectory = 'inequality/'

def file_plot(module, title='title', xlabel ='xlabel', ylabel='ylabel', dataStyle = 'linespoints', label = ''):
	"""
	"""

	## Notice that changing output.write() by g() should
	## make it work with Gnuplot.py
	## this has been disabled as gnuplut.py does not handle
	## dates properly
	
	output = open(config_graphsDirectory + module + ".gnuplot", 'w')
	output.write('set xlabel "Time intervals from first commit' + "\n")
#	output.write('set label "' + label +'" at 5,1750' + "\n") # set label on the plot
	output.write('set key 80,700' + "\n") # set key
	output.write('set xrange [0:100]' + "\n")
	output.write('set grid' + "\n")
	output.write('set data style ' + dataStyle + "\n") # dataStyle can be `lines`, `points`, `linespoints`, `impulses`, `dots`, `steps`, `errorbars`, `boxes`, and `boxerrorbars`
	output.write('set pointsize 0.5' + "\n")
	output.write('set terminal png' + "\n")

	output.write('set title "Atkinson index (Demand coefficient) for module ' + module + '"' + "\n")
	output.write('set yrange [0:10000]' + "\n")
	output.write('set ylabel "Atkinson index (Demand coefficient)"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-atkinson.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:2 title \'Aggregated Atkinson index (Demand) for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:3 title \'Atkinson index (last 10 intervals) for ' + module + '\'' + "\n")

	output.write('set title "Theil redundancy for module ' + module + '"' + "\n")
	output.write('set yrange [0:30000]' + "\n")
	output.write('set ylabel "Theil redundancy"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-theil.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:4 title \'Aggregated Theil redundancy for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:5 title \'Theil redundancy (last 10 intervals) for ' + module + '\'' + "\n")

	output.write('set title "Reserve coefficient for module ' + module + '"' + "\n")
	output.write('set yrange [0:10000]' + "\n")
	output.write('set ylabel "Reserve coefficient"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-reserve.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:6 title \'Aggregated Reserve coefficient for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:7 title \'Reserve coefficient (last 10 intervals) for ' + module + '\'' + "\n")

	output.write('set title "Reserve coefficient for module ' + module + '"' + "\n")
	output.write('set yrange [0:10000]' + "\n")
	output.write('set ylabel "D&R coefficient"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-d_and_r.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:8 title \'Aggregated D&R coefficient for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:9 title \'D&R coefficient (last 10 intervals) for ' + module + '\'' + "\n")

	output.write('set title "Kullback-Liebler Redundancy for module ' + module + '"' + "\n")
	output.write('set yrange [0:30000]' + "\n")
	output.write('set ylabel "Kullback-Liebler Redundancy"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-kullback_liebler.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:10 title \'Aggregated Kullback-Liebler Redundancy for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:11 title \'Kullback-Liebler Redundancy (last 10 intervals) for ' + module + '\'' + "\n")

	output.write('set title "Hoover coefficient for module ' + module + '"' + "\n")
	output.write('set yrange [0:10000]' + "\n")
	output.write('set ylabel "Hoover coefficient"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-hoover.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:12 title \'Aggregated Hoover coefficient for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:13 title \'Hoover coefficient (last 10 intervals) for ' + module + '\'' + "\n")

	output.write('set title "Coulter coefficient for module ' + module + '"' + "\n")
	output.write('set yrange [0:10000]' + "\n")
	output.write('set ylabel "Coulter coefficient"' + "\n")
	output.write('set output "' + config_graphsDirectory + module + '-coulter.png"' + "\n")
	output.write('plot "' + config_graphsDirectory + module + '.dat" using 1:14 title \'Aggregated Coulter coefficient for ' + module + '\', "' + config_graphsDirectory + module + '.dat" using 1:15 title \'Coulter coefficient (last 10 intervals) for ' + module + '\'' + "\n")

	output.close()
	
	# Execute gnuplots' temporary file
	os.system('gnuplot ' + config_graphsDirectory + module + ".gnuplot")

	# Delete temporary files
	os.system('rm ' + config_graphsDirectory + module + ".dat")
	os.system('rm ' + config_graphsDirectory + module + ".gnuplot")


def atkinsonF(commitList, Atot, Etot):
	"""
	Atkinson index
	(also known as the Demand coefficient)
	(it is relative to the McRae coefficient: ZMacRae = 1-ZDemand)
	ZDemand = 1-exp(sumi=1..N(Ei x ln(Ai/Ei))/Etot) x Etot/Atot = 1-ZMacRae

	In our case: Ai = constant = 1
	Atot = total commiters;	Etot = total commits

	* Expresses ineaquality in meritocracies (free competition, in
	corporate and market-oriented environments)
	* max if Ei -> 0
	* ZDemand x Etot have a completely unsatisfied demand for wealth
	* Gives how big in an enthropically equivalent two-class-meritocracy
	the class is that has no income (wealth)
	"""

	sum = 0
	for commits in commitList:
		sum += int(commits) * math.log(1.0/int(commits))
	sum = sum / Etot
	return 1 - math.exp(sum) * (Etot+0.0)/Atot
	

def theilF(ZDemand):
	"""
	Theil Redundancy  	
	RTheil = -ln(1-ZDemand) = -ln( ZMacRae) 

	Atot = total commiters; Etot = total commits
	"""
	if ZDemand == 1.0:
		return 999999999
	else:
		return - math.log(1 - ZDemand)

def reserveF(commitList, Atot, Etot):
	"""
	Reserve coefficient
	ZReserve = 1 - exp(sumi=1..N(Ai x ln(Ei/Ai))/Atot) x Atot/Etot

	In our case: Ai = constant = 1
	Atot = total commiters; Etot = total commits

	* Expresses inequality of a distribution in which only E (wealth)
	can be distributed (no competition, planned economies)
	* ZReserve is ZDemand with As and Es swapped
	* max if Ai -> 0
	* ZReserve: ownerless reserves ZReserv x Etot
	"""

	sum = 0
	for commits in commitList:
		sum += math.log(int(commits))

	return 1 - math.exp(sum/Atot) * ((Atot+0.0)/Etot)

def d_and_rF(ZDemand, ZReserve):
	"""
	D&R coefficient  	
	ZD&R = 1 - exp(-RKL) = 1-sqrt((1-ZDemand) x (1-ZReserve))

	* Its redundancy is the Kullback-Liebler redundancy
	* A and E can be distributed
	* max if Ei -> 0 or if Ai -> 0
	"""

	return 1 - math.sqrt((1-ZDemand) * (1-ZReserve))

def kullback_lieblerF(d_and_r):
	"""
	Kullback-Liebler redundancy
	RKL = RD&R = -ln(1-ZD&R)

	* Gives how inhomogeneous two things are mixed together, i.e
	how much space is given for further mixing
	"""

	if d_and_r == 1.0:
		return 999999
	else:
		return - math.log(1-d_and_r)

def hooverF(commitList, Atot, Etot):
	"""
	Hoover coefficient
	ZHoover = sumi=1..N(abs(Ei/Etot-Ai/Atot))/2

	In our case: Ai = constat = 1
	Atot = total commiters; Etot = total commits

	* Gives which ratio of total wealth or of population has to
	be redistributed in order to reach complete equality
	* It can be seen as the normalized mean deviation
	"""

	sum = 0
	for commits in commitList:
		sum += abs((int(commits)+0.0)/Etot - 1.0/Atot)

	return sum/2

def coulterF(commitList, Atot, Etot):
	"""
	Coulter coefficient
	ZCoulter = sqrt(sumi=1..N((Ei/Etot-Ai/Atot)^2)/2)

	In our case: Ai = constat = 1
	Atot = total commiters; Etot = total commits

	* It can be seen as the root mean square (also relative to
	the standard deviation)
	"""

	sum = 0
	for commits in commitList:
		sum += math.pow((int(commits)+0.0)/Etot - 1.0/Atot, 2)

	return math.sqrt(sum/2)

def avoidTooSmall(value):
	"""
	This is done in order to avoid python errors in calculating very
	small values which indeed are zero.
	"""

	if abs(value) < 0.000001:
		value = 0.0
	return value

def indexes2db(module, atkinson, theil, reserve, d_and_r, kullback_liebler, hoover, coulter):
	"""
	"""

	# Looking for the module id
	#result = querySQL('module_id', 'modules', "module='" + module + "'")
	db.query("UPDATE cvsanal_temp_inequality SET atkinson ='" + str(atkinson) + "', theil  ='" + str(theil) + "', reserve  ='" + str(reserve) + "', d_and_r ='" + str(d_and_r) + "', kullback_liebler ='" + str(kullback_liebler) + "', hoover ='" + str(hoover) + "', coulter  ='" + str(coulter) + "' WHERE module_id = '" + str(module) + "'")


def browseInTime(module_id, moduleName, time_start, time_slots, interval):
	"""
	"""

	output = open(config_graphsDirectory + moduleName + '.dat', 'w')

	i = 0
	start = time_start
	end = time_start
	while i < time_slots:
		i += 1
		if i > 9:
			start = end - 9*interval
		else:
			start = time_start
		end += interval
		where = ""

		# Aggregated index
		commitList = uniqueresult2list(querySQL('COUNT(*) AS count', 'log', "date_log > '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time_start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'count', 'commiter_id'))
		total_commits = 0
		total_commiters = 0
		for commits in commitList:
			total_commits += int(commits)
			total_commiters += 1
		if total_commiters == 0:
			atkinson_agg = 0
			theil_agg = 0
			reserve_agg = 0
			d_and_r_agg = 0
			kullback_liebler_agg = 0
			hoover_agg = 0
			coulter_agg = 0
		else:
			atkinson_agg = atkinsonF(commitList, total_commiters, total_commits)
			theil_agg = theilF(atkinson_agg)
			reserve_agg = reserveF(commitList, total_commiters, total_commits)
			d_and_r_agg = d_and_rF(atkinson_agg, reserve_agg)
			kullback_liebler_agg = kullback_lieblerF(d_and_r_agg)
			hoover_agg = hooverF(commitList, total_commiters, total_commits)
			coulter_agg = coulterF(commitList, total_commiters, total_commits)

		indexes2db(module_id, avoidTooSmall(atkinson_agg), avoidTooSmall(theil_agg), avoidTooSmall(reserve_agg), avoidTooSmall(d_and_r_agg), avoidTooSmall(kullback_liebler_agg), avoidTooSmall(hoover_agg), avoidTooSmall(coulter_agg))

		# Delta index
		commitList = uniqueresult2list(querySQL('COUNT(*) AS count', 'log', "date_log > '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(start)) + "' AND date_log < '" + time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(end)) + "'", 'count', 'commiter_id'))
		total_commits = 0
		total_commiters = 0
		for commits in commitList:
			total_commits += int(commits)
			total_commiters += 1
		if total_commiters == 0:
			atkinson = 0
			theil = 0
			reserve = 0
			d_and_r = 0
			kullback_liebler = 0
			hoover = 0
			coulter = 0
		else:
			atkinson = atkinsonF(commitList, total_commiters, total_commits)
			theil = theilF(atkinson)
			reserve = reserveF(commitList, total_commiters, total_commits)
			d_and_r = d_and_rF(atkinson, reserve)
			kullback_liebler = kullback_lieblerF(d_and_r)
			hoover = hooverF(commitList, total_commiters, total_commits)
			coulter = coulterF(commitList, total_commiters, total_commits)

		
		output.write(str(i)
			     + '\t' + str(int(10000 * atkinson_agg))  + '\t' + str(int(10000 * atkinson))
			     + '\t' + str(int(10000 * theil_agg))  + '\t' + str(int(10000 * theil))
			     + '\t' + str(int(10000 * reserve_agg))  + '\t' + str(int(10000 * reserve))
			     + '\t' + str(int(10000 * d_and_r_agg))  + '\t' + str(int(10000 * d_and_r))
			     + '\t' + str(int(10000 * kullback_liebler_agg))  + '\t' + str(int(10000 * kullback_liebler))
			     + '\t' + str(int(10000 * hoover_agg))  + '\t' + str(int(10000 * hoover))
     			     + '\t' + str(int(10000 * coulter_agg))  + '\t' + str(int(10000 * coulter))
			     + '\n')
	output.close()

def graph_inequality(db):

	if not os.path.isdir(config_graphsDirectory):
		os.mkdir(config_graphsDirectory)
	time_slots = 100
	# Getting modules out of database
        result = db.doubleStrInt2list(db.querySQL('module,module_id', 'modules'))

	print "Calculating several inequality indexes and redundancies"

	for module in result:
		print "Working with " + module[0]
		moduleCode = str(module[1])
		moduleName = str(module[0])
                time_start = time.mktime(time.strptime(first_commit('log','module_id = ' + str(module[1])), '%Y-%m-%d %H:%M:%S'))
                time_finish =  time.mktime(time.gmtime())
                interval = (time_finish - time_start) / time_slots
		browseInTime(moduleCode, moduleName, time_start, time_slots, interval)
		file_plot(moduleName)

