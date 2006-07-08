<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |        SourceWell 2 - The GPL Software Announcement System           |
// +----------------------------------------------------------------------+
// |      Copyright (c) 2001-2002 BerliOS, FOKUS Fraunhofer Institut      |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors: Gregorio Robles <grex@scouts-es.org>                        |
// +----------------------------------------------------------------------+
//
// $Id: lib.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

/**
 * Miscellaneous Library
 *
 * FIXME and TODO: There's a lot of work to be done here
 *       --> add functions
 *       --> add documentation
 *       --> refactor functions
 */

/**
 * Returns time in timestamp format 
 *
 * @param   int       $time          TODO
 * @return  int                      Timestamp
 *
 * @access public
 */
function mktimestamp($time)
{
    $timestamp = mktime(substr($time,8,2),substr($time,10,2),
                        substr($time,12,2),substr($time,4,2),
                        substr($time,6,2),substr($time,0,4));
    return $timestamp;
}

#
# returns something like this: monday, 5th November 2001, 19:45:00 CET
# second (optional) parameter is to know if $time is already in timestamp format
#

function lib_date_long($time, $timestamp = 0)
{
    if (!$timestamp) { 
        $time = mktimestamp($time);
    }
    return strftime("%A, %e de %B de %Y, %H:%M:%S %Z", $time);
}

/*
 * returns something like: 16:34 09.11.01
 */

function lib_date_medium($time, $timestamp = 0)
{
    if (!$timestamp) { 
        $time = mktimestamp($time);
    }
    return strftime("%H:%M %d.%m.%y", $time);
}


function lib_date_short($time, $timestamp = 0)
{
    if (!$timestamp) { 
        $time = mktimestamp($time);
    }
    return strftime("%e. %b", $time);
}

## show_more($iter,$maxiter,$url,$urlquery)
##
## shows 10 apps of the current iteraction $iter
## until it reaches the maximum number of iteractions $maxiter
## $url is the name of the page (*.php3)
## $urlquery contains an array with the paramaters for the new page
##            (everything after the ?)

/* DEPRECATED FUNCTION : Funcion en desuso */
/* Should be done through the use of the Summary or Stats calss */
/* I strongly believe this code is rubbish! */

function lib_mostrar_mas($iter,$maxiter,$url,$urlquery) {
  global $sess;

  $iter /=10;
  echo '<table border=0 width=600><tr>';
  echo '<td>&nbsp;</td>\n';
  echo '<td align=right>';

  $maxiter= Floor($maxiter);

  if ($iter > 3) {
    echo "<a href=\"".$sess->url($url).$sess->add_query($urlquery).$sess->add_query(array("iter" => 0))."\">&lt;&lt;</a>\n";
  }

  $number = $iter - 3;
  if ($number < 0) $number = 0;
  if ($iter > 2) {
    echo "<a href=\"".$sess->url($url).$sess->add_query($urlquery).$sess->add_query(array("iter" => $number))."\">&lt;</a>\n";
  }

  switch ($iter) {
    case 0: $bias=0; break;
    case 1: $bias=1; break;
    case ($maxiter-1): if ($iter>3) {$bias=3;} else {$bias=2;} break;
    case ($maxiter): if ($iter>4) {$bias=4;} else {$bias=2;} break;
    default: $bias=2; break;
  }

  for($i=$iter-$bias;$i<$maxiter+1 && $i<($iter+5-$bias);$i++) {
    $number1 = $i*10 +1;
    $number2 = $number1 + 9;
    $number = strval($number1)."-".strval($number2);
    if ($i != $iter) {
      echo "<a href=\"".$sess->url($url).$sess->add_query($urlquery).$sess->add_query(array("iter" => $i))."\">&nbsp;$number</a>\n";
    }
    else echo "<B>&nbsp;$number</B>\n"; 
   }

  $number = $iter + 5 - $bias;
  if ($number > $maxiter+$bias) $number =$maxiter+$bias;
  if ($iter < $maxiter-4+$bias) {
    echo "<a href=\"".$sess->url($url).$sess->add_query($urlquery).$sess->add_query(array("iter" => $number))."\"> &gt;</a>\n";
  }

  $number = $iter + 10 - $bias;
  if ($number > $maxiter) $number = $maxiter;
  if ($iter < $maxiter-5 +$bias) {
    echo "<a href=\"".$sess->url($url).$sess->add_query($urlquery).$sess->add_query(array("iter" => $number))."\"> &gt;&gt;</a>\n";
  }

   echo "</td>\n";
   echo "</tr></table><br>";
}
/*
function _($string)
{
    return $string;
}
*/
/**
 * Our 'die' function
 * Should be called when something anomalous happens
 * It mails the sys admins with the error message
 *
 * @param   string    $error_message    Error message
 * @global  object    $t                Translation object
 * @access public
 */
function lib_die($error_message)
{
    global $t;
    /* WISH: to do not have to include config.inc another time */
    require('config.inc');
    $be = new box('80%',$th_box_frame_color,$th_box_frame_width,
                  $th_box_title_bgcolor,$th_box_title_font_color,
                  $th_box_title_align,$th_box_body_bgcolor,
                  $th_box_error_font_color,$th_box_body_align);

    $be->box_full($t->translate('An error has ocurred'),
		  $error_message
		  .'<p>'
		  .$t->translate('This error is being mailed to the system administrators.'));

    /* Mails the sys admins */
    include('monitorlib.inc');
    mailuser('admin', 'An error has ocurred', $error_message);
}

/**
 * This functions provides the database names used from the original
 * ones. This is because some characters (-, +, ., etc.) are not
 * permitted in SQL. 
 *
 * @param   string    $module		Original module name
 * @return  string    $module		Module name as used in the database
 * @access public
 */


function lib_dbModuleName($module)
{
    $module = ereg_replace('-', '_minus_', $module);
    $module = ereg_replace('\.', '_dot_', $module);
    $module = ereg_replace(':', '_ddot_', $module);
    $module = ereg_replace('\+', '_plus_', $module);
    $module = ereg_replace('@', '_at_', $module);
    return $module;
}


/**
 * This functions prints a summary of the module named $module_orig
 *
 * @param   string    $module_orig	Original module name
 * @access public
 */

function lib_module_summary($module_orig) {
    global $db, $db2, $table;

    $db->query("SELECT module, 
                       SUM(commiters) AS commiters, 
                       SUM(commits) AS commits, 
		       SUM(files) AS files, 
		       SUM(plus) as plus, 
		       SUM(minus) AS minus, 
		       MIN(first_commit) AS first_commit, 
		       MAX(last_commit) AS last_commit 
		FROM cvsanal_temp_modules  
		WHERE module='".$module_orig."' 
		GROUP BY module_id");
		
    if($db->num_rows() > 0) {
        $table->table_begin('This table contains a summary of this module');
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
	
	//Query replaced
        //$db2->query("SELECT COUNT(*) AS commiters FROM ".lib_dbModuleName($db->f('module'))."_commiters");
	$db2->query("SELECT COUNT(cm.commiter_id) AS commiters 
	             FROM commiters_module cm,
		     	  modules m
	             WHERE 
		         cm.module_id = m.module_id and 
			 m.module = '" . $db->f('module') ."'");

	
	$db2->next_record();

	$table->table_column("<b>".html_link($module_orig, 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig))."</b>", '19%', $bgcolor);
        $table->table_column($db2->f('commiters'), '10%', $bgcolor);
        $table->table_column($db->f('commits'), '10%', $bgcolor);
        $table->table_column($db->f('files'), '10%', $bgcolor);
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
}


/**
 * This functions prints a summary of the different file types that are
 * used in the module given by $module_orig
 *
 * if $module_orig = "" (empty), then 
 *
 * @param   string    $module_orig	Original module name
 * @access public
 */

function lib_module_filetype_summary($module_orig, $order='commits') {
    global $db, $table;

    if (!$order) {
	$select = "*";
	$order = 'commits';
    }

    $db->query("SELECT * 
                FROM cvsanal_temp_modules, 
		     cvsanal_fileTypes 
		WHERE module='".$module_orig."' 
		      AND cvsanal_temp_modules.filetype=cvsanal_fileTypes.fileType_id 
		ORDER BY ".$order." DESC");

    if($db->num_rows() > 0) {

	 $table->table_strip('<center><b>Files by file type for module '.$module_orig.'</b></center>');

           print "<center>File types ordered by "
              .html_link('type', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'type_order' => 'filetype_id'))." | "
              .html_link('commiters', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'type_order' => 'commiters'))." | "
              .html_link('commits', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'type_order' => 'commits'))." | "
              .html_link('files', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'type_order' => 'files'))." | "
              .html_link('lines added', 'PHP_SELF', array('menu' => 'Modules', 'type_order' => 'plus', 'module' => $module_orig))." | "
              .html_link('external', 'PHP_SELF', array('menu' => 'Modules', 'type_order' => 'external', 'module' => $module_orig))." | "
              .html_link('cvs flag', 'PHP_SELF', array('menu' => 'Modules', 'type_order' => 'cvs_flag', 'module' => $module_orig))." | "
              .html_link('lines removed', 'PHP_SELF', array('menu' => 'Modules', 'type_order' => 'minus', 'module' => $module_orig))." | "
              .html_link('first commit', 'PHP_SELF', array('menu' => 'Modules', 'type_order' => 'first_commit', 'module' => $module_orig))." | "
              .html_link('last commit', 'PHP_SELF', array('menu' => 'Modules', 'type_order' => 'last_commit', 'module' => $module_orig))."</center>";


        $table->table_begin('This table contains a summary of the different file types used in this module');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>File type</b>', '9%', $bgcolor);
        $table->table_column('<b>Commiters</b>', '9%', $bgcolor);
        $table->table_column('<b>Commits</b>', '8%', $bgcolor);
        $table->table_column('<b>Files</b>', '8%', $bgcolor);
        $table->table_column('<b>Lines Changed</b>', '8%', $bgcolor);
        $table->table_column('<b>Lines Added</b>', '8%', $bgcolor);
        $table->table_column('<b>Lines Removed</b>', '8%', $bgcolor);
        $table->table_column('<b>Removed files</b>', '8%', $bgcolor);
        $table->table_column('<b>External</b>', '8%', $bgcolor);
        $table->table_column('<b>CVS flag</b>', '8%', $bgcolor);
        $table->table_column('<b>First commit</b>', '9%', $bgcolor);
        $table->table_column('<b>Last commit</b>', '9%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();
        /* Body */
        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
        $total_modules = 0;
        $total_commiters = 0;
	$total_commits = 0;
        $total_files = 0;
	$total_changes = 0;
        $total_plus = 0;
        $total_minus = 0;
	$total_external = 0;
	$total_cvs_flag = 0;
	while ($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 

	    $table->table_column(html_link($db->f('fileType'), 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'filetype' => $db->f('filetype'))), '9%', $bgcolor);
            $table->table_column($db->f('commiters'), '9%', $bgcolor);
	    $total_commiters += $db->f('commiters');
            $table->table_column($db->f('commits'), '8%', $bgcolor);
	    $total_commits += $db->f('commits');
            $table->table_column($db->f('files'), '8%', $bgcolor);
	    $total_files += $db->f('files');
            $table->table_column($db->f('plus')+$db->f('minus'), '8%', $bgcolor);
	    $total_changes += $db->f('plus')+$db->f('minus');
            $table->table_column($db->f('plus'), '8%', $bgcolor);
	    $total_plus += $db->f('plus');
            $table->table_column($db->f('minus'), '8%', $bgcolor);
	    $total_minus += $db->f('minus');
            $table->table_column($db->f('inAtticFiles'), '8%', $bgcolor);
	    $total_inAtticFiles += $db->f('inAtticFiles');
            $table->table_column($db->f('external'), '8%', $bgcolor);
	    $total_external += $db->f('external');
            $table->table_column($db->f('cvs_flag'), '8%', $bgcolor);
	    $total_cvs_flag += $db->f('cvs_flag');
            $table->table_column(substr($db->f('first_commit'),0,10), '9%', $bgcolor);
            $table->table_column(substr($db->f('last_commit'),0,10), '9%', $bgcolor);
            $table->table_nextRowWithColumns();
	    $i++;
	}
	$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
        $table->table_column('<b>Total</b>', '9%', $bgcolor);
        $table->table_column('<b>('.$total_commiters.')</b>', '9%', $bgcolor);
        $table->table_column('<b>'.$total_commits.'</b>', '9%', $bgcolor);
        $table->table_column('<b>'.$total_files.'</b>', '8%', $bgcolor);
	$total_changes = $total_plus+$total_minus;
        $table->table_column('<b>'.$total_changes.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_plus.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_minus.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_inAtticFiles.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_external.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_cvs_flag.'</b>', '8%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '9%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '9%', $bgcolor);

        $table->table_columns_end();
	/* Body ends */
        $table->table_body_end();
        $table->table_end();
    }

    /* Pie with file types */

    $table->table_begin('This table contains a pie graph with the file types in this module');
    $table->table_title('Commits by file type (pie)');
    $table->table_body('<center>'.html_link(html_image('gnuplot/pie/module_'.$module_orig.'.png', 'Pie for '.$module_orig), 'gnuplot/pie/module_'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();

}


/**
 * This functions prints a summary of the different file types that are
 * used in the module given by $module_orig
 *
 * if $module_orig = "" (empty), then 
 *
 * @param   string    $module_orig	Original module name
 * @access public
 */

function lib_module_filetype_statistics() {
    global $db, $table;

    $select = "COUNT(DISTINCT(module_id)) AS modules, SUM(commits) AS commits, SUM(plus) AS plus, SUM(minus) AS minus, SUM(files) AS files, SUM(cvs_flag) AS cvs_flag, SUM(external) AS external, cvsanal_fileTypes.filetype, SUM(inAtticFiles) AS inAtticFiles, MIN(first_commit) AS first_commit, MAX(last_commit) AS last_commit";
    $from = "cvsanal_temp_modules, cvsanal_fileTypes";
    $where = " WHERE cvsanal_temp_modules.filetype=cvsanal_fileTypes.fileType_id";
    $where .= " GROUP BY filetype";

    $db->query("SELECT ".$select." 
                FROM ".$from." ".$where." 
		ORDER BY commits DESC");

    if($db->num_rows() > 0) {

	 $table->table_strip('<center><b>File-type statistics for all modules</b></center>');

        $table->table_begin('This table contains a summary of the different file types used in this module');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>File type</b>', '9%', $bgcolor);
        $table->table_column('<b>Modules</b>', '9%', $bgcolor);
        $table->table_column('<b>Commits</b>', '8%', $bgcolor);
        $table->table_column('<b>Files</b>', '8%', $bgcolor);
        $table->table_column('<b>Lines Changed</b>', '8%', $bgcolor);
        $table->table_column('<b>Lines Added</b>', '8%', $bgcolor);
        $table->table_column('<b>Lines Removed</b>', '8%', $bgcolor);
        $table->table_column('<b>Removed files</b>', '8%', $bgcolor);
        $table->table_column('<b>External</b>', '8%', $bgcolor);
        $table->table_column('<b>CVS flag</b>', '8%', $bgcolor);
        $table->table_column('<b>First commit</b>', '9%', $bgcolor);
        $table->table_column('<b>Last commit</b>', '9%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();
        /* Body */
        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
        $total_modules = 0;
	$total_commits = 0;
        $total_files = 0;
	$total_changes = 0;
        $total_plus = 0;
        $total_minus = 0;
	$total_external = 0;
	$total_cvs_flag = 0;
	$total_inAtticFiles = 0;
	while ($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 

	    $table->table_column("<b>".$db->f('filetype')."</b>", '9%', $bgcolor);
            $table->table_column($db->f('modules'), '9%', $bgcolor);
	    $total_modules += $db->f('modules');
            $table->table_column($db->f('commits'), '8%', $bgcolor);
	    $total_commits += $db->f('commits');
            $table->table_column($db->f('files'), '8%', $bgcolor);
	    $total_files += $db->f('files');
            $table->table_column($db->f('plus')+$db->f('minus'), '8%', $bgcolor);
	    $total_changes += $db->f('plus')+$db->f('minus');
            $table->table_column($db->f('plus'), '8%', $bgcolor);
	    $total_plus += $db->f('plus');
            $table->table_column($db->f('minus'), '8%', $bgcolor);
	    $total_minus += $db->f('minus');
            $table->table_column($db->f('inAtticFiles'), '8%', $bgcolor);
	    $total_inAtticFiles += $db->f('inAtticFiles');
            $table->table_column($db->f('external'), '8%', $bgcolor);
	    $total_external += $db->f('external');
            $table->table_column($db->f('cvs_flag'), '8%', $bgcolor);
	    $total_cvs_flag += $db->f('cvs_flag');
            $table->table_column(substr($db->f('first_commit'),0,10), '9%', $bgcolor);
            $table->table_column(substr($db->f('last_commit'),0,10), '9%', $bgcolor);
            $table->table_nextRowWithColumns();
	    $i++;
	}
	$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
        $table->table_column('<b>Total</b>', '9%', $bgcolor);
        $table->table_column('<b>('.$total_modules.')</b>', '9%', $bgcolor);
        $table->table_column('<b>'.$total_commits.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_files.'</b>', '8%', $bgcolor);
	$total_changes = $total_plus+$total_minus;
        $table->table_column('<b>'.$total_changes.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_plus.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_minus.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_inAtticFiles.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_external.'</b>', '8%', $bgcolor);
        $table->table_column('<b>'.$total_cvs_flag.'</b>', '8%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '9%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '9%', $bgcolor);

        $table->table_columns_end();
	/* Body ends */
        $table->table_body_end();
        $table->table_end();
    }
}



/**
 * This functions prints a summary of the different commiters
 * that have participated in a module
 * If the filetype is given, then only the stats for that filetype 
 * are shown
 *
 * @param   string    $module_orig	Original module name
 * @param   string    $filetype		File type
 * @access public
 */

function lib_commiter_summary($module_orig, $order, $filetype='') {
    global $db, $table, $config_table_general_title_bgcolor;

    if ($filetype != '') {
	$query = "SELECT * 
	          FROM cvsanal_temp_commiters,
		       cvsanal_fileTypes,modules 
		  WHERE modules.module_id=cvsanal_temp_commiters.module_id 
		        AND cvsanal_temp_commiters.filetype=cvsanal_fileTypes.fileType_id 
			AND cvsanal_fileTypes.fileType='".$filetype."' 
			AND modules.module='".$module_orig."'";
    } else {
/*	$query = "SELECT commiter, 
	                 SUM(commits) AS commits, 
			 SUM(files) AS files, 
			 SUM(plus) AS plus, 
			 SUM(minus) AS minus, 
			 MIN(first_commit) AS first_commit, 
			 MAX(last_commit) AS last_commit 
	          FROM cvsanal_temp_commiters,
		       modules 
		  WHERE modules.module_id=cvsanal_temp_commiters.module_id 
		         AND modules.module='".$module_orig."' 
	          GROUP BY commiter";
*/
      $query = "SELECT commiters.commiter,
                   SUM(commits) AS commits,
                   SUM(files) AS files,
                   SUM(plus) AS plus,
                   SUM(minus) AS minus,
                   MIN(first_commit) AS first_commit,
                   MAX(last_commit) AS last_commit
                FROM cvsanal_temp_commiters,
	             modules,
		     commiters
	        WHERE modules.module_id=cvsanal_temp_commiters.module_id
	              AND modules.module='".$module_orig."'
		      AND commiters.commiter_id = cvsanal_temp_commiters.commiter_id
	        GROUP BY commiters.commiter";																																  
    }
    
    if ($filetype != '') {
	$fileTitle = $filetype.' files in ';
    }
    $table->table_strip('<center><b>Commiters that have participated in '.$fileTitle.' module '.$module_orig."</b></center>");

    print "<center>Commiters ordered by "
          .html_link('name', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'order' => 'commiter'))." | "
          .html_link('commits', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'order' => 'commits'))." | "
          .html_link('files', 'PHP_SELF', array('menu' => 'Modules', 'module' => $module_orig, 'order' => 'files'))." | "
          .html_link('lines added', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'plus', 'module' => $module_orig))." | "
          .html_link('lines removed', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'minus', 'module' => $module_orig))." | "
          .html_link('first commit', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'first_commit', 'module' => $module_orig))." | "
          .html_link('last commit', 'PHP_SELF', array('menu' => 'Modules', 'order' => 'last_commit', 'module' => $module_orig))."</center>";

    if (!$order) {
        $order = 'commits';
    }

    $db->query($query." ORDER BY ".$order." DESC");
    if($db->num_rows() > 0) {
        $table->table_begin('This table contains a list of the commiters that haver commited at least once to this module');
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>Rank</b>', '4%', $bgcolor);
        $table->table_column('<b>Name</b>', '26%', $bgcolor);
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
        $total_count = 0;
        $total_files = 0;
        $total_plus = 0;
        $total_minus = 0;
        while($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 
            $table->table_column($i.'.', '4%', $bgcolor);
            $table->table_column(html_link($db->f('commiter'), 'PHP_SELF', array('menu' => 'Commiters', 'commiter' => $db->f('commiter'))), '26%', $bgcolor);
            $table->table_column($db->f('commits'), '10%', $bgcolor);
	    $total_count += $db->f('commits');
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
            $i++;
        }
	$bgcolor = $config_table_general_title_bgcolor;
	$table->table_column('<b>&nbsp;</b>', '4%', $bgcolor);
        $table->table_column('<b>Total</b>', '28%', $bgcolor);
        $table->table_column('<b>'.$total_count.'</b>', '10%', $bgcolor);
        $table->table_column('<b>('.$total_files.')</b>', '10%', $bgcolor);
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

/**
 *
 *
 */

function lib_show_graphs ($module_orig)
{
    global $db, $table;

    $module = lib_dbModuleName($module_orig);

    $array = array(commiters, commits, files, LOCs);

    foreach ($array as $graph) {
        $table->table_begin('This table contains the '.$array.'-in-time-graph');
        $table->table_title('Evolution of '.$graph.' in time');
        $table->table_body('<center>'.html_link(html_image('gnuplot/evolution/'.$graph.'_in_time_for_module_'.$module_orig.'.png', $graph.' in time for '.$module_orig, '620', '465'), 'gnuplot/evolution/'.$graph.'_in_time_for_module_'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
        $table->table_end();
    }

    /* Activity rate by hour */

    $table->table_begin('This table contains the hour activity rate');
    $table->table_title('Commit activity by clock time');
    $table->table_body('<center>'.html_link(html_image('gnuplot/activity/hours_'.$module_orig.'.png', 'Commit activity for '.$module_orig), 'gnuplot/activity/hours_'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();

    /* weekday activity rate */

    $table->table_begin('This table contains the hour activity rate');
    $table->table_title('Commit activity by day of the week');
    $table->table_body('<center>'.html_link(html_image('gnuplot/activity/weekdays_'.$module_orig.'.png', 'Commit activity by day of the week for '.$module_orig), 'gnuplot/activity/weekdays_'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();


    /* Lorenz/Gini curve */

    $table->table_begin('This table contains Lorenz curve');
    $table->table_title('Lorenz curve (Gini coefficient)');
    $table->table_body('<center>(Gives an idea visually (and numerically) of how unequal the commits are distributed among commiters)</center>');
    $table->table_body('<center>'.html_link(html_image('gnuplot/gini/'.$module_orig.'.png', 'Lorenz curve for '.$module_orig, '620', '465'), 'gnuplot/gini/'.$module_orig.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();

    /* File type correlation animated heat map */

    $table->table_begin('This table contains some graphs about the relationship between filetypes');
    $table->table_title('Correlation between different file types (for several equally-large time slots of the project)');
    $table->table_body('<center>(This allows for instance to know the specialization of commiters in a given module)<br>(diagonal ommited for obvious reasons)</center>');
    $table->table_body('<center>'.html_link(html_image('gnuplot/filetype/'.$module_orig.'-animated.gif', 'Filetype correlation for '.$module_orig), 'gnuplot/filetype/'.$module.'-animated.gif', array()).'</center><p><center>(Click on the image to see it full-size)</center>'
);
    $table->table_end();

    /* Generation graphs */

    $table->table_begin('This table contains some generation graphs');
    $table->table_title('Generation graphs (10 intervals, top 20% commiters)');
    $table->table_body('<center>(Allows to see the evolution of the members of the core group in time)</center>');
    $table->table_body('<center>'.html_link(html_image('gnuplot/generations/'.$module.'_log_10_22.png', 'Core group evolution in time for '.$module_orig, '620', '465'), 'gnuplot/generations/'.$module.'_log_10_22.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>'.
	'<center>'.html_link(html_image('gnuplot/generations/'.$module.'_log-per_10_22.png', 'Core group evolution in time for '.$module_orig, '620', '465'), 'gnuplot/generations/'.$module.'_log-per_10_22.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>'.
	'<center>'.html_link(html_image('gnuplot/generations/'.$module.'_log-sum_10_22.png', 'Core group evolution in time for '.$module_orig, '620', '465'), 'gnuplot/generations/'.$module.'_log-sum_10_22.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>'
);
    $table->table_end();

    /* Heat map for commiters */

    $table->table_begin('This table contains the heat maps');
    $table->table_title('Heat map of commiter activity');
    $table->table_body('<center>(Gives the relative activity for each commiter in a given time slot)</center>');
    $table->table_body_begin('top');
    
    #Next line Replaced:
    #$db->query("SELECT COUNT(DISTINCT(commiter_id)) AS count FROM ".$module."_log");
    $db->query("SELECT COUNT(DISTINCT(commiter_id)) AS count 
                FROM log, modules
		WHERE log.module_id = modules.module_id
		      AND modules.module ='".$module."'");
    
    $db->next_record();
    $number = ceil($db->f('count')/25);

    print "<center><table bgcolor=black width=60%><tr><td>";
    for ($i=1;$i<$number+1;$i++) {
        print '<center>'.html_link(html_image('gnuplot/heatmaps/'.$module_orig.'___'.$i.'.png', 'Heat map for '.$module_orig), 'gnuplot/heatmaps/'.$module_orig.'___1.png', array()).'</center>'."\n";
    }
    print "</td></tr></table></center>";
    $table->table_body_end();
    $table->table_end();

/* FIXME FIXME: this should change some time in the future */
/*
    $bgcolor = '#EEEEEE';
    $table->table_begin('This table contains generation graphs about this module');
    $table->table_title('Generational graphs with other numbers of intervals and top % of commiters considered as core group');
    $table->table_body_begin('top');
    $table->table_columns_begin();
    $table->table_column('&nbsp;', '25%', $bgcolor);
    $table->table_column('5 time slots', '25%', $bgcolor);
    $table->table_column('10 time slots', '25%', $bgcolor);
    $table->table_column('20 time slots', '25%', $bgcolor);
    $table->table_nextRowWithColumns();
    $table->table_column('Top 5% of commiters', '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '5', 'percentage' => '6')), '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '10', 'percentage' => '11')), '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '20')), '25%', $bgcolor);
    $table->table_nextRowWithColumns();
    $table->table_column('Top 10% of commiters', '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '5', 'percentage' => '6')), '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '10', 'percentage' => '11')), '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '20')), '25%', $bgcolor);
    $table->table_nextRowWithColumns();
    $table->table_column('Top 20% of commiters', '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '5', 'percentage' => '6')), '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '10', 'percentage' => '11')), '25%', $bgcolor);
    $table->table_column(html_link('Graphs', 'PHP_SELF', array('menu' => 'Generations', 'module' => $module_orig, 'graph' => '20')), '25%', $bgcolor);
    $table->table_columns_end();
    $table->table_body_end();
    $table->table_end();
*/

}

?>
