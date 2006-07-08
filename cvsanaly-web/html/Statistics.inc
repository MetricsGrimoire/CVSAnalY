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
// $Id: Statistics.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table;

include('include/stats.inc');

$table->table_strip('<b>'.$GLOBALS['config_sys_name'].' - General Statistics</b>', 'center'); 


$number_of_days = round((strtotime(lastCommit()) - strtotime(firstCommit())) / (24*3600),2);


$table->table_begin('This table contains the first and last considered commit in this analysis');
$bgcolor = '#EEEEEE';
$table->table_title('Historical data');
$table->table_body_begin('top');
$table->table_columns_begin();
$table->table_column('<b>First commit</b>', '50%', $bgcolor);
$table->table_column('<b>'.firstCommit().'</b>', '50%', $bgcolor);
$table->table_nextRowWithColumns();
$table->table_column('<b>Last commit considered (*)</b>', '50%', $bgcolor);
$table->table_column('<b>'.lastCommit().'</b>', '50%', $bgcolor);
$table->table_nextRowWithColumns();
$table->table_column('<b>Number of days</b>', '50%', $bgcolor);
$table->table_column('<b>'.$number_of_days.'</b>', '50%', $bgcolor);
$table->table_columns_end();
/* Body ends */
$table->table_body_end();
$table->table_end();

print "<center>(*) CVSAnalY analysis date. This date is considered as the reference point for further analysis.</center><br>";



$table->table_begin('This table contains numerical statistics on the repository');
$table->table_title_begin();
$bgcolor = $GLOBALS['config_table_general_title_bgcolor'];
$table->table_columns_begin();
$table->table_column('<b>&nbsp;</b>', '35%', $bgcolor);
$table->table_column('<b>Number</b>', '25%', $bgcolor);
$table->table_column('<b>Mean per module</b>', '10%', $bgcolor);
$table->table_column('<b>Mean per commiter</b>', '10%', $bgcolor);
$table->table_column('<b>Mean per commit</b>', '10%', $bgcolor);
$table->table_column('<b>Mean per day</b>', '10%', $bgcolor);
$table->table_columns_end();
$table->table_title_end();
/* Body */

$number_of_modules = numberOfModules();
$number_of_commiters = numberOfCommiters();
$number_of_commits = numberOfCommits();
$number_of_files = numberOfFiles();
$number_of_added_lines = numberOfAddedLines();
$number_of_removed_lines = numberOfRemovedLines();
$number_of_changed_lines = $number_of_added_lines + $number_of_removed_lines;
$number_of_final_lines = $number_of_added_lines - $number_of_removed_lines;

$table->table_body_begin('top');
$table->table_columns_begin(); $bgcolor = 'white';
$table->table_column('<b>Modules</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_modules.'</b>', '25%', $bgcolor);
$table->table_column('1', '10%', $bgcolor);
$table->table_column(round($number_of_modules/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column(round($number_of_modules/$number_of_commits,5), '10%', $bgcolor);
$table->table_column(round($number_of_modules/$number_of_days,4), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Commiters</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_commiters.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_commiters/$number_of_modules,2), '10%', $bgcolor);
$table->table_column('1', '10%', $bgcolor);
$table->table_column(round($number_of_commiters/$number_of_commits,4), '10%', $bgcolor);
$table->table_column(round($number_of_commiters/$number_of_days,2), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Commits</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_commits.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_commits/$number_of_modules,2), '10%', $bgcolor);
$table->table_column(round($number_of_commits/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column('1', '10%', $bgcolor);
$table->table_column(round($number_of_commits/$number_of_days,2), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Files</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_files.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_files/$number_of_modules,2), '10%', $bgcolor);
$table->table_column(round($number_of_files/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column(round($number_of_files/$number_of_commits,2), '10%', $bgcolor);
$table->table_column(round($number_of_files/$number_of_days,2), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Aggregated Lines</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_added_lines.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_added_lines/$number_of_modules,2), '10%', $bgcolor);
$table->table_column(round($number_of_added_lines/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column(round($number_of_added_lines/$number_of_commits,2), '10%', $bgcolor);
$table->table_column(round($number_of_added_lines/$number_of_days,2), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Removed Lines</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_removed_lines.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_removed_lines/$number_of_modules,2), '10%', $bgcolor);
$table->table_column(round($number_of_removed_lines/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column(round($number_of_removed_lines/$number_of_commits,2), '10%', $bgcolor);
$table->table_column(round($number_of_removed_lines/$number_of_days,2), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Changed lines</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_changed_lines.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_changed_lines/$number_of_modules,2), '10%', $bgcolor);
$table->table_column(round($number_of_changed_lines/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column(round($number_of_changed_lines/$number_of_commits,2), '10%', $bgcolor);
$table->table_column(round($number_of_changed_lines/$number_of_days,2), '10%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Final Lines</b>', '35%', $bgcolor);
$table->table_column('<b>'.$number_of_final_lines.'</b>', '25%', $bgcolor);
$table->table_column(round($number_of_final_lines/$number_of_modules,2), '10%', $bgcolor);
$table->table_column(round($number_of_final_lines/$number_of_commiters,2), '10%', $bgcolor);
$table->table_column(round($number_of_final_lines/$number_of_commits,2), '10%', $bgcolor);
$table->table_column(round($number_of_final_lines/$number_of_days,2), '10%', $bgcolor);
$table->table_columns_end();
/* Body ends */
$table->table_body_end();
$table->table_end();

lib_module_filetype_statistics();

/* Pie with file types */

$table->table_begin('This table contains a pie graph with the file types for the whole repository');
$table->table_title('Commits by file type (pie)');
$table->table_body('<center>'.html_link(html_image('gnuplot/pie/cvsanal_repository.png', 'Pie for whole repository'), 'gnuplot/pie/cvsanal_repository.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
$table->table_end();


$table->table_begin('This table contains data for inactivity');
$table->table_title('Inactivity rate for modules');
$table->table_body_begin('top');
$table->table_columns_begin(); $bgcolor = 'white';
$table->table_column('<b>Inactive modules in the last year</b>', '50%', $bgcolor);
$table->table_column(inactiveModules(), '25%', $bgcolor);
$table->table_column(round(100*inactiveModules()/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Inactive modules in the last 2 years</b>', '50%', $bgcolor);
$table->table_column(inactiveModules(2), '25%', $bgcolor);
$table->table_column(round(100*inactiveModules(2)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Inactive modules in the last 3 years</b>', '50%', $bgcolor);
$table->table_column(inactiveModules(3), '25%', $bgcolor);
$table->table_column(round(100*inactiveModules(3)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Inactive modules in the last 4 years</b>', '50%', $bgcolor);
$table->table_column(inactiveModules(4), '25%', $bgcolor);
$table->table_column(round(100*inactiveModules(4)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_columns_end();
$table->table_body_end();
$table->table_end();


$table->table_begin('This table contains data for inactivity');
$table->table_title('Inactivity rate for commiters');
$table->table_body_begin('top');
$table->table_columns_begin(); $bgcolor = 'white';
$table->table_column('<b>Inactive commiters in the last year</b>', '50%', $bgcolor);
$table->table_column(inactiveCommiters(), '25%', $bgcolor);
$table->table_column(round(100*inactiveCommiters()/$number_of_commiters).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Inactive commiters in the last 2 years</b>', '50%', $bgcolor);
$table->table_column(inactiveCommiters(2), '25%', $bgcolor);
$table->table_column(round(100*inactiveCommiters(2)/$number_of_commiters).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Inactive commiters in the last 3 years</b>', '50%', $bgcolor);
$table->table_column(inactiveCommiters(3), '25%', $bgcolor);
$table->table_column(round(100*inactiveCommiters(3)/$number_of_commiters).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Inactive commiters in the last 4 years</b>', '50%', $bgcolor);
$table->table_column(inactiveCommiters(4), '25%', $bgcolor);
$table->table_column(round(100*inactiveCommiters(4)/$number_of_commiters).'%', '25%', $bgcolor);
$table->table_columns_end();
$table->table_body_end();
$table->table_end();

/* Evolution graphs */

$table->table_begin('This table contains the evolution graph for the repository');
$table->table_title("Evolution of the number of modules");
$table->table_body('<center>'.html_link(html_image('gnuplot/evolution/repository_first_and_last.png', 'repository_first_and_last', '620', '465'), 'gnuplot/evolution/repository_first_and_last.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
$table->table_end();




$table->table_begin('This table contains FIXME');
$table->table_title('Commiters per module');
$table->table_body_begin('top');
$table->table_columns_begin(); $bgcolor = 'white';
$table->table_column('<b>Number of modules with 1 commiter</b>', '50%', $bgcolor);
$table->table_column(lessCommitersThan(2), '25%', $bgcolor);
$table->table_column(round(100*lessCommitersThan(2)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Number of modules with less than 3 commiters</b>', '50%', $bgcolor);
$table->table_column(lessCommitersThan(3), '25%', $bgcolor);
$table->table_column(round(100*lessCommitersThan(3)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Number of modules with less than 5 commiters</b>', '50%', $bgcolor);
$table->table_column(lessCommitersThan(5), '25%', $bgcolor);
$table->table_column(round(100*lessCommitersThan(5)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Number of modules with less than 10 commiters</b>', '50%', $bgcolor);
$table->table_column(lessCommitersThan(10), '25%', $bgcolor);
$table->table_column(round(100*lessCommitersThan(10)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_columns_end();
$table->table_body_end();
$table->table_end();


$table->table_begin('This table contains FIXME');
$table->table_title('Herfindahl-Hirschman Index for modules');
$table->table_body_begin('top');
$table->table_columns_begin(); $bgcolor = 'white';
$table->table_column('<b>Number of modules with HHI < 6000</b>', '50%', $bgcolor);
$table->table_column(lessHerfindahlThan(6000), '25%', $bgcolor);
$table->table_column(round(100*lessHerfindahlThan(6000)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Number of modules with HHI < 3000</b>', '50%', $bgcolor);
$table->table_column(lessHerfindahlThan(3000), '25%', $bgcolor);
$table->table_column(round(100*lessHerfindahlThan(3000)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = 'white';
$table->table_column('<b>Number of modules with HHI < 2000</b>', '50%', $bgcolor);
$table->table_column(lessHerfindahlThan(2000), '25%', $bgcolor);
$table->table_column(round(100*lessHerfindahlThan(2000)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_nextRowWithColumns(); $bgcolor = '#EEEEEE';
$table->table_column('<b>Number of modules with HHI < 1200</b>', '50%', $bgcolor);
$table->table_column(lessHerfindahlThan(1200), '25%', $bgcolor);
$table->table_column(round(100*lessHerfindahlThan(1200)/$number_of_modules).'%', '25%', $bgcolor);
$table->table_columns_end();
$table->table_body_end();
$table->table_end();



/* Graphical Statistics for modules */
// FIXME: 'new_modules_in_time', 'new_commiters_in_time', 
$array = array('modules_by_commiters', 'modules_by_commits', 'modules_by_files', 'modules_by_changes', 'commiter_by_modules', 'commiter_by_commits', 'commiter_by_files', 'commiter_by_changes');

foreach ($array as $graph) {
    $table->table_begin('This table contains the graph for '.$graph);
    $table->table_title($graph." (log-log)");
    $table->table_body('<center>'.html_link(html_image('gnuplot/global/'.$graph.'.png', $graph, '620', '465'), 'gnuplot/global/'.$graph.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();
}

/* // By filetype

$table->table_begin('From this point on, we show data for file types');
$table->table_title('General graphs by file type');
$table->table_body();
$table->table_end();

$array = array('modules_by_commiters_', 'modules_by_commits_');

foreach ($array as $graph) {
  foreach($GLOBALS['config_file_types_array'] as $filetype) {
    $table->table_begin('This table contains the graph for '.$graph.$filetype);
    $table->table_title($graph.$filetype." (log-log)");
    $table->table_body('<center>'.html_link(html_image('gnuplot/global/'.$graph.$filetype.'.png', $graph.$filetype, '620', '465'), 'gnuplot/global/'.$graph.$filetype.'.png', array()).'</center><p><center>(Click on the image to see it full-size)</center>');
    $table->table_end();
  }
}

*/

?>
