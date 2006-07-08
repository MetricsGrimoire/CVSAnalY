<?php
/* vim: set expandtab tabstop=4 shiftwidth=4: */
// +----------------------------------------------------------------------+
// |        SourceWell 2 - The GPL Software Announcement System           |
// +----------------------------------------------------------------------+
// |      Copyright (c) 2001-2002 BerliOS, FOKUS Fraunhofer Institut      |
// +----------------------------------------------------------------------+
// | This program is free software. You can redistribute it and/or modify |
// | it under the terms of the GNU General Public License as published by |
// | the Free Software Foundation; either version 2 or later of the GPL.  |
// +----------------------------------------------------------------------+
// | Authors: Gregorio Robles <grex@scouts-es.org>                        |
// |          Lutz Henckel <lutz.henckel@fokus.fhg.de>                    |
// |          Carlos Martín Ugalde <carlos@scouts-es.org>                 |
// +----------------------------------------------------------------------+
//
// $Id: html.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * HTML library for PHP (and PHPLib)
 *
 * This library allows to obtain clean PHP code without much HTML
 * It has been thought to work with PHPLib whithout problem
 * 
 * The only two functions that have PHPLib characteristics (session queries) are:
 *      html_link
 *      html_form_action
 *
 * For any function we will have two types
 *	One that returns a string (html_*)
 *	another one that prints a string (htmlp_*)
 *
 * @author Gregorio Robles <grex@scouts-es.org>
 * @package HTML
 * @access public
 * @see Table
 */

/**
 * HTML link abstraction
 *
 * @param   string  $text      Link label
 * @param   string  $target    Target file (blank or 'PHP_SELF' if it is the current one)
 * @param   array   $query     PHPLib session array for variables passes through HTTP GET
 *                             for insntace: array('id' => 3, 'show' => 'yes')
 * @param   string  $cssClass  Class of CSS this link will have
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 * see PHPLib
 */

function html_link($text, $target = 'PHP_SELF', $query = '', $cssClass = '')
{

    if ($target == 'PHP_SELF') {
        if (is_array($query) && !isset($query) || empty($query)) {
            $output = '<a href="'.$PHP_SELF.'" class="'.$cssClass.'">'.$text.'</a>';
        } else {
            $output = '<a href="'.$PHP_SELF._add_query($query).'" class="'.$cssClass.'">'.$text.'</a>';
        }
    } else {
        if (is_array($query) && !isset($query) || empty($query)) {
            $output = '<a href="'.$target.'" class="'.$cssClass.'">'.$text.'</a>';
        } else {
            $output = '<a href="'.$target._add_query($query).'" class="'.$cssClass.'">'.$text.'</a>';
        }
    }
    return($output);
}

function htmlp_link($target, $query = '', $text, $cssClass = '')
{
    print html_link($target, $query, $text, $cssClass);
}

/**
 * HTML anchor abstraction
 *
 * @param   string  $name      Anchor name
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */

function html_anchor($name)
{
    $output = '<a name="'.$name.'"></a>'."\n";
    return($output);
}

function htmlp_anchor($name)
{
    print html_anchor($name);
}

/**
 * HTML image abstraction
 *
 * @param   string  $file         Image file
 * @param   string  $description  Alternate text that is shown for non-graphical browsers
 * @param   int     $width        Image width
 * @param   int     $height       Image height
 * @param   int     $border       Border width
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_image($file, $description,  $width= '', $height= '', $border ='0')
{
    if (!isset($width) || empty($width)) {
	if (!isset($height) || empty($height)) {
	    $output = '<img src="'.$file.'" border="'.$border.'" alt="'.$description.'">';
	} else {
	    $output = '<img src="'.$file.'" border="'.$border.'" height="'.$height.'" alt="'.$description.'">';
        }
    } else {
        if (!isset($height) || empty($height)) {
	    $output = '<img src="'.$file.'" border="'.$border.'" width="'.$width.'" alt="'.$description.'">';
        } else {
	    $output = '<img src="'.$file.'" border="'.$border.'" width="'.$width.'" height="'.$height.'" alt="'.$description.'">';
	}
    }
    return($output);
}

function htmlp_image($file, $description = '', $width = '', $height = '', $border = '')
{
    print html_image($file, $description, $width, $height, $border);
}

/**
 * HTML Form: action
 *
 * @param   string  $target    Target file (blank or 'PHP_SELF' if it is the current one)
 * @param   array   $query     PHPLib session array for variables passes through HTTP GET
 *                             for insntace: array('id' => 3, 'show' => 'yes')
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 * @see PHPLib
 */

function html_form_action($target = 'PHP_SELF', $query = '', $method = 'post')
{

    /* TODO: has to be finished */
    /* 4 different cases
     * a) Target PHP_SELF and a given query
     * b) Target PHP_SELF, query not given
     * c) Other target, given query
     * d) Other target, query not given */

    if ($target == 'PHP_SELF') {
        if (is_array($query)) {
           $output = "\n".'<form action="'.$PHP_SELF._add_query($query).'" method="'.$method.'">';
        } else {
           $output = "\n".'<form action="'.$PHP_SELF.'" method="'.$method.'">';
        }
    } else {
        if (is_array($query)) {
           $output = "\n".'<form action="'.$target._add_query($query).'" method="'.$method.'">';
        } else {
           $output = "\n".'<form action="'.$target.'" method="'.$method.'">';
        }
    }         
    return($output);
}

function htmlp_form_action($file = 'PHP_SELF', $query = '', $method='post')
{
    print html_form_action($file, $query, $method);
}

/**
 * HTML Form: hidden field
 *
 * @param   string  $name    Name of the variable
 * @param   string  $value   Value of the variable
 * @return string/void       depending whether it is the htmlp or html function
 * @access public
 */
	
function html_form_hidden($name, $value)
{
    $output = "\n".'   <input type="hidden" name="'.$name.'" value="'.$value.'">';
    return($output);
}

function htmlp_form_hidden($name, $value)
{
    print html_form_hidden($name, $value);
}

/**
 * HTML Form: starting select choice
 *
 * @param   string  $name      Name of the variable
 * @param   boolean $multiple  If its a multiple select or not
 * @param   int     $size      If multiple, size of the select box
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */

function html_form_select($name, $multiple = 0, $size = 1)
{
    $output = "\n".'   <select name="'.$name.'" size="'.$size.'"';
    if ($multiple) {
        $output .= ' multiple';
    }
    $output .= ">\n";
    return($output);
}

function htmlp_form_select($name, $multiple = 0, $size = 1)
{
    print html_form_select($name, $multiple, $size);
}

/**
 * HTML Form: select option
 *
 * @param   string  $value     Value (that will be passed as form)
 * @param   boolean $selected  If this options is the selected one or not
 * @param   string  $text      Text that will be displayed
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */
	
function html_form_select_option($value, $selected, $text)
{
    $output = "\n".'      <option ';
    if ($selected) {
        $output .= 'selected ';
    }
    $output .= 'value="'.$value.'">'.$text."\n";
    return($output);
}

function htmlp_form_select_option($value, $selected, $text)
{
    print html_form_select_option($value, $selected, $text);
}

/**
 * HTML Form: end select choice
 *
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */

function html_form_select_end()
{
    $output = "\n   </select>\n";
    return($output);
}

function htmlp_form_select_end()
{
    print html_form_select_end();
}

/**
 * HTML Form: text field
 *
 * @param   string  $name      Name of the variable that will be passed
 * @param   string  $value     Default value
 * @param   int     $size      Text field length that will be displayed
 * @param   int     $maxlenght Maximal input
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */

function html_form_textField($name, $value, $size = 24, $maxlength = 128)
{
    $output = "\n".'   <input type="text" name="'.$name.'" size="'.$size.'" maxlength="'.$maxlength.'" value="'.$value.'">';
    return($output);
}

function htmlp_form_textField($name, $value, $size= 24, $maxlength = 128)
{
    print html_form_textField($name, $value, $size, $maxlength);
}

/**
 * HTML Form: password field
 *
 * @param   string  $name      Name of the variable that will be passed
 * @param   int     $size      Text field length that will be displayed
 * @param   int     $maxlenght Maximal input
 * @param   string  $value     Default value
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */

function html_form_PassWordField($name, $size = 16, $maxlength = 32, $value='')
{
    $output = "\n".'   <input type="password" name="'.$name.'" size="'.$size.'" maxlength="'.$maxlength.'" value="'.$value.'">';
    return($output);
}

function htmlp_form_PassWordField($name, $size = 16, $maxlength = 32, $value='')
{
    print html_form_campo_PassWordField($name, $size, $maxlength, $value);
}

/**
 * HTML Form: submit button
 *
 * @param   string  $value     Button label
 * @param   string  $name      Name of the variable that will be passed (not strictly needed)
 * @return string/void         depending whether it is the htmlp or html function
 * @access public
 */

function html_form_submit($value, $name='')
{
    if ($name) {
        $output = "\n".'   <input type="submit" value="'.$value.'"  name="'.$name.'">';
    } else {
        $output = "\n".'   <input type="submit" value="'.$value.'">';        
    }
    return($output);
}

function htmlp_form_submit($value, $name ='')
{
    print html_form_submit($value, $name);
}

/**
 * HTML Form: image as submit button
 *
 * @param   string  $file         path to the image
 * @param   string  $description  alternate text for non-graphical browsers
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_image($file, $description)
{
    $output = "\n".'   <input type="image" src="'.$file.'" alt="'.$description.'">';
    return($output);
}

function htmlp_form_image($file, $description)
{
    print html_form_image($file, $description);
}

/**
 * HTML Form: reset button
 *
 * @param   string  $value        label for the button
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_reset($value = 'Reset')
{
    $output = "\n".'   <input type="reset" value="'.$value.'">';
    return($output);
}

function htmlp_form_reset($value = 'Reset')
{
    print html_form_reset($value);
}

/**
 * HTML Form: check button
 *
 * @param   string  $name         name of the checkbox
 * @param   string  $value        value of the checkbox
 * @param   int     $selected     Whether this option is selected or not
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_checkBox($name, $value, $selected)
{
    $output = "\n".'   <input type="checkbox" name="'.$name.'" value="'.$value.'"';
    if ($selected) {
        $output .= ' checked ';
    }
    $output .= '>';
    return($output);
}

function htmlp_form_checkBox($name, $value, $selected)
{
    print html_form_checkBox($name, $value, $selected);
}

/**
 * HTML Form: radio button
 *
 * @param   string  $name         name of the radio button
 * @param   string  $value        value of the radio button
 * @param   int     $selected     Whether this option is selected or not
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_radioButton($name, $value, $selected)
{
    $output = "\n".'   <input type="radio" name="'.$name.'" value="'.$value.'"';
    if ($selected) {
        $output .= ' checked ';
    }
    $output .= '>';
    return($output);
}

function htmlp_form_radioButton($name, $value, $selected)
{
    print html_form_circular($name, $value, $selected);
}

/**
 * HTML Form: Text area
 *
 * @param   string  $name         name of the variable
 * @param   string  $value        default value
 * @param   int     $columns      Number of columns
 * @param   int     $rows         Number of rows
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_textArea($name, $value, $columns = 40, $rows =7)
{
    $output = "\n".'   <textarea name="'.$name.'" cols="'.$columns.'" rows="'.$rows.'">'.$value.'</textarea>';
    return($output);
}

function htmlp_form_textArea($name, $value, $columns = 40, $rows =7)
{
    print html_form_areatext($name, $value, $columns, $rows);
}

/**
 * HTML Form: end tag
 *
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_end()
{
    $output = "\n</form>";
    return($output);
}

function htmlp_form_end()
{
    print html_form_end();
}

/**
 * HTML Form: File Upload
 *
 * @param   string  $name         path of the file (FIXME: is that correct?)
 * @return string/void            depending whether it is the htmlp or html function
 * @access public
 */

function html_form_file($name)
{
    $output = "\n".'   <input type="file" name="'.$name.'">';
    return($output);
}

function htmlp_form_file($name)
{
    print html_form_file($name);
}

function _add_query($qarray) {
    global $PHP_SELF;
    global $QUERY_STRING;

			// fix no.1: Gregorio Robles <grex@scouts-es.org>
			// We want to start always with a "clean"
			// query url string!!!!
    $QUERY_STRING = "";
			// end fix

    if ((isset($QUERY_STRING) && ("" != $QUERY_STRING))) {
        $sep_char = "&amp;";
    } else {
        $sep_char = "?";
    }

    $qstring = "";
    while (list($k, $v) = each($qarray)) {

				// Fix no. 2 for SourceWell
				// when iter from show_more function
				// then do not print a question mark
      if ($k == "iter") $sep_char = "&amp;";
      $v = ereg_replace("%20", " ", $v); 
				// end fix no. 2 Grex

        $qstring .= $sep_char . urlencode($k) . "=" . urlencode($v);
        $sep_char = "&amp;";
    }

    return $qstring;
}

?>
