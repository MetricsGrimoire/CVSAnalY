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
// $Id: footer.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $

/**
 * Footer file
 */

?>

           <!------------------------------------------------>
           <!--              Fin página datos              -->
           <!------------------------------------------------>
           <br>
	  </td>
        </tr>
      </table>
      </td>
      <td height="1" bgcolor="<?php print $config_color_line; ?>"></td>
    </tr>
    <tr><td colspan="5" width="1" bgcolor="<?php print $config_color_line; ?>"></td></tr>
    <tr><td colspan="5" height="2" bgcolor="#FFFFFF"></td></tr>
    <tr><td colspan="5" width="1" bgcolor="<?php print $config_color_line; ?>"></td></tr>
    <tr>
      <td height="1" bgcolor="#17891A"></td>
      <td colspan="3" height="5" bgcolor="<?php print $config_color_dark; ?>"></td>
      <td height="1" bgcolor="#17891A"></td>
    </tr>
    <tr><td colspan="5" width="1" bgcolor="<?php print $config_color_line; ?>"></td></tr>
    <tr><td colspan="5" height="2" bgcolor="#FFFFFF"></td></tr>
    <tr><td colspan="5" width="1" bgcolor="<?php print $config_color_line; ?>"></td></tr>
    <tr>
      <td height="50" bgcolor="#17891A"></td>
      <td colspan="3" bgcolor="#FFFFFF" align="center">
	<table width="100%" border="0" summary="Table with images and validation links">
	  <tr>
	    <td align="center" width="27%">
 	      <a href="http://gsyc.escet.urjc.es/"><img src="images/gsyc.png" border="0" alt="GSyC"></a>
	    </td>
	    <td align="center" width="34%">
              <div style=" font: 10px Arial; margin-bottom: 5px"><a href="http://libresoft.dat.escet.urjc.es/cvsanal/mono-cvs/index.php?menu=Credits#copyright">&copy;</a> 2003 Grupo de Sistemas y Comunicaciones<br>Universidad Rey Juan Carlos<br>M&oacute;stoles, Madrid, Spain<br></div>
	    </td>
            <td align="right" width="39%">
 	      <a href="http://validator.w3.org/check/referer"><img src="images/valid-html40" border="0" alt="Valid HTML 4.01"></a> | 
 	      <a href="http://jigsaw.w3.org/css-validator"><img src="images/vcss.png" border="0" alt="Valid CSS!"></a> | 
	      <a href="http://www.tawdis.net/servlets/taw?url=<?php print $GLOBALS['config_sys_url'].$GLOBALS['PHP_SELF']; ?>"><img border="0" width="88" height="31" src="images/wcag1AA.gif" alt="AA Accesibility"></a>
            </td>
          </tr>
	</table>
     </td>
     <td height="50" bgcolor="<?php print $config_color_line; ?>"></td>
   <tr><td colspan="5" width="1" bgcolor="<?php print $config_color_line; ?>"></td></tr>
</table>

</body>
</html>

