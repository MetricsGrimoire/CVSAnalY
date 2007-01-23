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
// |          Lutz Henckel <lutz.henckel@fokus.fhg.de>                    |
// |          Carlos Martin Ugalde <carlos@scouts-es.org>                 |
// +----------------------------------------------------------------------+
//
// $Id: config.inc.php,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * General System Configuration
 *
 * This file contains all the constants with the general system
 * parameters, basically tied to visualization (colors, fonts, etc.)
 */

/**
 * System
 *
 * config_sys_name  string      Name of your system
 * config_sys_title string      Title of the page
 * config_sys_url   string 	URL of your system
 * config_sys_credits string    Name of the persons/organization who are behind this site
 */

$_INC_PATH = './include/';
$config_sys_name = 'CVS Analysis';
$config_sys_title = 'CVS Analisys';
$config_sys_url = 'http://localhost';
$config_sys_credits = 'GSyC/Libresoft (Universidad Rey Juan Carlos)';

/*
 * Database
 */

if (!class_exists('DB')) {
	if (!class_exists('DB_Sql')){
		require 'db_mysql.inc';
	}
	class DB extends DB_Sql {
	var $Host     = "localhost";
	var $Database = "cvsanaly";
	var $User     = "root";
	var $Password = "";
	}

}

/**
 * Colors
 */

$config_color_dark = '#3177c5'; 
$config_color_clear = '#96a2ff';
$config_color_line = '#19568c';
$config_navstrip_bgcolor = 'grey';
$config_navstrip_font_color = 'white';

/**
 * Header image
 *
 * config_sys_logo_image   string  Image of your System (should be in the images directory)
 * config_sys_url_image    string  URL the image of your system points to
 * config_sys_logo_alt	   string  Alternative text for your site's image
 * config_sys_logo_width   int     Width of the image of your site
 * config_sys_logo_heigth  int     Height of the image of your site
 */

$config_sys_logo_image = $config_path_images.'infonomics.png';
$config_sys_url_image = 'http://curso-sobre.berlios.de';
$config_sys_logo_alt = 'Universidad Rey Juan Carlos, Madrid, Spain';
$config_sys_logo_width = 350;
$config_sys_logo_heigth = 70;

/**
 * Organisation Config
 * (this can be sometimes the same as the one of the system)
 *
 * org_name	    string    Name of your Organisation
 * org_url	    string    URL of your Organisation
 * org_logo_image   string    Image of your Organisation
 * org_logo_alt	    string    Alternative text for the image of your Organisation
 * org_logo_width   int       Width of the image of your Organisation
 * org_logo_heigth  int       Height of the image of your Organisation
 */

$config_org_name = '';
$config_org_url = '';
$config_org_logo_image = $config_path_images.'';
$config_org_logo_alt = $org_name;
$config_org_logo_width = 63;
$config_org_logo_heigth = 60;


/**
 * HTML Metainformation
 * 
 *
 *
 */

$config_meta_description = 'meta description';
$config_meta_keywords = 'Free Software, Open Source, cvs, developers, CODD, statistics, research, software engineering';
# 16x16 pixels favicon
$config_shortcut_icon = 'images/favicon.ico';

/**
 * Main menu (at the left hand side of the pages)
 */

$config_menu[] = "Index";
$config_menu[] = "About";
$config_menu[] = "Statistics";
$config_menu[] = "Modules";
$config_menu[] = "Commiters";
//$config_menu[] = "Graphs";
$config_menu[] = "Inequality";
//$config_menu[] = "Comments";
//$config_menu[] = "Generations";
$config_menu[] = "FAQ";
$config_menu[] = "Credits";

/**
 * Array with the file types
 * (should better not be touched unless you know what you do)!!!
 **/

$config_file_types_array = array(documentation, images, translation, ui, multimedia, code, build, develDoc, unknown);

/**
 * Secondary menu
 */

#$config_menu_Graphs[] = "General";

/**
 * Languages
 * 
 *  List of languages supported by your website
 * You can add/delete/modify as long as you mantain the syntax
 * New languages are always wellcome. Contact with the authors!
 */

// WISH: this should obtain the list of languages from the *-lang.inc
// WISH: files in the include directory. But this might be too expensive
// WISH: since this file is read in for each page .... further: it might
// WISH: be possible to do this and store the results in an environmental
// WISH: variable, ofcourse updating the variable once set would be a problem

$config_la_array[] = 'English';
$config_la_array[] = 'Deutsch';
$config_la_array[] = 'Español';

/**
 * Configurable properties for general and error table
 *											     
 * Controls the table padding. It should have units (pt/em/%..)
 * Background color for the strip that contains the title
 * Background color for the box that contains the dta
 * Text align for the title (left/right/justify)
 * Text align for the content
 * Text color for the title
 * Text color for the content
 */

/* General table */

$config_table_general_filling = '3pt';
$config_table_general_title_bgcolor = '#DDDDDD';
$config_table_general_body_bgcolor = 'white';
$config_table_general_title_align = 'left';
$config_table_general_body_align = 'left';
$config_table_general_title_font_color = '#000000';
$config_table_general_body_font_color = '#333333';

/* Error Table */

$config_table_error_filling = '3pt';
$config_table_error_title_bgcolor = '#CCCCCC';
$config_table_error_body_bgcolor = '#FFFFFF';
$config_table_error_title_align = 'left';
$config_table_error_body_align = 'left';
$config_table_error_title_font_color = '#000000';
$config_table_error_body_font_color = '#FF2020';

/**
 * Width of the columns shown in the Field, Show, etc. classes
 *
 * Note that both values should sum up 100%
 */

$config_LeftColumnWidth = '33%';
$config_RightColumnWidth = '67%';


/**
 * Settings for Comments database.
 *

$Comments_Database = 'cvsanaly_gaim';
$Comments_Table    = 'comments';
$Comments_Host     = 'localhost';
$Comments_User     = 'operator';
$Comments_Password = 'operator';

 */
			      

/**
 * 
 *  Path of cvsanaly graphs
 *
 */

$Cvsanaly_Graphs = 'config_mainDirectory + /graphs/';
 
 
?>
