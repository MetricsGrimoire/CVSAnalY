<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |                                                                      |
// +----------------------------------------------------------------------+
// |       Copyright (c) 2002 Gregorio Robles.  All rights reserved       |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors: Gregorio Robles <grex@scouts-es.org>                        |
// +----------------------------------------------------------------------+
//
// $Id: Modules.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $


global $table, $db, $db2;

if ($HTTP_GET_VARS['module'] && !isset($HTTP_GET_VARS['filetype'])) {

    $module_orig = $HTTP_GET_VARS['module'];
    $module = lib_dbModuleName($module_orig);

    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<b>Module '.$module_orig.'</b> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    lib_module_summary($module_orig);
    lib_module_filetype_summary($module_orig, $HTTP_GET_VARS['type_order']);
    lib_commiter_summary($module_orig, $HTTP_GET_VARS['order']);
    lib_show_graphs ($module_orig);
    

} elseif (isset($HTTP_GET_VARS['filetype'])) {
    $fileType = $HTTP_GET_VARS['filetype'];
    $module_orig = $HTTP_GET_VARS['module'];

    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <b>'.$fileType.' files in '.$module_orig.'</b> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    lib_module_summary($module_orig);
    $module = lib_dbModuleName($module_orig);
    lib_module_filetype_summary($module_orig, $HTTP_GET_VARS['type_order']);
    //    lib_commiter_summary($module_orig, $HTTP_GET_VARS['order'], $fileType);
    //    lib_show_graphs($module_orig, $fileType);

    htmlp_anchor('fileType');

    if (!$HTTP_GET_VARS['order']) {
        $order = 'sum';
    } else {
        $order = $HTTP_GET_VARS['order'];
    }

/*
    $db->query("SELECT file, 
                   COUNT(file) AS sum, 
		   SUM(plus) AS sum_plus, 
		   SUM(minus) AS sum_minus, 
		   COUNT(DISTINCT(commiter_id)) AS sum_commiters, 
		   MIN(date) AS first, 
		   MAX(date) AS last 
		FROM log, cvsanal_fileTypes  
		WHERE cvsanal_fileTypes.fileType_id=log.fileType_id 
		   AND cvsanal_fileTypes.fileType_id='".$fileType."' 
		   AND cvsanal_fileTypes.fileType_id=log.filetype_id 
		GROUP BY file 
		ORDER BY $order DESC");
*/

   $db->query("SELECT files.name,
                  COUNT(log.file_id) AS sum,
                  SUM(log.plus) AS sum_plus,
                  SUM(log.minus) AS sum_minus,
                  COUNT(DISTINCT(log.commiter_id)) AS sum_commiters,
                  MIN(log.date_log) AS first,
                  MAX(log.date_log) AS last
               FROM log, 
	            cvsanal_fileTypes,
		    files
	       WHERE cvsanal_fileTypes.fileType_id=log.filetype
	             AND cvsanal_fileTypes.filetype='".$fileType."'
		     AND files.file_id = log.file_id
	       GROUP BY files.name
	       ORDER BY $order DESC");
																											   

    if($db->num_rows() > 0) {
      print "<center>Ordered by "
	.html_link('name', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'file'))." | "
	.html_link('commiters', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'sum_commiters'))." | "
	.html_link('commits', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'sum'))." | "
	.html_link('lines added', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'sum_plus'))." | "
	.html_link('lines removed', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'sum_minus'))." | "
	.html_link('first commit', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'first'))." | "
	.html_link('last commit', 'PHP_SELF', array('menu' => 'Modules', 'files' => $module_orig, 'order' => 'last'))."</center>";

        $table->table_begin('This table contains FIXME');
	$table->table_title('Files of the selected file type for module: '.html_link($module, 'PHP_SELF', array('menu' => 'Modules', 'module' => $module)));
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>Rank</b>', '4%', $bgcolor);
        $table->table_column('<b>Filename</b>', '26%', $bgcolor);
        $table->table_column('<b>Commits</b>', '10%', $bgcolor);
        $table->table_column('<b>Commiters</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Changed</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Added</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Removed</b>', '10%', $bgcolor);
        $table->table_column('<b>First Commit</b>', '10%', $bgcolor);
        $table->table_column('<b>Last Commit</b>', '10%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();

        /* Body */

        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
        $total_sum = 0;
        $total_commiters = 0;
        $total_plus = 0;
        $total_minus = 0;
        while($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 
            $table->table_column($i.'.', '4%', $bgcolor);
            $table->table_column($db->f('file'), '26%', $bgcolor);
            $table->table_column($db->f('sum'), '10%', $bgcolor);
	    $total_sum += $db->f('sum');
            $table->table_column($db->f('sum_commiters'), '10%', $bgcolor);
            $total_commiters += $db->f('sum_commiters');
            $table->table_column($db->f('sum_plus')+$db->f('sum_minus'), '10%', $bgcolor);
            $table->table_column($db->f('sum_plus'), '10%', $bgcolor);
            $total_plus += $db->f('sum_plus');
            $table->table_column($db->f('sum_minus'), '10%', $bgcolor);
            $total_minus += $db->f('sum_minus');
            $table->table_column(substr($db->f('first'),0,10), '10%', $bgcolor);
            $table->table_column(substr($db->f('last'),0,10), '10%', $bgcolor);
            $table->table_nextRowWithColumns();
            $i++;
        }
	$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
        $table->table_column('<b>&nbsp;</b>', '4%', $bgcolor);
        $table->table_column('<b>Total</b>', '26%', $bgcolor);
        $table->table_column('<b>'.$total_sum.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_commiters.'</b>', '10%', $bgcolor);
	$total_changes = $total_plus+$total_minus;
        $table->table_column('<b>'.$total_changes.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_plus.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_minus.'</b>', '10%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '10%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '10%', $bgcolor);

        $table->table_columns_end();
        $table->table_body_end();
        $table->table_end();
    }

} else {
    $table->table_strip('&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;Modules &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;', 'center');

    print "<center>Ordered by "
          .html_link('name', 'PHP_SELF', array('menu' => 'Modules'))." | "
          .html_link('commits', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'commits'))." | "
          .html_link('files', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'files'))." | "
          .html_link('lines added', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'plus'))." | "
          .html_link('lines removed', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'minus'))." | "
          .html_link('first commit', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'first_commit'))." | "
          .html_link('last commit', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'last_commit'))."</center>";

    if (!$HTTP_GET_VARS['order']) {
        $order = '';
    } else {
        $order = "ORDER BY ".$HTTP_GET_VARS['order']." DESC";
    }

    $db->query("SELECT module, 
                       SUM(commits) AS commits, 
		       SUM(files) AS files, 
		       SUM(plus) as plus, 
		       SUM(minus) AS minus, 
		       MIN(first_commit) AS first_commit, 
		       MAX(last_commit) AS last_commit 
		FROM cvsanal_temp_modules 
		GROUP BY module_id ".$order);
		
    if($db->num_rows() > 0) {
        $table->table_begin('This table contains FIXME');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>#</b>', '3%', $bgcolor);
        $table->table_column('<b>Name</b>', '19%', $bgcolor);
        $table->table_column('<b>Commiters</b>', '10%', $bgcolor);
        $table->table_column('<b>Commits</b>', '10%', $bgcolor);
        $table->table_column('<b>Files</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Changed</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Added</b>', '10%', $bgcolor);
        $table->table_column('<b>Lines Removed</b>', '10%', $bgcolor);
        $table->table_column('<b>First commit</b>', '9%', $bgcolor);
        $table->table_column('<b>Last commit</b>', '9%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();

        /* Body */

        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
	$total_commiters = 0;
        $total_commits = 0;
        $total_files = 0;
        $total_plus = 0;
        $total_minus = 0;
        while($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 

	    //Replaced by next line.
            $db2->query("SELECT COUNT(cm.commiter_id) AS commiters 
	                 FROM modules m,
			      commiters_module cm
			 WHERE cm.module_id = m.module_id
			       AND m.module = '".$db->f('module')."'");

	    //$db2->query("SELECT COUNT(*) AS commiters FROM ".lib_dbModuleName($db->f('module'))."_commiters");
	    $db2->next_record();

            $table->table_column($i.'.', '3%', $bgcolor);
	    $table->table_column(html_link($db->f('module'), 'PHP_SELF', array('menu' => 'Modules', 'module' => $db->f('module'))), '19%', $bgcolor);
            $table->table_column($db2->f('commiters'), '10%', $bgcolor);
	    $total_commiters += $db2->f('commiters');
	    $table->table_column($db->f('commits'), '10%', $bgcolor);
	    $total_commits += $db->f('commits');
            $table->table_column($db->f('files'), '10%', $bgcolor);
            $total_files += $db->f('files');
            $table->table_column($db->f('plus')+$db->f('minus'), '10%', $bgcolor);
            $table->table_column($db->f('plus'), '10%', $bgcolor);
            $total_plus += $db->f('plus');
            $table->table_column($db->f('minus'), '10%', $bgcolor);
            $total_minus += $db->f('minus');
            $table->table_column(substr($db->f('first_commit'),0,10), '9%', $bgcolor);
            $table->table_column(substr($db->f('last_commit'),0,10), '9%', $bgcolor);
            $table->table_nextRowWithColumns();
            $i++;
        }
	$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
        $table->table_column('<b>&nbsp;</b>', '3%', $bgcolor);
        $table->table_column('<b>Total</b>', '19%', $bgcolor);
        $table->table_column('<b>('.$total_commiters.')</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_commits.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_files.'</b>', '10%', $bgcolor);
        $total_changes = $total_plus+$total_minus;
        $table->table_column('<b>'.$total_changes.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_plus.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_minus.'</b>', '10%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '9%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '9%', $bgcolor);

        $table->table_columns_end();
        $table->table_body_end();
        $table->table_end();
    }
}
?>

 
