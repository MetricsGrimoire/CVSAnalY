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
// $Id: Graphs.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table, $db;

if ($HTTP_GET_VARS['module'] && $HTTP_GET_VARS['graph']) {
	$module = $HTTP_GET_VARS['module'];
	$graph = $HTTP_GET_VARS['graph'];

	$table->table_strip($graph.' in time for '.html_link($module, 'PHP_SELF', array('menu' => 'Modules', 'module' => $module)), 'center'); 

	if ($graph != "lorenz") {
	    print '<center>'.html_link(html_image('gnuplot/evolution/'.$graph.'_in_time_for_'.$module.'.png', $graph.' in time for '.$module, '620', '465'), 'gnuplot/evolution/'.$graph.'_in_time_for_'.$module.'.png', array()).'</center>'."\n";
	} else {
	    print '<center>'.html_link(html_image('gnuplot/gini/'.$module.'.png', 'Lorenz curve for '.$module, '620', '465'), 'gnuplot/gini/'.$module.'.png', array()).'</center>'."\n";
	}

	print '<center>(Click on the image to see it full-size)</center>'."\n";

} else {
    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Evolution in time of several parameters for Modules &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    print "<center>Ordered by "
          .html_link('name', 'PHP_SELF', array('menu' => 'Graphs'))." | "
          .html_link('commiters', 'PHP_SELF', array('menu' => 'Graphs', 'order' => 'commiters'))." | "
          .html_link('commits', 'PHP_SELF', array('menu' => 'Graphs', 'order' => 'commits'))." | "
          .html_link('files', 'PHP_SELF', array('menu' => 'Graphs', 'order' => 'files'))." | "
          .html_link('lines added', 'PHP_SELF', array('menu' => 'Graphs', 'order' => 'plus'))." | "
          .html_link('lines removed', 'PHP_SELF', array('menu' => 'Graphs', 'order' => 'minus'))."</center>";

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
        $table->table_column('<b>Name</b>', '26%', $bgcolor);
        $table->table_column('<b>Commiters</b>', '14%', $bgcolor);
        $table->table_column('<b>Commits</b>', '14%', $bgcolor);
        $table->table_column('<b>Files</b>', '14%', $bgcolor);
        $table->table_column('<b>Lines of Code</b>', '14%', $bgcolor);
        $table->table_column('<b>Lorenz curve</b>', '14%', $bgcolor);
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
	    $table->table_column(html_link($db->f('module'), 'PHP_SELF', array('menu' => 'Modules', 'module' => $db->f('module'))), '26%', $bgcolor);
            $table->table_column(html_link('commiters(t)', 'PHP_SELF', array('menu' => 'Graphs', 'module' => $db->f('module'), 'graph' => 'commiters')), '14%', $bgcolor);
            $table->table_column(html_link('commits(t)', 'PHP_SELF', array('menu' => 'Graphs', 'module' => $db->f('module'), 'graph' => 'commits')), '14%', $bgcolor);
            $table->table_column(html_link('files(t)', 'PHP_SELF', array('menu' => 'Graphs', 'module' => $db->f('module'), 'graph' => 'files')), '14%', $bgcolor);
            $table->table_column(html_link('LOCs(t)', 'PHP_SELF', array('menu' => 'Graphs', 'module' => $db->f('module'), 'graph' => 'LOCs')), '14%', $bgcolor);            $table->table_column(html_link('Lorenz', 'PHP_SELF', array('menu' => 'Graphs', 'module' => $db->f('module'), 'graph' => 'lorenz')), '14%', $bgcolor);

            $table->table_nextRowWithColumns();
            $i++;
        }
        $table->table_column('<b>&nbsp;</b>', '4%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '26%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '14%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '14%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '14%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '14%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '14%', $bgcolor);

        $table->table_columns_end();
        $table->table_body_end();
        $table->table_end();
    }
}

?>
