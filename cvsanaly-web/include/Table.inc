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
// |          Gregorio Robles <grex@scouts-es.org>                        |
// |          Carlos Martín Ugalde <carlos@scouts-es.org>                 |
// +----------------------------------------------------------------------+
//
// $Id: Table.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * Class Table: a class for HTML Tables
 *
 * This library contains an object oriented vision of the HTML tables.
 * Its use allows to abstract the PHP from the HTML
 *
 * With this class, you should be able of doing something like this:
 *
 * +------------------------------------------------+
 * | Title                                          |
 * +------------------------------------------------+
 * | Body                                           |
 * |                                                |
 * |                                                |
 * +------------------------------------------------+
 *
 * or even like this:
 *
 * +------------------------------------------------+
 * | Title                                          |
 * +------------------------------------------------+
 * | Body                                           |
 * |                                                |
 * | +-------------++--------------++-------------+ |
 * | |  Column     ||  Column      ||  Column     | |
 * | +-------------++--------------++-------------+ |
 * | |  Column     ||  Column      ||  Column     | |
 * | +-------------++--------------++-------------+ |
 * | |  Spanned column             ||  Column     | |
 * | +-----------------------------++-------------+ |
 * +------------------------------------------------+
 *
 * Title, Body, Column and Spanned Column are contents
 * (in string format) you may want to put in there
 *
 * This class handles primarily visual aspects of the table,
 * while it provides an interface to introduce its contents
 * Visual configuration is done through config.inc
 *
 * @author Lutz Henckel <lutz.henckel@fokus.fhg.de>
 * @author Gregorio Robles <grex@scouts-es.org>
 * @author Carlos Martín Ugalde <carlos@scouts-es.org>
 * @package HTML
 * @access public
 * @see HTML
 * TODO: language configurability -> class variable and translation function
 */

class Table {

   /**
     * Width of the table (IE has problems with 100% widths!) 
     * @var  string
     */
    var $table_width;
   /**
     * 
     * @var  string
     */
    var $table_filling;
   /**
     * Background color of the Title
     * @var  string
     */
    var $table_title_bgcolor;
   /**
     * Font Color of the Title
     * @var  string
     */
    var $table_title_font_color;
   /**
     * Align of the Title
     * @var  string
     */
    var $table_title_align;
   /**
     * Background color of the Body
     * @var  string
     */
    var $table_body_bgcolor;
   /**
     * Font color of the body
     * @var  string
     */
    var $table_body_font_color;
   /**
     * Align of the Body
     * @var  string
     */
    var $table_body_align;

    /**
     * Constructor
     *
     * @param   string  $table_type      can be 'general' or 'error'
     * @param   string  $table_width     can be xx% or in pixels
     * @access  public
     * @global  string  $config_table_*  Configuration parameters (see config.inc file)
     */
    function Table($table_type ='general', $table_width='98%')
    {
        /* Configuration parameters for the general table */
        global $config_table_general_filling;
        global $config_table_general_title_bgcolor;
        global $config_table_general_title_font_color;
        global $config_table_general_title_align;
        global $config_table_general_body_bgcolor;
        global $config_table_general_body_font_color;
        global $config_table_general_body_align;
	/* Configuration parameters for an error table */
        global $config_table_error_filling;
        global $config_table_error_title_bgcolor;
        global $config_table_error_title_font_color;
        global $config_table_error_title_align;
        global $config_table_error_body_bgcolor;
        global $config_table_error_body_font_color;
        global $config_table_error_body_align;

        $this->table_width = $table_width;

        /* depending on the table, we have different parameters */
        /* if we were Object-oriented purists, this should be done
           with inheritance --> TODO */

        switch ($table_type) {

        case 'general':
            $this->table_filling = $config_table_general_filling;
            $this->table_title_bgcolor = $config_table_general_title_bgcolor;
            $this->table_title_font_color = $config_table_general_title_font_color;
            $this->table_title_align = $config_table_general_title_align;
            $this->table_body_bgcolor = $config_table_general_body_bgcolor;
            $this->table_body_font_color = $config_table_general_body_font_color;
            $this->table_body_align = $config_table_general_body_align;
            break;

        case 'error':
            $this->table_filling = $config_table_error_filling;
            $this->table_title_bgcolor = $config_table_error_title_bgcolor;
            $this->table_title_font_color = $config_table_error_title_font_color;
            $this->table_title_align = $config_table_error_title_align;
            $this->table_body_bgcolor = $config_table_error_body_bgcolor;
            $this->table_body_font_color = $config_table_error_body_font_color;
            $this->table_body_align = $config_table_error_body_align;
            break;
        }
        /* Internet Explorer does not work ok when we put the width
           of the tables to 100%
           If we have a width that is greater than 98% we set it to 98% */

        if (substr($this->table_width,0,strpos($this->table_width, '%')) > 98) {
            $this->table_width = '98%';
        }        
    }

    /**
     * Prints the beginning tags for a table
     *
     * @param    string       $summary   table summary as specified in HTML 4
     * @access public
     */
  
    function table_begin($summary = '')
    {
       echo "\n<!-- Table Begins -->\n";
       echo '<table style="border: 0; padding: '.$this->table_filling.'; width: '.$this->table_width.';" align="center">'."\n";
    }

    /**
     * Prints the end tags for a table
     *
     * @access public
     */

    function table_end()
    {
        echo "</table>\n";
        echo "<!-- Table ends -->\n";
        echo "<br>\n";
    }

    /**
     * Prints the beginning tags for the table title
     *
     * @access public
     */

    function table_title_begin()
    {
        echo "   <!-- Table title begins -->\n";
        echo "   <tr style=\"background: $this->table_title_bgcolor\">\n";
        echo "      <td style=\"text-align: $this->table_title_align; color: $this->table_title_font_color\">\n";
    }

    /**
     * Prints the end tags for the table title
     *
     * @access public
     */

    function table_title_end()
    {
        echo "      </td>\n";
        echo "   </tr>\n";
        echo "   <!-- Table title ends -->\n";
    }

    /**
     * Prints the title
     * It is the same as calling (but in one function):
     *       table_title_begin()
     *       echo $text;
     *       table_title_end()
     *
     * @param    string      $title     Text that will be the title
     * @access public
     */

    function table_title($title = '&nbsp;')
    {
        $this->table_title_begin();
        echo "      <b>$title</b>\n";
        $this->table_title_end();
    }

    /**
     * Prints the beginning tags for the table body
     *
     * @param      string      $valign      Vertical align of the body
     * @access public
     */

    function table_body_begin($valign = 'top')
    {
        echo "   <!-- Table body begins -->\n";
        echo "   <tr style=\"background: $this->table_body_bgcolor\">\n";
        echo "      <td style=\"text-align: $this->table_body_align; color: $this->table_body_font_color\" valign=\"$valign\">\n";
    }

    /**
     * Prints the end tags for the table body
     *
     * @access public
     */

    function table_body_end()
    {
        echo "      </td>\n";
        echo "   </tr>\n";
        echo "   <!-- End Table body -->\n";
    }

    /**
     * Prints the body
     * It is the same as calling (but in one function):
     *       table_body_begin()
     *       echo $text;
     *       table_body_end()
     *
     * @param    string      $text     Text that will be in the body
     * @param    string      $valign   Vertical align of the body
     * @access public
     */

    function table_body($text = '&nbsp;', $valign = 'top')
    {
        $this->table_body_begin($valign);
        echo "    ".$text."\n";
        $this->table_body_end();
    }

    /**
     * Prints a full box (title + body)
     * It is the same as calling (but in one function):
     *       table_title($title)
     *       table_body($text, $valign)
     *
     * @param    string      $title    Text that will be the title of the table
     * @param    string      $text     Text that will be in the body
     * @param    string      $valign   Vertical align of the body
     * @param    string      $summary  table summary as specified in HTML 4
     * @access public
     */

    function table_full($title = '&nbsp;', $text ='&nbsp;', $valign = 'top', $summary ='')
    {
        $this->table_begin($summary);
        $this->table_title($title);
        $this->table_body($text, $valign);
        $this->table_end();
    }

    /**
     * Prints the beginning tags for starting row(s) of columns
     *
     * @access public
     */

    function table_columns_begin()
    {
        echo "\n<!-- Table with columns begins -->\n";
        echo "<table style=\"border: 0; padding: $this->table_filling; width: $this->table_width; \" align=\"center\">\n";
        echo "   <tr>\n";
    }


    /**
     * Prints the ending tags for ending row(s) of columns
     *
     * @access public
     */

    function table_columns_end()
    {
        echo "   </tr>\n";
        echo "</table>\n";
        echo "<!-- End Table columns -->\n";
    }

    /**
     * Prints the beginning tags for starting a single columns
     * It is the same as calling (but in one function):
     *
     * @param    string      $width     Column width (best in %)
     * @param    string      $bgcolor   Background color
     * @param    string      $align     Text align
     * @access public
     */

    function table_column_start($width = '100%', $bgcolor = '', $align = 'center')
    {
        echo "\n      <!-- New column starts -->\n";
        echo "      <td align=\"$align\" width=\"$width\" bgcolor=\"$bgcolor\" valign=\"top\">\n";
    }

    /**
     * Prints the ending tags for a single columns
     *
     * @access public
     */

    function table_column_finish()
    {
        echo "      </td>\n";
        echo "      <!-- Column finishes -->\n";
    }

    /**
     * Prints a single columns
     * It is the same as calling (but in one function):
     *       table_column_start($width, $bgcolor, $align)
     *       echo $text;
     *       table_column_finish()
     *
     * Requires to work fine that you put it between:
     *       table_columns_begin()
     *       table_columns_end()
     *
     * @param    string      $text      Text in the column
     * @param    string      $width     Column width (best in %)
     * @param    string      $bgcolor   Background color
     * @param    string      $align     Text align
     * @access public
     */

    function table_column($text = '&nbsp;', $width = '100%', $bgcolor = '', $align = 'center')
    {
        $this->table_column_start($width, $bgcolor, $align);
        echo "    ".$text."\n";
        $this->table_column_finish();
    }

    /**
     * New row of columns
     *
     * It should be used as followed:
     * StartColumns
     * Column1  Column2  nextRowWithColumns
     * Column4  Column5  nextRowWithColumns
     * Column7  Column8
     * EndColumns
     *
     * @access public
     */

    function table_nextRowWithColumns()
    {
        echo "   </tr>\n";
        echo "   <!-- Next row with columns -->\n";
        echo "   <tr>\n";
    }

    /**
     * Joins several columns in one
     *
     * Requires to work fine that you put it between:
     *       table_columns_begin()
     *       table_columns_end()
     *
     * @param    string      $text                 Text in the column
     * @param    int         $numberOfColumns      number of columns being joined
     * @param    string      $width                Column width (best in %)
     * @param    string      $bgcolor              Background color
     * @param    string      $align                Text align
     * @access public
     */
    function table_colspan($text = '&nbsp;', $numberOfColumns ='2', $bgcolor = '', $align = 'center')
    {
        echo "      <!-- Column that extends itself over $numberOfColumns columns columns begins -->\n";
        echo "      <td colspan=\"$numberOfColumns\" align=\"$align\" bgcolor=\"$bgcolor\">\n";
        echo "      ".$text."\n";
        echo "      </td>\n";
        echo "      <!-- End of column that extends itself over  $number_of_columns columns columns -->\n";
    }

    /**
     * This is just a single (usual) table
     * It has no title and body part. It is just a simple strip
     *
     * Example:
     * table_strip('This is a strip');
     * will print out the following:
     *
     * +------------------------------------------------+
     * | This is a strip                                |
     * +------------------------------------------------+
     *
     * The strip takes the $this->table_title_* parameters as the
     * ones to be used (the body parameters are discarded)
     * (in the example, for instance, this->table_title_align is 'left')
     *
     * @param    string      $text                 Text in the column
     * @access public
     */
    function table_strip($text = '$nbsp;', $align = 'right') {
        echo "\n<!-- Table (strip) Begins -->\n";
        echo '<table style="border: 0; padding: '.$this->table_filling.'; width: '.$this->table_width.';" align="center">'."\n";
        echo "   <tr style=\"background: $this->table_title_bgcolor\">\n";
        echo "      <td style=\"text-align: $align; color: $this->table_title_font_color\">\n";
        echo $text;
        echo "      </td>\n";
        echo "   </tr>\n";
        echo "</table>\n";
        echo "<!-- Table (strip) ends -->\n";
        echo "<br>\n";
    }
}
?>