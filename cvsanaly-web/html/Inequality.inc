<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |                                                                      |
// +----------------------------------------------------------------------+
// |      Copyright (c) 2002-3 Gregorio Robles.  All rights reserved      |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors: Gregorio Robles <grex@scouts-es.org>                        |
// +----------------------------------------------------------------------+
//
// $Id: Inequality.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table, $db;

if ($HTTP_GET_VARS['module']) {
    $module_orig = $HTTP_GET_VARS['module'];
    $module = lib_dbModuleName($module_orig);

    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<b>Module '.$module_orig.'</b> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    $db->query("SELECT module, SUM(commits) AS commits, SUM(files) AS files, SUM(plus) AS plus, SUM(minus) AS minus, MIN(first_commit) AS first_commit, MAX(last_commit) AS last_commit FROM cvsanal_temp_modules WHERE module='".$module_orig."' GROUP BY module");    
    if($db->num_rows() > 0) {
        $table->table_begin('This table contains FIXME');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>Name</b>', '20%', $bgcolor);
        $table->table_column('<b>Commiters</b>', '10%', $bgcolor);
        $table->table_column('<b>Commits</b>', '10%', $bgcolor);
        $table->table_column('<b>Files</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Changed</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Added</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Removed</b>', '10%', $bgcolor);
        $table->table_column('<b>First commit</b>', '10%', $bgcolor);
        $table->table_column('<b>Last commit</b>', '10%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();
        /* Body */
        $table->table_body_begin('top');
        $table->table_columns_begin();
	$db->next_record();
	$table->table_column("<b>".$db->f('module')."</b>", '19%', $bgcolor);
        $table->table_column($db->f('commiters'), '10%', $bgcolor);
        $table->table_column($db->f('commits'), '10%', $bgcolor);
        $table->table_column(html_link($db->f('files'), 'PHP_SELF', array('menu' => 'Modules', 'files' => $db->f('module'), 'order' => 'sum')), '10%', $bgcolor);
        $table->table_column($db->f('plus')+$db->f('minus'), '10%', $bgcolor);
        $table->table_column($db->f('plus'), '10%', $bgcolor);
        $table->table_column($db->f('minus'), '10%', $bgcolor);
        $table->table_column(substr($db->f('first_commit'),0,10), '9%', $bgcolor);
        $table->table_column(substr($db->f('last_commit'),0,10), '9%', $bgcolor);
        $table->table_columns_end();
	/* Body ends */
        $table->table_body_end();
        $table->table_end();
    }

    $array = array(commiters, commits);
    foreach ($array as $graph) {
        $table->table_begin('This table contains the '.$commiters.'-in-time-graph');
        $table->table_title('Evolution of '.$graph.' in time');
        $table->table_body('<center>'.html_link(html_image('gnuplot/evolution/'.$graph.'_in_time_for_'.$module_orig.'.png', $graph.' in time for '.$module_orig, '620', '465'), 'gnuplot/evolution/'.$graph.'_in_time_for_'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
        $table->table_end();
    }

    $table->table_begin('This table contains Lorenz curve');
    $table->table_title('Lorenz curve (Gini coefficient)');
    $table->table_body('<center>'.html_link(html_image('gnuplot/gini/'.$module_orig.'.png', 'Lorenz curve for '.$module_orig, '620', '465'), 'gnuplot/gini/'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();


    $array = array(atkinson, theil, reserve, d_and_r, kullback_liebler, hoover, coulter, herfindahl);
    foreach ($array as $graph) {
        $table->table_begin('This table contains the '.$commiters.'-in-time-graph');
        $table->table_title('Evolution of '.$graph.' in time');
        $table->table_body('<center>'.html_link(html_image('gnuplot/inequality/'.$module_orig.'-'.$graph.'.png', $graph.' in time for '.$module_orig, '620', '465'), 'gnuplot/inequality/'.$module_orig.'-'.$graph.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
        $table->table_end();
    }

} else {
    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<b>Inequality coefficients and redundancies for all modules</b> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    print "<center>Ordered by "
          .html_link('name', 'PHP_SELF', array('menu' => 'Inequality'))." | "
          .html_link('commiters', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'commiters'))." | "
          .html_link('commits', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'commits'))." | "
          .html_link('Gini', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'gini'))." | "
          .html_link('Concentration', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'concentration'))." | "
          .html_link('EU', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'eu'))." | "
          .html_link('Atkinson', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'atkinson'))." | "
          .html_link('Theil', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'theil'))." | "
          .html_link('Reserve', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'reserve'))." | "
          .html_link('D&amp;R', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'd_and_r'))." | "
          .html_link('Kullback-Liebler', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'kullback_liebler'))." | "
          .html_link('Hoover', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'hoover'))." | "
          .html_link('Coulter', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'coulter'))." | "
          .html_link('Herfindahl', 'PHP_SELF', array('menu' => 'Inequality', 'order' => 'herfindahl'))."</center>";

    if (!$HTTP_GET_VARS['order']) {
        $order = '';
    } else {
        $order = "ORDER BY ".$HTTP_GET_VARS['order']." DESC";
    }

    $db->query("SELECT * FROM cvsanal_temp_inequality, cvsanal_temp_modules WHERE cvsanal_temp_inequality.module_id=cvsanal_temp_modules.module_id ".$order." GROUP by cvsanal_temp_modules.module_id");
    if($db->num_rows() > 0) {
        $table->table_begin('This table contains FIXME');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>#</b>', '3%', $bgcolor);
        $table->table_column('<b>Name</b>', '16%', $bgcolor);
        $table->table_column('<b>Commiters</b><br><b>Commits</b>', '9%', $bgcolor);
        $table->table_column('<b>Gini</b><br><b>Concentration</b>', '9%', $bgcolor);
        $table->table_column('<b>EU</b>', '9%', $bgcolor);
        $table->table_column('<b>Atkinson</b><br><b>Theil</b>', '9%', $bgcolor);
        $table->table_column('<b>Reserve</b>', '9%', $bgcolor);
        $table->table_column('<b>D&R</b><br><b>Kullback-Lieber</b>', '9%', $bgcolor);
        $table->table_column('<b>Hoover</b>', '9%', $bgcolor);
        $table->table_column('<b>Coulter</b>', '9%', $bgcolor);
        $table->table_column('<b>Herfindahl</b>', '9%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();

        /* Body */

        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
	$total_commiters = 0;
        $total_commits = 0;
	$total_gini = 0;
	$total_concentration = 0;
	$total_eu = 0;
	$total_atkinson = 0;
	$total_theil = 0;
	$total_reserve = 0;
	$total_d_and_r = 0;
	$total_kullback_liebler = 0;
	$total_hoover = 0;
	$total_coulter = 0;
	$total_herfindahl = 0;
        while($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 
            $table->table_column($i.'.', '3%', $bgcolor);
	    $table->table_column(html_link($db->f('module'), 'PHP_SELF', array('menu' => 'Inequality', 'module' => $db->f('module'))), '16%', $bgcolor);
            $table->table_column($db->f('commiters').'<br>'.$db->f('commits'), '9%', $bgcolor);
	    $total_commiters += $db->f('commiters');
	    $total_commits += $db->f('commits');
	    $table->table_column(round($db->f('gini'),2).'<br>'.round($db->f('concentration'),2), '9%', $bgcolor);
	    $total_gini += $db->f('gini');
	    $total_concentration += $db->f('concentration');
	    $table->table_column(round($db->f('eu'),2), '9%', $bgcolor);
	    $total_eu += $db->f('eu');
	    $table->table_column(round($db->f('atkinson'),2).'<br>'.round($db->f('theil'),2), '9%', $bgcolor);
	    $total_atkinson += $db->f('atkinson');
	    $total_theil += $db->f('theil');
	    $table->table_column(round($db->f('reserve'),2), '9%', $bgcolor);
	    $total_reserve += $db->f('reserve');
	    $table->table_column(round($db->f('d_and_r'),2).'<br>'.round($db->f('kullback_liebler'),2), '9%', $bgcolor);
	    $total_d_and_r += $db->f('d_and_r');
	    $total_kullback_liebler += $db->f('kullback_liebler');
	    $table->table_column(round($db->f('hoover'),2), '9%', $bgcolor);
	    $total_hoover += $db->f('hoover');
	    $table->table_column(round($db->f('coulter'),2), '9%', $bgcolor);
	    $total_coulter += $db->f('coulter');
	    $table->table_column($db->f('herfindahl'), '9%', $bgcolor);
	    $total_herfindahl += $db->f('herfindahl');

            $table->table_nextRowWithColumns();
            $i++;
        }

	$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
        $table->table_column('<b>&nbsp;</b>', '3%', $bgcolor);
        $table->table_column('<b>Total</b>', '16%', $bgcolor);
        $table->table_column('<b>'.$total_commiters.'</b><br><b>'.$total_commits.'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_gini,2).'</b><br><b>'.round($total_concentration,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_eu,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_atkinson,2).'</b><br><b>'.round($total_theil,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_reserve,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_d_and_r,2).'</b><br><b>'.round($total_kullback_liebler,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_hoover,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_coulter,2).'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.round($total_herfindahl,2).'</b>', '9%', $bgcolor);
        $table->table_columns_end();
        $table->table_body_end();
        $table->table_end();
    }
}
?>
