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
// $Id: show.php,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

include('include/start.inc');

if ($module) {

    print '<font size="-1">[ Ordered by number of: '.html_link('commits', 'show.php', array('module' => $module, 'order' => 'count')).' | '.html_link('changed lines', 'show.php', array('module' => $module, 'order' => 'sum')).' ]';

    $module_orig = $module;
    $module = ereg_replace('-', '_', $module);

    if (!$order) {
        $order = 'count';
    }
    $db->query("SELECT commiter, COUNT(*) AS count, SUM(plus) as sum_plus, SUM(minus) as sum_minus, SUM(plus + minus) as sum FROM ".$module."_log, ".$module."_commiters, modules WHERE ".$module."_log.commiter_id=".$module."_commiters.commiter_id AND ".$module."_log.module_id=modules.module_id AND modules.module='$module_orig' GROUP BY commiter ORDER BY $order DESC;");

    if($db->num_rows() > 0) {
        $table->table_begin('This table contains FIXME');
	$table->table_title('Module: '.$module);
        $table->table_title_begin();
        $table->table_columns_begin();
        $table->table_column('<b>Rank</b>', '5%', $bgcolor);
        $table->table_column('<b>Name</b>', '31%', $bgcolor);
        $table->table_column('<b>Commits</b>', '16%', $bgcolor);
        $table->table_column('<b>Lines Changed</b>', '16%', $bgcolor);
        $table->table_column('<b>Lines Added</b>', '16%', $bgcolor);
        $table->table_column('<b>Lines Removed</b>', '16%', $bgcolor);
        $table->table_columns_end();
        $table->table_title_end();

        /* Body */

        $table->table_body_begin('top');
        $table->table_columns_begin();

        $i=1;
        $total_count = 0;
        $total_plus = 0;
        $total_minus = 0;
        while($db->next_record()) {
            if ($i%2) {
	        $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 
            $table->table_column($i.'.', '5%', $bgcolor);
//            $table->table_column(html_link($db->f('commiter'), 'commiter_'.$db->f('commiter').'.html', array()), '31%', $bgcolor);
            $table->table_column(html_link($db->f('commiter'), 'show.php', array('commiter' => $db->f('commiter'))), '31%', $bgcolor);
            $table->table_column($db->f('count'), '16%', $bgcolor);
	    $total_count += $db->f('count');
            $table->table_column($db->f('sum_plus')+$db->f('sum_minus'), '16%', $bgcolor);
            $table->table_column($db->f('sum_plus'), '16%', $bgcolor);
            $total_plus += $db->f('sum_plus');
            $table->table_column($db->f('sum_minus'), '16%', $bgcolor);
            $total_minus += $db->f('sum_minus');
            $table->table_nextRowWithColumns();
            $i++;
        }
        $table->table_column('<b>Total</b>', '5%', $bgcolor);
        $table->table_column('<b>&nbsp;</b>', '31%', $bgcolor);
        $table->table_column('<b>'.$total_count.'</b>', '16%', $bgcolor);
	$total_changes = $total_plus+$total_minus;
        $table->table_column('<b>'.$total_changes.'</b>', '16%', $bgcolor);
        $table->table_column('<b>'.$total_plus.'</b>', '16%', $bgcolor);
        $table->table_column('<b>'.$total_minus.'</b>', '16%', $bgcolor);

        $table->table_columns_end();
        $table->table_body_end();
        $table->table_end();
    }
} elseif ($commiter) {

    print '<font size="-1">[ Ordered by number of: '.html_link('commits', 'show.php', array('commiter' => $commiter, 'order' => 'count')).' | '.html_link('changed lines', 'show.php', array('commiter' => $commiter, 'order' => 'sum')).' ]</font>';

    if (!$order) {
        $order = 'count';
    }

    $table->table_begin('This table contains FIXME');
    $table->table_title('Commiter: '.$commiter);
    $table->table_title_begin();
    $table->table_columns_begin();
    $table->table_column('<b>Module</b>', '31%', $bgcolor);
    $table->table_column('<b>Commits</b>', '16%', $bgcolor);
    $table->table_column('<b>Lines Changed</b>', '16%', $bgcolor);
    $table->table_column('<b>Lines Added</b>', '16%', $bgcolor);
    $table->table_column('<b>Lines Removed</b>', '16%', $bgcolor);
    $table->table_columns_end();
    $table->table_title_end();

    /* Body */

    $table->table_body_begin('top');
    $table->table_columns_begin();

    $i=1;
    $total_count = 0;
    $total_plus = 0;
    $total_minus = 0;


    $db2->query("SELECT * FROM modules");
    while ($db2->next_record()) {
        $module = ereg_replace('-', '_', $db2->f('module'));

        $db->query("SELECT module, COUNT(*) AS count, SUM(plus) as sum_plus, SUM(minus) as sum_minus, SUM(plus + minus) as sum  FROM ".$module."_log,modules,".$module."_commiters WHERE  ".$module."_log.commiter_id=".$module."_commiters.commiter_id AND ".$module."_log.module_id=modules.module_id AND commiter='$commiter' GROUP BY modules.module_id ORDER BY $order DESC");

        if ($db->num_rows() > 0) {
	    $db->next_record();
            if ($i%2) {
                $bgcolor = 'white';
            } else {
                $bgcolor = '#EEEEEE';
            } 

            $table->table_column(html_link($db->f('module'), 'show.php', array('module' => $db->f('module'))), '31%', $bgcolor);
            $table->table_column($db->f('count'), '16%', $bgcolor);
	    $total_count += $db->f('count');
            $table->table_column($db->f('sum_plus')+$db->f('sum_minus'), '16%', $bgcolor);
            $table->table_column($db->f('sum_plus'), '16%', $bgcolor);
	    $total_plus += $db->f('sum_plus');
            $table->table_column($db->f('sum_minus'), '16%', $bgcolor);
	    $total_minus += $db->f('sum_minus');
        }
        $table->table_nextRowWithColumns();
        $i++;
    }
    $table->table_column('<b>Total</b>', '31%', $bgcolor);
    $table->table_column('<b>'.$total_count.'</b>', '16%', $bgcolor);
    $total_changes = $total_plus+$total_minus;
    $table->table_column('<b>'.$total_changes.'</b>', '16%', $bgcolor);
    $table->table_column('<b>'.$total_plus.'</b>', '16%', $bgcolor);
    $table->table_column('<b>'.$total_minus.'</b>', '16%', $bgcolor);

    $table->table_columns_end();
    $table->table_body_end();
    $table->table_end();

}

include('include/end.inc');
?>
