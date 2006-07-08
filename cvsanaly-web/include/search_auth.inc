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
// $Id: search_auth.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/* TODO: explanation */

/* TODO: PHPDoc documentation */

function search_for_exact_match($search)
{
    global $db, $array_with_already;

    $table_alt = new Table();

    $db->query("SELECT * 
                FROM cvsanal_temp_commiters,
		     commiters
		WHERE commiters.commiter='$search'
		     AND commiters.commiter_id = cvsanal_temp_commiters.commiter_id");
    if ($db->num_rows() > 0) {

        $table_alt->table_strip('<center><b>Exact Match</b></center>');

        while ($db->next_record()) {
            $array_with_already[] = $db->f('commiter');
            htmlp_link($db->f('commiter'), 'index.php', array('menu' => 'Commiters', 'commiter' => $db->f('commiter')));
	    print "<br>\n";
            return 1;
        }
    } else {
        return 0;
    }
}

// FIXME: three conditions:
// FIXME: LIKE '$search %' for starting word
// FIXME: LIKE ' % $search %' for a condition in the middle
// FIXME: LIKE '% $search' for the last word

function search_for_partial_match_single_word($search, $count)
{
    global $db;

    $db->query("SELECT * 
                FROM cvsanal_temp_commiters ctc,
		     commiters c
		WHERE ctc.commiter_id = c.commiter_id
		      AND (c.commiter LIKE '% $search%' OR c.commiter LIKE '$search %' OR c.commiter LIKE '$search %') ");
    if ($db->num_rows() > 0) {
        return _showIt(&$db, 'Matches a single word in the commiter', $count, $search);
    } else {
        return 0;
    }
}

function search_for_partial_match($search, $count)
{
    global $db;

    $db->query("SELECT * 
                FROM  cvsanal_temp_commiters,
		      commiters
		WHERE commiters.commiter_id = cvsanal_temp_commiters.commiter_id AND
		      commiters.commiter LIKE '%$search%'");



    if ($db->num_rows() > 0) {
        return _showIt(&$db,'Partial match in the commiter',$count, $search);
    } else {
        return 0;
    }
}

function search_for_match_in_description ($search, $count)
{
    global $db;

    $db->query("SELECT * FROM table WHERE status='A' AND description LIKE '% $search %' ORDER BY modification DESC");
    if ($db->num_rows() > 0) {
        return _showIt(&$db,'Exact match in the description',$count, $search);
    } else {
        return 0;
    }
}

function search_for_partial_match_in_description ($search, $count)
{
    global $db;

    $db->query("SELECT appid FROM table WHERE status='A' AND description LIKE '%$search%' ORDER BY modification DESC");
    if ($db->num_rows() > 0) {
        return _showIt(&$db,'Partial match in the description',$count, $search);
    } else {
        return 0;
    }
}

function search_nothing_found($count)
{
    global $table;

    if ($count == 0) {
        $table->table_full(_('Search'),_("No commiters found"));
    }
}

function _showIt($db, $message, $count, $search)
{
    global $array_with_already;

    $table_alt = new Table();

    $j = 0;
    while ($db->next_record() && $i < (1000 - $count)) {
        if (!_inArray($array_with_already, $db->f('commiter'))) {
            if ($j==0) {
                $table_alt->table_strip('<center><b>'.$message.'</b></center>');
            }
            htmlp_link($db->f('commiter'), 'index.php', array('menu' => 'Commiters', 'commiter' => $db->f('commiter')));
	    print "<br>&nbsp;\n";
            $array_with_already[] = $db->f('commiter');
            $i++;
            $j++;
        }
    }
    return $db->num_rows();
}

function _inArray($array, $value)
{
    for ($i=0; $i < sizeof($array)+1; $i++) {
        if ($array[$i] == $value) {
            return 1;
        }
    }
}
?>
