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
// | Authors: Gregorio Robles <grex@scouts-es.org>                        |
// |          Lutz Henckel <lutz.henckel@fokus.fhg.de>                    |
// |          Carlos Martin Ugalde <carlos@scouts-es.org>                 |
// +----------------------------------------------------------------------+
//
// $Id: start.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

// Disabling cache
header('Cache-Control: no-cache, must-revalidate');     // HTTP/1.1
header('Pragma: no-cache'); 				// HTTP/1.0

require('include/db_mysql.inc');
require('include/config.inc.php');


include($_INC_PATH.'lib.inc');
include($_INC_PATH.'html.inc');
include($_INC_PATH.'Table.inc');
include($_INC_PATH.'navigation.inc');

//setlocale('LC_TIME', 'es_ES');
//config_inc('Lang');
//config_inc('Translation');
//$t = new Translation($la);

$db = new DB;
$db2 = new DB;

$table = new Table();
$table_error = new Table('error', '80%');

include($_INC_PATH.'header.inc');
?>
