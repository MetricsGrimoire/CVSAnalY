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
// $Id: search.php,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

require('include/start.inc');
require('include/search.inc');

// Get the parameter searched
$search = $HTTP_GET_VARS['search'];


// When there's a search for a blank line, we look for 'xxxxxxxx'
if (!isset($search) || $search=='') {
  $search = 'xxxxxxxx';
}

// $iter is a variable for printing the Top Statistics in steps of 10 apps
if (!isset($iter)) {
     $iter=0;
} else {
    $iter*=10;
}

// WISH: have a navigation bar with the different options

// Exact match
$count = search_for_exact_match($search);	


// Partial Match in the name (single word match)
$count += search_for_partial_match_single_word($search, $count);

// Partial Match in the name
$count2 = search_for_partial_match($search, $count);
$count += $count2;

// TODO: if nothing is found: advanced search
search_nothing_found($count);

if ($count) {
    print '<p align="center">'.$count2.' matches found</p>';
}

include('include/end.inc');
?>
