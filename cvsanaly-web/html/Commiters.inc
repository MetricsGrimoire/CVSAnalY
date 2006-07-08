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
// $Id: Commiters.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

// FIXME: this is spaghetti unclean code. Maybe some day I'll have some
// time to refactor it! - grex
// There's possibly a design fault in the database structure, that
// makes this statistics horrible to compute :-/

global $table, $db, $db2;

if ($HTTP_GET_VARS['commiter']) {
    $commiter = $HTTP_GET_VARS['commiter'];

    $table->table_strip('<center><b>Commiter: '.$commiter.'</b></center>');


    $table->table_strip('<center><b>Modules '.$commiter.' has commited to</b></center>');

    print '<center><font size="-1">[ Ordered by number of: '
      .html_link('commits', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'order' => 'commits')).' | '
      .html_link('added lines', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'order' => 'plus')).' | '
      .html_link('removed lines', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'order' => 'minus')).' | '
      .html_link('files', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'order' => 'files')).' | '
      .html_link('first commit', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'order' => 'first_commit')).' | '
      .html_link('last commit', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'order' => 'last_commit')).' ]</font></center>';

    if (!$HTTP_GET_VARS['order']) {
        $order = 'commits';
    } else {
        $order = $HTTP_GET_VARS['order'];
    }

    $table->table_begin('This table contains FIXME');
    $table->table_title_begin();
    $table->table_columns_begin();
    $table->table_column('<b>#</b>', '3%', $bgcolor);
    $table->table_column('<b>Module</b>', '27%', $bgcolor);
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

    $i=1;
    $total_commits = 0;
    $total_files = 0;
    $total_plus = 0;
    $total_minus = 0;

    $db->query("SELECT DISTINCT(modules.module) AS module, 
                   SUM(commits) AS commits, 
		   SUM(plus) AS plus, 
		   SUM(minus) AS minus, 
		   SUM(files) AS files, 
		   MIN(first_commit) AS first_commit, 
		   MAX(last_commit) AS last_commit 
	        FROM cvsanal_temp_commiters,
		     modules,
		     commiters
		WHERE cvsanal_temp_commiters.module_id = modules.module_id 
		     AND commiters.commiter ='".$commiter."'
		     AND cvsanal_temp_commiters.commiter_id = commiters.commiter_id		     
		GROUP BY modules.module 
		ORDER BY ".$order." DESC");

    $i = 0;
    while ($db->next_record()) {
        $i++;
        if ($db->num_rows() > 0) {
            if ($i%2) {
                $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 

            $table->table_column($i.'.', '3%', $bgcolor);
            $table->table_column(html_link($db->f('module'), 'PHP_SELF', array('menu' => 'Modules', 'module' => $db->f('module'))), '27%', $bgcolor);
            $table->table_column($db->f('commits'), '10%', $bgcolor);
	    $total_commits += $db->f('commits');
            $table->table_column($db->f('files'), '10%', $bgcolor);
            $total_files += $db->f('files');
            $table->table_column($db->f('plus')+$db->f('minus'), '10%', $bgcolor);
            $table->table_column($db->f('plus'), '10%', $bgcolor);
	    $total_plus += $db->f('plus');
            $table->table_column($db->f('minus'), '10%', $bgcolor);
	    $total_minus += $db->f('minus');
            $table->table_column(substr($db->f('first_commit'),0,10), '10%', $bgcolor);
            $table->table_column(substr($db->f('last_commit'),0,10), '10%', $bgcolor);
            $table->table_nextRowWithColumns();
        }
    }
    $bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
    $table->table_column('<b>&nbsp;</b>', '3%', $bgcolor);
    $table->table_column('<b>Total</b>', '27%', $bgcolor);
    $table->table_column('<b>'.$total_commits.'</b>', '10%', $bgcolor);
    $total_changes = $total_plus+$total_minus;
    $table->table_column('<b>'.$total_files.'</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_changes.'</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_plus.'</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_minus.'</b>', '10%', $bgcolor);
    $table->table_column('<b>&nbsp;</b>', '10%', $bgcolor);
    $table->table_column('<b>&nbsp;</b>', '10%', $bgcolor);

    $table->table_columns_end();
    $table->table_body_end();
    $table->table_end();



    $table->table_strip('<center><b>Summary of the file types '.$commiter.' has commited</b></center>');

    print '<center><font size="-1">[ Ordered by number of: '
      .html_link('commits', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'filetype_order' => 'commits')).' | '
      .html_link('added lines', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'filetype_order' => 'plus')).' | '
      .html_link('removed lines', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'filetype_order' => 'minus')).' | '
      .html_link('files', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'filetype_order' => 'files')).' | '
      .html_link('first commit', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'filetype_order' => 'first_commit')).' | '
      .html_link('last commit', 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $commiter, 'filetype_order' => 'last_commit')).' ]</font></center>';

    if (!$HTTP_GET_VARS['filetype_order']) {
        $filetype_order = 'commits';
    } else {
        $filetype_order = $HTTP_GET_VARS['filetype_order'];
    }

    $table->table_begin('This table contains FIXME');
    $table->table_title_begin();
    $table->table_columns_begin();
    $table->table_column('<b>#</b>', '3%', $bgcolor);
    $table->table_column('<b>File Type</b>', '17%', $bgcolor);
    $table->table_column('<b>Modules</b>', '10%', $bgcolor);
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

    $i=1;
    $total_modules = 0;
    $total_commits = 0;
    $total_files = 0;
    $total_plus = 0;
    $total_minus = 0;
/*
    $db->query("SELECT cvsanal_fileTypes.filetype, 
                   COUNT(DISTINCT(module_id)) AS modules, 
		   SUM(commits) AS commits, 
		   SUM(files) AS files, 
		   SUM(plus) as plus, 
		   SUM(minus) AS minus, 
		   MIN(first_commit) AS first_commit, 
		   MAX(last_commit) AS last_commit 
		FROM cvsanal_temp_commiters, cvsanal_fileTypes 
		WHERE cvsanal_temp_commiters.filetype=cvsanal_fileTypes.fileType_id 
		   AND commiter_id='".$commiter."' group by cvsanal_fileTypes.filetype 
		ORDER BY ".$filetype_order." DESC");
*/
    $db->query("SELECT cvsanal_fileTypes.filetype,
                   COUNT(DISTINCT(module_id)) AS modules,
                   SUM(commits) AS commits,
                   SUM(files) AS files,
                   SUM(plus) as plus,
                   SUM(minus) AS minus,
                   MIN(first_commit) AS first_commit,
                   MAX(last_commit) AS last_commit
                FROM cvsanal_temp_commiters, 
		     cvsanal_fileTypes,
		     commiters
                WHERE cvsanal_temp_commiters.filetype = cvsanal_fileTypes.fileType_id
		      AND commiters.commiter = '".$commiter."'
                      AND commiters.commiter_id = cvsanal_temp_commiters.commiter_id 
		GROUP BY cvsanal_fileTypes.filetype
                ORDER BY ".$filetype_order." DESC");
																							  
    $i = 0;
    while ($db->next_record()) {
        $i++;
        if ($db->num_rows() > 0) {
            if ($i%2) {
                $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 

            $table->table_column($i.'.', '3%', $bgcolor);
            $table->table_column('<b>'.$db->f('filetype').'</b>', '17%', $bgcolor);
            $table->table_column($db->f('modules'), '10%', $bgcolor);
	    $total_modules += $db->f('modules');
            $table->table_column($db->f('commits'), '10%', $bgcolor);
	    $total_commits += $db->f('commits');
            $table->table_column($db->f('files'), '10%', $bgcolor);
            $total_files += $db->f('files');
            $table->table_column($db->f('plus')+$db->f('minus'), '10%', $bgcolor);
            $table->table_column($db->f('plus'), '10%', $bgcolor);
	    $total_plus += $db->f('plus');
            $table->table_column($db->f('minus'), '10%', $bgcolor);
	    $total_minus += $db->f('minus');
            $table->table_column(substr($db->f('first_commit'),0,10), '10%', $bgcolor);
            $table->table_column(substr($db->f('last_commit'),0,10), '10%', $bgcolor);
            $table->table_nextRowWithColumns();
        }
    }
    $bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
    $table->table_column('<b>&nbsp;</b>', '3%', $bgcolor);
    $table->table_column('<b>Total</b>', '17%', $bgcolor);
    $table->table_column('<b>('.$total_modules.')</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_commits.'</b>', '10%', $bgcolor);
    $total_changes = $total_plus+$total_minus;
    $table->table_column('<b>'.$total_files.'</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_changes.'</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_plus.'</b>', '10%', $bgcolor);
    $table->table_column('<b>'.$total_minus.'</b>', '10%', $bgcolor);
    $table->table_column('<b>&nbsp;</b>', '10%', $bgcolor);
    $table->table_column('<b>&nbsp;</b>', '10%', $bgcolor);

    $table->table_columns_end();
    $table->table_body_end();
    $table->table_end();


    /* Pie with file types */

    $table->table_begin('This table contains a pie graph with the file types in this ');
    $table->table_title('Commits by file type (pie)');
    $table->table_body('<center>'.html_link(html_image('gnuplot/pie/commiter_'.$commiter.'.png', 'Pie for '.$commiter), 'gnuplot/pie/commiter_'.$commiter.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();

    /* Several evolution graphs */

    $array = array(modules, commits, files, LOCs);

    foreach ($array as $graph) {
        $table->table_begin('This table contains the '.$commiter.'-in-time-graph');
        $table->table_title('Evolution of '.$graph.' in time');
        $table->table_body('<center>'.html_link(html_image('gnuplot/evolution/'.$graph.'_in_time_for_commiter_'.$commiter.'.png', $graph.' in time for '.$commiter, '620', '465'), 'gnuplot/evolution/'.$graph.'_in_time_for_commiter_'.$commiter.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
        $table->table_end();
    }


} else {
    $alphabet = array ("A","B","C","D","E","F","G","H","I","J","K","L",
		"M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z");
    $msg = "[ ";

    while (list(, $ltr) = each($alphabet)) {
       $msg .= html_link($ltr, 'PHP_SELF', array ('menu' => 'Commiters', 'by' => $ltr)).' | ';
    }
    $msg .= html_link('All', 'PHP_SELF', array('menu' => 'Commiters', 'by' => 'All'));
    $msg .= ' ]';

    $table->table_strip($msg, 'center');

    print "<center>Ordered by "
          .html_link('alphabetically', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by']))." | "
          .html_link('modules', 'PHP_SELF', array('menu' => 'Commiters', 'by'=> $HTTP_GET_VARS['by'], 'order' => 'modules'))." | "
          .html_link('commits', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by'], 'order' => 'commits'))." | "
          .html_link('files', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by'], 'order' => 'files'))." | "
          .html_link('lines added', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by'], 'order' => 'plus'))." | "
          .html_link('lines removed', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by'], 'order' => 'minus'))." | "
          .html_link('first commit', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by'], 'order' => 'first_commit'))." | "
          .html_link('last commit', 'PHP_SELF', array('menu' => 'Commiters', 'by' => $HTTP_GET_VARS['by'], 'order' => 'last_commit'))."</center>";

    if ($HTTP_GET_VARS['by']) {
        $by = $HTTP_GET_VARS['by'];
    } else {
        $by = 'All';
    }

    if ($by != 'All') {
        $where = "commiter LIKE '$by%' AND";
    }
    if (!$HTTP_GET_VARS['order']) {
        $order = '';
    } else {
        $order = "ORDER BY ".$HTTP_GET_VARS['order']." DESC";
    } 
    $db->query("SELECT  c.commiter, COUNT(DISTINCT(module_id)) AS modules, SUM(commits) AS commits, SUM(plus) AS plus, SUM(minus) AS minus, SUM(files) AS files, MIN(first_commit) AS first_commit, MAX(last_commit) AS last_commit FROM cvsanal_temp_commiters ct, commiters c WHERE ".$where." c.commiter_id = ct.commiter_id GROUP BY commiter ".$order);
    if ($db->num_rows() > 0) {
        $table->table_begin('This table contains FIXME');
    	$table->table_title_begin();
   	$table->table_columns_begin();
    	$table->table_column('<b>#</b>', '4%', $bgcolor);
    	$table->table_column('<b>Commiter</b>', '16%', $bgcolor);
    	$table->table_column('<b>Modules</b>', '10%', $bgcolor);
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

  	$total_modules = 0;
	$total_commits = 0;
        $total_files = 0;
	$total_lines = 0;
        $total_plus = 0;
        $total_minus = 0;
	$i = 0;

        while($db->next_record()) {
	  $i++;
          if ($i%2) {
              $bgcolor = 'white';
          } else {
              $bgcolor = '#EEEEEE';
          } 

          $table->table_column($i, '4%', $bgcolor);
          $table->table_column(html_link($db->f('commiter'), 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $db->f('commiter'))), '16%', $bgcolor);
          $table->table_column($db->f('modules'), '10%', $bgcolor);
 	  $total_modules += $db->f('modules');
          $table->table_column($db->f('commits'), '10%', $bgcolor);
	  $total_commits += $db->f('commits');
          $table->table_column($db->f('files'), '10%', $bgcolor);
          $total_files += $db->f('files');
          $table->table_column($db->f('plus') + $db->f('minus'), '10%', $bgcolor);
          $table->table_column($db->f('plus'), '10%', $bgcolor);
	  $total_plus += $db->f('plus');
          $table->table_column($db->f('minus'), '10%', $bgcolor);
	  $total_minus += $db->f('minus');
          $table->table_column(substr($db->f('first_commit'),0,10), '10%', $bgcolor);
          $table->table_column(substr($db->f('last_commit'),0,10), '10%', $bgcolor);
	  $table->table_nextRowWithColumns();
  	}

	$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
        $table->table_column('<b>&nbsp;</b>', '4%', $bgcolor);
        $table->table_column('<b>Total</b>', '16%', $bgcolor);
        $table->table_column('<b>'.$total_modules.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_commits.'</b>', '10%', $bgcolor);
        $table->table_column('<b>'.$total_files.'</b>', '10%', $bgcolor);
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

}

?>
