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
// | Authors: Ricardo Gallir <gallir@uib.es>                              |
// |          Gregorio Robles <grex@scouts-es.org>                        |
// +----------------------------------------------------------------------+
//
// $Id: cache.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 *
 * $lastModified     date     last database modification, in "epochs"
 * $logged           boolean  It takes in account that pages can be accessed
 *                            as public or authorised
 */

function DoHeaders($lastModified, $logged=TRUE)
{

    $now = time();
    $maxCache = $now - 10800; // Max. time before refreshing
    $headers = getallheaders();
    $refresh=TRUE; // refresh, as default

    if(isset($headers["If-Modified-Since"])) {
        // NetCrap sends ";lenght = xxx" after the date
        $arraySince = explode(";", $headers["If-Modified-Since"]);
        $since = strtotime($arraySince[0]);
        if($since >= $lastModified) $refresh=FALSE;
    }

    if($logged == TRUE) {
        $tag="\"AUT".$lastModified."\"";  // A private page
    } else {
        $tag="\"PUB".$lastModified."\"";  // and public one
    }

    if(isset($headers["If-None-Match"])) { // check ETag
        if(strcmp($headers["If-None-Match"], $tag) == 0 ) {
            $refresh=FALSE;
        } else {
            $refresh=TRUE;
        }
    }

    if(!$refresh) {
        header("HTTP/1.1 304 Not changed");
        // The first header must be this
        // otherwise Netcrap gives "No Data" error
        $strLastModified = gmdate("r", $lastModified);
    } else {
        $strLastModified = gmdate("r", $now);
    }

    header("ETag: $tag");  // The new TAG
    header("Last-Modified: $strLastModified");
    header("Expires: " . gmdate("r", time()+3));
    header("Cache-Control: max-age=3, must-revalidate"); // HTTP/1.1

    // Netscape doesn't handle very well the header("Pragma: no-cache");

    if(!$refresh) {
  //        ob_end_clean(); // Just in case..
        die; // Don't do anything more
    }
//    ob_start(); // We start buffering to allow "Content-Lenght" header
                // at the end of the output to allow HTTP/1.0 persistent connections.
}

/**
 * Add following code at the end of your output
 * If we allowed buffering before, we send the lenght
 * to allow HTTP/1.0 persistent connections
 */

function SendLength()
{
    if(ob_get_length()) {
        header("Content-Length: " . ob_get_length());
        ob_end_flush();
        die;  // Delete it if you don't want to finish the script
    }
}

function begin()
{
    /**
     * FIXME
     * this should be a field in the database
     */
  /*
    $query = 'SELECT xxxx FROM table';
    $db->query($query);
  */
    $lastModified = strtotime('last Monday');
    // transform it into the $lastModified way
    DoHeaders($lastModified);
}

/**
 * HTTP validator according to RFC2616 of HTTP/1.1
 * originial author: Ricardo Gallir <gallir@uib.es>
 * original license: BSD type
 *        --> I've changed its license to GNU GPL version 2 or later
 *
 * It's also compatible with HTTP/1.0 and
 * take care of Netscape non-standard headers
 * If more than 10800 secs have gone since last load
 * it makes the client/cache to reload the page
 * Call this function before doing anything else with databases or similar.
 *
 * ob_* functions require 4.0.2 or superior
 */

?>