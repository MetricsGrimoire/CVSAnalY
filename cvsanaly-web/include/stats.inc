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
// $Id: stats.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * Stats Library
 *
 */

function numberOfModules() {
    global $db;
    $db->query("SELECT COUNT(DISTINCT module) AS count FROM modules");
    $db->next_record();
    return $db->f('count');
}

function numberOfCommiters() {
    global $db;
    //Replaced
    //$db->query("SELECT COUNT(DISTINCT(commiter)) AS count FROM cvsanal_temp_commiters");
    $db->query("SELECT COUNT(DISTINCT(commiter_id)) AS count 
                FROM cvsanal_temp_commiters");
    $db->next_record();
    return $db->f('count');
}

function numberOfCommits() {
    global $db;
    $db->query("SELECT SUM(commits) AS sum FROM cvsanal_temp_commiters");
    $db->next_record();
    return $db->f('sum');
}

function numberOfChangedLines() {
    global $db;
    $db->query("SELECT SUM(plus + minus) as sum FROM cvsanal_temp_commiters");
    $db->next_record();
    return $db->f('sum');
}

function numberOfAddedLines() {
    global $db;
    $db->query("SELECT SUM(plus) as sum FROM cvsanal_temp_commiters");
    $db->next_record();
    return $db->f('sum');
}

function numberOfRemovedLines() {
    global $db;
    $db->query("SELECT SUM(minus) as sum FROM cvsanal_temp_commiters");
    $db->next_record();
    return $db->f('sum');
}

function numberOfFiles() {
    global $db;
    $db->query("SELECT SUM(files) as count FROM cvsanal_temp_modules");
    $db->next_record();
    return $db->f('count');
}

function firstCommit() {
    global $db;
    $db->query("SELECT MIN(first_commit) AS first FROM cvsanal_temp_modules");
    $db->next_record();
    return $db->f('first');
}

function lastCommit() {
    global $db;
    $db->query("SELECT MAX(last_commit) AS last FROM cvsanal_temp_modules");
    $db->next_record();
    return $db->f('last');
}

function inactiveModules($years = 1) {
    global $db;

    $last_year = strtotime(lastCommit()) - $years * 365 * 24 * 3600;
    $db->query("SELECT MAX(last_commit) AS last_commit FROM cvsanal_temp_modules GROUP BY module_id ORDER BY last_commit");
    $i=0;
    while ($db->next_record()) {
      
      if (strtotime($db->f('last_commit')) < $last_year) {$i++;}
      else {return $i;}
    }
}

function inactiveCommiters($years = 1) {
    global $db;

    $last_year = strtotime(lastCommit()) - $years * 365 * 24 * 3600;
    //Replaced
    //$db->query("SELECT MAX(last_commit) AS last_commit FROM cvsanal_temp_commiters GROUP BY commiter ORDER BY last_commit");
    $db->query("SELECT MAX(last_commit) AS last_commit 
                FROM cvsanal_temp_commiters 
		GROUP BY commiter_id ORDER BY last_commit");
    
    $i=0;
    while ($db->next_record()) {
      if (strtotime($db->f('last_commit')) < $last_year) {$i++;}
      else {return $i;}
    }
}


function lessCommitersThan($number_of_commiters) {
    global $db;

    $db->query("SELECT MAX(commiters) AS commiters FROM cvsanal_temp_modules GROUP BY module_id ORDER BY commiters");
    $i=0;
    while ($db->next_record()) {
      if ($db->f('commiters') < $number_of_commiters) {$i++;}
      else {return $i;}
    }
}

function lessHerfindahlThan($value) {
    global $db;
    $db->query("SELECT COUNT(*) AS count FROM cvsanal_temp_inequality WHERE herfindahl < '".$value."'");
    $db->next_record();
    return $db->f('count');
}

?>
