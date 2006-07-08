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
// | Authors: Lutz Henckel <lutz.henckel@fokus.fhg.de>                    |
// +----------------------------------------------------------------------+
//
// $Id: Navigation.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * Class Navigation: a class for links in the navigation bar
 *
 * This library contains an object oriented vision of the links that
 * usually are in the navigation bar.
 * Links can be easily configured in the config.inc file
 *
 * @author Gregorio Robles <grex@scouts-es.org>
 * @package HTML
 * @access public
 * @see HTML, config
 * depends on PHPLib db and auth classes
 * TODO: language configurability -> class variable and translation function
 * TODO: documentation
 */

class Navigation {
   /**
     * 
     * @var  string
     */
    var $string;
   /**
     * 
     * @var  string
     */
    var $link;
   /**
     *
     * @var  string
     */
    var $httpGetArray;
   /**
     * 
     * @var  string
     */
    var $permisions;
   /**
     * 
     * @var  string
     */
    var $statistics;
   /**
     * 
     * @var  string
     */
    var $table;
   /**
     * 
     * @var  string
     */
    var $where;
   /**
     * 
     * @var  string
     */
    var $additionalBR;
   /**
     * 
     * @var  boolean
     */
    var $requiredAuth;
   /**
     * 
     * @var  string
     */
    var $extension = '.php';

    /**
     * Constructor
     *
     * @param   string  $string          String that will be shown
     * @param   string  $link            Page that is linked
     * @access  public
     */
    function Navigation($string, $link)
    {
        $this->string = $string;
	$this->link = $link.$this->extension;
	$this->httpGetArray = '';
	$this->permisions = '';
	$this->statistics = 0;
	$this->where = '';
	$this->additionalBR = 0;
	$this->requiredAuth = 'initialization';
    }

    function setHttpGetArray($array) {
        $this->httpGetArray = $array; 
    }

    function setPermisions($perm) {
        $this->permisions = $perm;
    }

    function additionalBR() {
        $this->additionalBR = 1;
    }

    function setStatistics($table, $where = '') {
        $this->statistics = 1;
        $this->table = $table;
        if ($where) {
            $this->where = " WHERE ".$where;
	} else {
  	    $where = '';
	}
    }

    function showIfAuth($value) {
        $this->requiredAuth = $value;
    }

    function checkPermision() {
        global $auth, $logout;

        if (isset($auth) && !$this->requiredAuth && !$logout) {
	    return 0;
	} elseif (!isset($auth) && $this->requiredAuth == 1) {
  	    return 0;
	} elseif (isset($auth) && $this->requriredAuth == 1 && $logout) {
  	    return 0;
	} elseif ($this->permisions) {
            /* Should not be ==... instead regexp */
            if ($this->permisions == $auth->auth["perm"]) {
  	        return 1;
            } else {
	      return 0;
	    }
        } else {
   	    return 1;
	}
    }

    function countStatistics() {
        global $db;

        $db->query("SELECT COUNT(*) FROM ".$this->table.$this->where);
        $db->next_record();
        return $db->f('COUNT(*)');
    }

    function render() {
        global $auth;

        if ($this->checkPermision()) {
  	    $return = '      <font face="sans-serif"><small>';
	    $return .= html_link($this->string, $this->link, $this->httpGetArray, 'menu-dcho');
            if ($this->statistics) {
  	        $return .= ' ['.$this->countStatistics().']';
	    }
	    $return .= '</small></font><br>';
	    if ($this->additionalBR) {
	        $return .= '<br>';
	    }
            $return .= "\n";
        }
        return $return;
    }
}
?>