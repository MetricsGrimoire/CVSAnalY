<?php

//If install_lock file exists then we go to the installer wizard.
if (file_exists("install_lock"))
{
	include("installer/installer.html");
	exit;
}
//In other case we execute next code.



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
// $Id: index.php,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

include('include/start.inc');
navigation_page($HTTP_GET_VARS['menu'], $HTTP_GET_VARS[$menu]);
include('include/end.inc');

?>
