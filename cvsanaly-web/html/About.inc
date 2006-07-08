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
// $Id: About.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table;

$table->table_full('About '.$GLOBALS['config_sys_name'].' and other projects', '');

print '<p>';


$table->table_full('About CVSAnalY', 'CVSAnalY is a tool that extracts statistical information out of CVS logs and transforms it in either information exchange XML and database SQL formats. It has a web interface where the results can be retrieved and analized in an easy way. You can have more information at the <a href="http://barba.dat.escet.urjc.es/index.php?menu=Tools&Tools=CVSAnalY">CVSAnalY homepage</a>.');

$table->table_full('About Libre Software Engineering', 'Libre Software offers Software Engineering scientists the possibility not only of having a closer look at the product that is being created, but also of studying in detail the whole development process and its technical, social and economic consequences. The <a href="http://barba.dat.escet.urjc.es/">Libre Software Engineering</a> project site at GSyC has plenty of information on this topic.');


$table->table_full('About other Libre Software analysis tools', 'There exist several tools that we use to extract information about the Libre Software development process. These tools are usually Libre Software themselves so that you can download them for free from the Internet, and enhance or modify them to suit your needs. See an <a href="http://barba.dat.escet.urjc.es/index.php?menu=Tools">uncomplete list</a> of such libre software analysis tools.');

?>
