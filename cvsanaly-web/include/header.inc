<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |                   Libre Software Engineering                         |
// +----------------------------------------------------------------------+
// |                   http://gsyc.escet.urjc.es/                         |
// +----------------------------------------------------------------------+
// |             Copyright (c) 2003 Universidad Rey Juan Carlos           |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors:                                                             |
// |          Gregorio Robles <grex@gsyc.escet.urjc.es>                   |
// +----------------------------------------------------------------------+
//
// $Id: header.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * Header file
 */

?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
		      "http://www.w3.org/tr/REC-html40/loose.dtd">
<html lang="en">
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
   <meta name="Author" content="Gregorio Robles">
   <meta name="Description" content="<?php print $config_meta_description; ?>">
   <meta name="KeyWords" content="<?php print $config_meta_keywords; ?>">
   <link rel="stylesheet" href="estilos.css" type="text/css">
   <link rel="SHORTCUT ICON" href="<?php print $config_shortcut_icon; ?>">
   <!-- HTML Design taken from Grupo Scout Alborada 434: http://asde.scouts-es.net/gs434/ and modified by Gregorio Robles -->

   <title><?php print $config_sys_name." - ".$HTTP_GET_VARS['menu']." - ".$HTTP_GET_VARS[$menu]; ?></title>
</head>

<body>

<table align="center" width="100%" border="0" summary="Header with the title and information about the university where this research is happening">
  <tr>
    <td bgcolor="<?php print $config_color_dark; ?>" align="right"><b><a href="http://libresoft.dat.escet.urjc.es">Libre Software Engineering</a></b></td>
  </tr>
  <tr>
    <td bgcolor="<?php print $config_color_clear; ?>" class="cabecera" style="padding-top: 0px; font-size: 30px"><?php print $config_sys_name; ?></td>
  </tr>
</table>

<table align="center" width="100%" cellspacing="0" cellpadding="0" border="0" summary="main table with two columns: one at the left with the navigation bar and the big box at the right with the contents of the pages">
  <tr>
    <td colspan="5" width="2" bgcolor="<?php print $config_color_line; ?>"></td>
  </tr>
  <tr valign="top">
    <td height="1" bgcolor="<?print $config_color_line; ?>"></td>
    <td bgcolor="<?php print $config_color_clear?>" width="16%">
    <table width="100%" cellspacing="0" cellpadding="0" border="0" summary="Table with the menu bar">
      <tr><td class="cabecera" style="text-align: justify; padding-left: 10px">Contents</td></tr>
      <?php navigation_bar($HTTP_GET_VARS['menu'], $HTTP_GET_VARS[$menu]); ?>
      <tr><td><br>&nbsp;<br>&nbsp;</td></tr>
      <!-- Module Search menu -->
      <tr bgcolor="<?php echo $config_navstrip_bgcolor;?>">
        <td align="center">
          <img src="images/blank.gif" height="1" width="135" border=0 alt="">
          <span class="titlebar"><font color="<?php echo $config_navstrip_font_color;?>">
            <?php echo '<b>Module Search</b>'; ?>
          </font></span>
        </td>
      </tr>
      <tr>
        <td align="center">
          <?php
          htmlp_form_action('search.php', '', 'get');
          htmlp_form_textField('search', '', $size = 10);
          htmlp_form_submit('Go');
          htmlp_form_end();
          ?>
        </td>
      </tr>
<!-- end Search menu -->

<!-- Author Search menu -->
      <tr bgcolor="<?php echo $config_navstrip_bgcolor;?>">
        <td align="center">
          <img src="images/blank.gif" height="1" width="135" border=0 alt="">
          <span class="titlebar"><font color="<?php echo $config_navstrip_font_color;?>">
            <?php echo '<b>Commiter Search</b>'; ?>
          </font></span>
        </td>
      </tr>

      <tr align="right" bgcolor="<?php echo $config_nav_bgcolor;?>">
        <td align="center">
          <?php
          htmlp_form_action('search_auth.php', '', 'get');
          htmlp_form_textField('search', '', $size = 10);
          htmlp_form_submit('Go');
          htmlp_form_end();
          ?>
        </td>
      </tr>
<!-- end Search menu -->

<!-- Language menu -->
      <tr bgcolor="<?php echo $config_navstrip_bgcolor;?>">
        <td align="center"><img src="images/blank.gif" height="1" width="135" border="0" alt="">
          <span class="titlebar"><font color="<?php echo $config_navstrip_font_color;?>">
            <?php echo '<b>Language</b>';?>
          </font></span>
        </td>
      </tr>

      <tr ALIGN=RIGHT bgcolor="<?php echo $config_nav_bgcolor;?>">
        <td align=center>
          <?php
          htmlp_form_action();
          while (is_array($HTTP_GET_VARS) 
                && list($key, $val) = each($HTTP_GET_VARS)) {
            if ($key != "lang" && $key != "go") {
                htmlp_form_hidden($key, $val);
            }
          }
          htmlp_form_select($lang);
          while (list(, $ln) = each($config_la_array)) {
            htmlp_form_select_option($ln, $la, $ln);;
          }
          htmlp_form_select_end();
          htmlp_form_submit('Go');
          htmlp_form_end();
          ?>
        </td>
      </tr>
      <tr><td height="1" bgcolor="<?php print $config_color_clear; ?>"></td></tr>
    </table>
    </td>
    <td height="1" bgcolor="<?php print $config_color_line; ?>"></td>
    <td width="100%">
      <table width="100%" cellspacing="0" cellpadding="0" border="0" summary="Table with the contents">
	<tr>
	  <td valign="top">
            <br>
           <!------------------------------------------------>
           <!--           Principio pagina datos           -->
           <!------------------------------------------------>
