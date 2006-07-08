


<?php
	require('../../include/config.inc.php');
	//Set these varibles for your comments database and table.

	/* vim: set expandtab tabstop=4 shiftwidth=4: */
	// +----------------------------------------------------------------------+
	// |                                                                      |
	// +----------------------------------------------------------------------+
	// |       Copyright (c) 2003 Gregorio Robles.    All rights reserved     |
	// |       Copyright (c) 2005 Jorge Gascon Perez. All rights reserved     |
	// +----------------------------------------------------------------------+
	// | This program is free software. You can redistribute it and/or modify |
	// | it under the terms of the GNU General Public License as published by |
	// | the Free Software Foundation; either version 2 or later of the GPL.  |
	// +----------------------------------------------------------------------+
	// | Authors: Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
	// |          Jorge Gascon Perez <jgascon@gsyc.escet.urjc.es>             |
	// +----------------------------------------------------------------------+
	//
	// $Id: Post_New_Comment.php,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $
	
	//Version: 0.01 



	//This variable stores html generadet content.
	$html_Content =	"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">".
			"<html>".
			"<head>".
			"<title>Adding a comment</title>".
			"<meta http-equiv=\"REFRESH\" content=\"2;url=../../index.php?menu=Comments\">".
			"</head>".
			"<BODY>".
			"<br><br><br><br><br><br><br>";


	$email   = $_POST["email"];
	$title   = $_POST["title"];
	$comment = $_POST["comment"];

	//First: We analyze input data and if the data is correct (we want to avoid SQL injection!!!) 

	if ($title && $comment){	
		//If data is correct we build an insert query and insert the data in our database.
		$enlace = mysql_connect($Comments_Host, $Comments_User, $Comments_Password) or die ("Connection failed : " . mysql_error());
		
		//Our Insert query for a new comment.
		$consulta  = "INSERT INTO ".$Comments_Database.".".$Comments_Table.
				" (email, title, comment, date_posted, time_posted) ".
				" VALUES ('".$email."','".$title."','".$comment."', CURDATE(), CURTIME())";

		
		$resultado = mysql_query($consulta, $enlace) or die ("Insert failed : ".mysql_error());	
		mysql_close($enlace);	

		$html_Content .=	"<center><h1>Creating a new comment, please be patient.</h1><br><br>".
					"<img src=\"../../images/clock.gif\"></center>".
					"</BODY>".
					"</HTML>";
	}
	else
	{
		$html_Content .=	"<center><h1><font color=\"red\">".
						"I'm Sorry, but this is an incorrect or incomplete comment.".
					"</font></h1><br><br>".
					"<img src=\"../../images/clock.gif\"></center>".
					"</BODY>".
					"</HTML>";
	}

	echo $html_Content;

?>
