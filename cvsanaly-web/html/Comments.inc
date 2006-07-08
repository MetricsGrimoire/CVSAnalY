


 


<style type="text/css">
table.sample {
 border-width: 3px 3px 3px 3px;
 border-spacing: ;
 border-style: solid solid solid solid;
 border-color: blue blue blue blue;
 border-collapse: separate;
 background-color: white;
}
table.sample th {
 border-width: 1px 1px 1px 1px;
 padding: 1px 1px 1px 1px;
 border-style: none none none none;
 border-color: white white white white;
 background-color: white;
 -moz-border-radius: ;
}
table.sample td {
 border-width: 1px 1px 1px 1px;
 padding: 1px 1px 1px 1px;
 border-style: none none none none;
 border-color: white white white white;
 background-color: white;
 -moz-border-radius: ;
}
</style>







<?php

	//Set these varibles for your comments database and table.
	require('include/config.inc.php');

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
	// |          Jorge Gascon Perez <jgascon@gsyc.escet.urjc.es>             |
	// +----------------------------------------------------------------------+
	//
	// $Id: Comments.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $
	
	//Version: 0.01 

	function Show_All_Comments ($Conection='', $Database='', $Table='') {

		//This variable will contain all html content generated.
		$html = "";

		//Next Mysl query is used to obtain all comments.
		$consulta  = "SELECT email, title, comment, date_posted, time_posted ".
				"FROM ".$Database.".".$Table.
				" ORDER BY date_posted, time_posted DESC";

		$resultado = mysql_query($consulta, $Conection) or die("Query failed : ".mysql_error());
				
		//Despues para cada una de las filas se elabora un comentario en forma de tabla.
		while ($linea = mysql_fetch_array($resultado, MYSQL_ASSOC)) {
		
			//Every comment has three tables:

			//First table: A blue rounded square with the comment title.
			$html .= "<table class=\"sample\" width=\"90%\" align=\"center\">";
			$html .= "<tr>";
			$html .= "<td bordercolor=\"white\" colspan=\"3\"><h3><font color=\"blue\">".$linea["title"]."</font></h3></td>";
			$html .= "</tr>";
			$html .= "</table><br>";

			//Second table: the author of the comment and the date and time, the table has not border.
			$html .= "<table border=\"0\" width=\"90%\" align=\"center\">";
			$html .= "<tr><td>Posted by  ";
						if ($linea["email"])	$html .= $linea["email"];
						else 			$html .= "Anonimous";
			$html .= "</td>";
			$html .= "<td>On:  ".$linea["date_posted"]." - ".$linea["time_posted"]."</td>";
			$html .= "</tr></table>";


			//Third table: A white square with the comment.
			$html .= "<table border=\"0\" width=\"90%\" align=\"center\">";
			$html .= "<tr><td colspan=\"3\"><h3> ".$linea["comment"]."</h3></td></tr>";
			$html .= "</table><br><br><br>";

		};
		return $html;
	};







	//Main Code:


	//Next variable will store all generated html content:
	$Content_Html = "<a name=\"top\"/>".
			"<center><h2>Help us to improve CvsAnaly</h2>".
			"<a href=\"#Post_Comment\">".
				"<h4><font color=\"blue\">Post a Comment</font></h4>".
			"</a></center>".
			"<br><br><br><br>";
	
	//Primero se hace una consulta Sql a la tabla de comments ordenada por fechas (la mas moderna primero)
	$enlace = mysql_connect($Comments_Host, $Comments_User, $Comments_Password)  or die ("Connection failed : " . mysql_error());
	
	//We show all comments posted
	$Content_Html .= Show_All_Comments ($enlace, $Comments_Database, $Comments_Table);


	//Database Conection is closed.
	mysql_close($enlace);


	//A Post Comment FORM is added.

	$Content_Html .=  
		        //"<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>".
			//"<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>".
			"<form method=\"POST\" action=\"html/Comments/Post_New_Comment.php\">".

			"<a name=\"Post_Comment\">".

			"<table class=\"sample\" width=\"70%\" align=\"center\">".
			"<tr>".
				"<td colspan=\"3\">".
					"<center><h3>Post a Comment</h3></center>".
				"</td>".
			"</tr></table>".


			"<table style=\"width: 70%; text-align: left; margin-left: auto; margin-right: auto;\"".
			" border=\"0\" cellpadding=\"2\" cellspacing=\"2\">".
			"<tbody>".
			"    <tr>".
			"      <td style=\"height: 70%; text-align: center; vertical-align: middle; width: 423px;\"></td>".
			"      <td style=\"width: 194px;\"></td>".
			"    </tr>".
			"    <tr>".
			"      <td style=\"width: 240px;\"><h3>E-Mail (Optional)</h3></td>".
			"      <td style=\"width: 423px;\"><input type=\"text\" name=\"email\"/></td>".
			"      <td style=\"width: 194px;\"></td>".
			"    </tr>".
			"    <tr>".
			"      <td style=\"width: 240px;\"><h3>Title</h3></td>".
			"      <td style=\"width: 423px;\"><input type=\"text\" name=\"title\"/></td>".
			"      <td style=\"width: 194px;\"></td>".
			"    </tr>".
			"    <tr>".
			"      <td style=\"width: 240px;\"><h3>Comment Description</h3></td>".
			"      <td style=\"width: 423px;\"><textarea cols=\"60\" rows=\"8\" name=\"comment\"/></textarea></td>".
			"      <td style=\"width: 194px;\"></td>".
			"    </tr>".
			"    <tr>".
			"      <td colspan=\"3\" style=\"text-align: center;\">".
					"<center><input type=\"submit\" /></center>".
			"      </td>".
			"    </tr>".
			"    <tr>".
			"      <td colspan=\"3\" style=\"text-align: center;\">".
					"<center>&nbsp;Note: We don't resposibility about posted comments.</center>".
			"      </td>".
			"    </tr>".
			"  </tbody>".
			"</table>".
			"</form>".
			"<center><a href=\"#top\"><h4><font color=\"blue\">Back</font></h4></a></center>".
			"<br>";

	//Se muestra todo el contenido html generado
	echo $Content_Html;

?>

