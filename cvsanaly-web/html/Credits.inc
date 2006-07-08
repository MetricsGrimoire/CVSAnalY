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
// $Id: Credits.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table;

$table->table_full('Credits', '');

print '<p>';

$table->table_full('About this site', 'This site about '.$GLOBALS['config_sys_name'].' has been installed, configured and is being held by '.$GLOBALS['config_sys_credits']);

htmlp_anchor("copyright");
$table->table_full('Copyright', 'All images, statistics and data on this site are Copyright <i>(C) Grupo de Sistemas y Comunicaciones (Universidad Rey Juan Carlos)</i> and may be reproduced for any purpose provided they are credited to the Libre Software Engineering project at the Universidad Rey Juan Carlos using an attribution like "(C) Grupo de Sistemas y Comunicaciones (Universidad Rey Juan Carlos), from http://libresoft.dat.escet.urjc.es".');


$table->table_full('Libre Software Engineering at Universidad Rey Juan Carlos', 'This software has been created by members of a research group at GSyC. The research group at GSyC coordinated by Jesús M. González-Barahona is mainly interested in Software Engineering issues regarding libre software development, specially those focused on (quantitative) measurement aspects and developer interaction, and in distributed tools for collaboration in libre software projects. You can have more information about their <a href="http://barba.dat.escet.urjc.es">Libre Software Engineering</a> project in his site.');

$table->table_full('J. Mallett', '<a href="http://people.freebsd.org/~jmallett/">J. Mallett</a> is the original author of cvstat, a tool written in Perl that can be seen as the predecesor of CVSanalY.');

$table->table_full('Rishab A. Ghosh', '<a href="http://dxm.org/">Rishab Ghosh</a> is the original author of the polygini perl script on which the Gini coefficient calculation and Lorenz graph generation is based on.');

$table->table_full('Others', '
<a href="http://wwwai.wu-wien.ac.at/mitarbeiter/koch.html">Stefan Koch</a> from the Wirtschaftsuniversität Wien
<br>Carlos Perell&oacute;n Mar&iacute;n and the <a href="http://www.gnome-db.org">GNOME-DB</a> team
<br>Jorge Ferrer
<br>All those who contribute or have contributed in one or another way to the CVSAnalY project
<br>All those Libre Software developers who make Libre Software possible
');

?>
