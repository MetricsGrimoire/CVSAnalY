<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |                                                                      |
// +----------------------------------------------------------------------+
// |       Copyright (c) 2003 Gregorio Robles.  All rights reserved       |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors: Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
// +----------------------------------------------------------------------+
//
// $Id: Index.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table;

$table->table_full('Welcome to '.$GLOBALS['config_sys_name'], '');

print '<p>';

$table->table_full('Introduction to '.$GLOBALS['config_sys_name'], 'This site contains statistics and graphs from the interaction with the CVS or Subversion repository. In order to facilitate analysis, you can retrieve general statistics or statistical information of a single module (usually a module is a <i>project</i> or <i>subproject</i>) or even a single developer - in our case being developers called <i>commiters</i>.');

$table->table_full('How to use this site', '
This site has a clear structure that can be followed easily through its navigation bar at the left hand side of your web browser.

<ul>
<li><b><i>About</i></b> allows you to deepen into the goals of CVSAnalY and the research that is done in the Libre Software Engineering field.</li>
<li><b><i>Statistics</i></b> is a place where the <b>general statistics</b> of the CVS or Subversion repository are shown.</li>
<li><b><i>Modules</i></b> contains general statistics on modules: number of interactions (commits), files, lines of code and so on. By looking at any given module, a detailed analysis of the module will be shown which includes commiters that have participated, evolution graphs, commiter heatmaps and generational analysis.</li>
<li><b><i>Commiters</i></b> contains a list of the project commiters (that can be sorted by different means). You can see the modules a commiter has been working on and other parameters.</li>
<li><b><i>Inequality</i></b> handles with how equal (or inequal) the participation of commiters in the project.
<li><b><i>FAQ</i></b> is where the most common questions on this website, the used methodology as well as the concepts it is based on are answered. Please refer to this page if you have any doubt.
<li><b><i>Credits</b></i>: people behind this site and the CVSAnalY project. If you want to provied feedback, that will be the place to look.</li>
<li><b><i>Search</i></b> boxes allow you to find a given module or commiter.</li>
</ul>
');

$table->table_full('More on Libre Software Engineering', '
If you are interested in the facts and figures that are shown in this site, 
then maybe it is a good idea to have a look at the
<a href="http://libresoft.dat.escet.urjc.es/">Libre Software Engineering</a>
project at the Universidad Rey Juan Carlos (Madrid, Spain). There you will find 
some links that show <a href="http://libresoft.dat.escet.urjc.es/index.php?menu=Results">results</a> for other Libre Software projects.
');

?>