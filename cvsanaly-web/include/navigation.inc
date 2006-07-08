<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |                   Libre Software Engineering                         |
// +----------------------------------------------------------------------+
// |                   http://gsyc.escet.urjc.es/                         |
// +----------------------------------------------------------------------+
// |             Copyright (c) 2003 Universidad Rey Juan Carlos           |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors:                                                             |
// |          Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
// +----------------------------------------------------------------------+
//
// $Id: navigation.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * Site navigation bar
 */

/**
 * Generates the left hand side navigation bar dinamically
 *
 * @var  $main         string		Main navigation item
 * @var  $secondary    string		Secondarty navigation item
 * @access  public
 */

function navigation_bar ($main = '', $secondary = '')
{
    while (list(, $array_value) = each($GLOBALS['config_menu'])) {
        if ($array_value == $main || ($array_value == 'Index' && $main == '') ) {
#	    if (!isset($secondary) || empty($secondary)) {
#   	        print "      <tr><td class=\"menu\">$array_value\n";
#            } else {
    	        print "      <tr><td class=\"menu\"><a href=\"index.php?menu=$array_value\">$array_value</a>\n";
#            }
	    if (is_array($GLOBALS['config_menu_'.$array_value])) {
                while (list(, $array2_value) = each($GLOBALS['config_menu_'.$array_value])) {
 	            if ($array2_value != $secondary) {
 	                print "          <br>&nbsp; &nbsp; <a href=\"index.php?menu=$array_value&amp;$array_value=$array2_value\">$array2_value</a>\n";
		    } else {
 	                print "          <br>&nbsp; &nbsp; $array2_value\n";
                    }
	        }
            }
	    print "      </td></tr>\n";
        } else {
  	    print "      <tr><td class=\"menu\"><a href=\"index.php?menu=$array_value\">$array_value</a></td></tr>\n";
        }
    }
}

function navigation_page ($main, $secondary)
{
    global $HTTP_GET_VARS;

    /* First, we check if the requested page really exists */
    if ($main && !element_in_array($GLOBALS['config_menu'], $main)) {
        print "Error. There is no reference possible to ".$main.". Please, go back to the Index web page";
    } elseif ($secondary && !element_in_array($GLOBALS['config_menu_'.$main], $secondary)) {
    print "Error. There is no reference possible to ".$secondary.". Please, go back to the Index web page";

    } else {
        /* if it does, let's display it */

    if ($secondary) {
            include("html/".$main."/".$secondary.".inc");
        } elseif ($main) {
            include("html/".$main.".inc");
        } else {
            /* Main page */
            include('html/Index.inc');
        }
    }
}

function element_in_array($array, $element)
{
    while (list(, $array_value) = each($array)) {
        if ($array_value == $element) {
        return 1;
        }
    }
    return 0;
}

?>