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
// $Id: Generations.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table, $db;

if ($HTTP_GET_VARS['module'] && $HTTP_GET_VARS['graph']) {
	$module_orig = $HTTP_GET_VARS['module'];
	$graph = $HTTP_GET_VARS['graph'];
	$module = lib_dbModuleName($module_orig);

	if ($graph != 'heat') {
	    $percentage = $HTTP_GET_VARS['percentage'];
	    if (!$percentage) { $percentage = '22'; }

	    $table->table_strip('Core team evolution for '.html_link($module_orig, 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig)), 'center'); 

	    print '<center>'.html_link(html_image('gnuplot/generations/'.$module.'_log_'.$graph.'_'.$percentage.'.png', $graph.' in time for '.$module_orig, '620', '465'), 'gnuplot/generations/'.$module.'_log_'.$graph.'_'.$percentage.'.png', array()).'</center>'."\n";
	    print '<p><center>(Click on the image to see it full-size)</center>'."\n";

	    print '<center>'.html_link(html_image('gnuplot/generations/'.$module.'_log-per_'.$graph.'_'.$percentage.'.png', $graph.' in time for '.$module_orig, '620', '465'), 'gnuplot/generations/'.$module.'_log-per_'.$graph.'_'.$percentage.'.png', array()).'</center>'."\n";
	    print '<p><center>(Click on the image to see it full-size)</center>'."\n";

	    print '<center>'.html_link(html_image('gnuplot/generations/'.$module.'_log-sum_'.$graph.'_'.$percentage.'.png', $graph.' in time for '.$module_orig, '620', '465'), 'gnuplot/generations/'.$module.'_log-sum_'.$graph.'_'.$percentage.'.png', array()).'</center>'."\n";
  	    print '<p><center>(Click on the image to see it full-size)</center>'."\n";
	} else {      
	    $table->table_strip('Heat map for for '.html_link($module_orig, 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig)), 'center'); 


	    $db->query("SELECT COUNT(DISTINCT(commiter_id)) AS count FROM ".$module ."_log");
	    $db->next_record();

	    $number = ceil($db->f('count')/25);

	    print "<center><table bgcolor=black width=60%><tr><td>";
	    for ($i=1;$i<$number+1;$i++) {
	        print '<center>'.html_link(html_image('gnuplot/heatmaps/'.$module_orig.'___'.$i.'.png', 'Heat map for '.$module_orig), 'gnuplot/heatmaps/'.$module_orig.'___1.png', array()).'</center>'."\n";
	    }
	    print "</td></tr></table></center>";
	}

} else {
    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Evolution in time of several parameters for Modules &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    print "<center>Ordered by "
          .html_link('name', 'PHP_SELF', array('menu' => 'Generations'))." | "
          .html_link('commiters', 'PHP_SELF', array('menu' => 'Generations', 'order' => 'commiters'))." | "
          .html_link('commits', 'PHP_SELF', array('menu' => 'Generations', 'order' => 'commits'))." | "
          .html_link('files', 'PHP_SELF', array('menu' => 'Generations', 'order' => 'files'))." | "
          .html_link('lines added', 'PHP_SELF', array('menu' => 'Generations', 'order' => 'plus'))." | "
          .html_link('lines removed', 'PHP_SELF', array('menu' => 'Generations', 'order' => 'minus'))."</center>";

    if (!$HTTP_GET_VARS['order']) {
        $order = '';
    } else {
        $order = "ORDER BY ".$HTTP_GET_VARS['order']." DESC";
    }

    $db->query("SELECT * FROM cvsanal_temp_modules ".$order);
    if($db->num_rows() > 0) {
        $table->table_begin('This table contains FIXME');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>#</b>', '4%', $bgcolor);
        $table->table_column('<b>Name</b>', '24%', $bgcolor);
        $table->table_column('<b>5 time slots</b>', '18%', $bgcolor);
        $table->table_column('<b>10 time slots</b>', '18%', $bgcolor);
        $table->table_column('<b>20 time slots</b>', '18%', $bgcolor);
        $table->table_column('<b>Heat map</b>', '18%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();

        /* Body */

        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
        while($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 
            $table->table_column($i.'.', '4%', $bgcolor);
	    $table->table_column(html_link($db->f('module'), 'PHP_SELF', array('menu' => 'Modules', 'module' => $db->f('module'))), '24%', $bgcolor);
            $table->table_column(html_link('Core team evolution', 'PHP_SELF', array('menu' => 'Generations', 'module' => $db->f('module'), 'graph' => '5')), '18%', $bgcolor);
            $table->table_column(html_link('Core team evolution', 'PHP_SELF', array('menu' => 'Generations', 'module' => $db->f('module'), 'graph' => '10')), '18%', $bgcolor);
            $table->table_column(html_link('Core team evolution', 'PHP_SELF', array('menu' => 'Generations', 'module' => $db->f('module'), 'graph' => '20')), '18%', $bgcolor);
            $table->table_column(html_link('Heat map', 'PHP_SELF', array('menu' => 'Generations', 'module' => $db->f('module'), 'graph' => 'heat')), '18%', $bgcolor);

            $table->table_nextRowWithColumns();
            $i++;
        }
        $table->table_column('<b>&nbsp;</b>', '4%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '24%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '18%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '18%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '18%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '18%', $bgcolor);

        $table->table_columns_end();
        $table->table_body_end();
        $table->table_end();
    }
}

?>
