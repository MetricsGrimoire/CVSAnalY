<?php
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
// +----------------------------------------------------------------------+
//
// $Id: FAQ.inc,v 1.1.1.1 2006/06/08 11:12:04 anavarro Exp $

global $table;

$table->table_full('Frequently Asked Questions', '');

print '<p>';


$table->table_full('What is CVS?', '
CVS is a version control system. Using it, you can record the history of your source files.
<p>For example, bugs sometimes creep in when software is modified, and you might not detect the bug until a long time after you make the modification. With CVS, you can easily retrieve old versions to see exactly which change caused the bug. This can sometimes be a big help.</p>
<p>You could of course save every version of every file you have ever created. This would however waste an enormous amount of disk space. CVS stores all the versions of a file in a single file in a clever way that only stores the differences between versions.</p>
<p>CVS also helps you if you are part of a group of people working on the same project. It is all too easy to overwrite each others\' changes unless you are extremely careful. Some editors, like GNU Emacs, try to make sure that the same file is never modified by two people at the same time. Unfortunately, if someone is using another editor, that safeguard will not work. CVS solves this problem by insulating the different developers from each other. Every developer works in his own directory, and CVS merges the work when each developer is done.</p>
<p>[<i>excerpt from <a href="http://www.loria.fr/~molli/cvs/doc/cvs_1.html#SEC2">Version Management with CVS</a> by Per Cederqvist et al</i>]');

$table->table_full('What is a CVS repository?', '
The CVS repository stores a complete copy of all the files and directories which are under version control.
<p>Normally, you never access any of the files in the repository directly. Instead, you use CVS commands to get your own copy of the files into a working directory, and then work on that copy. When you\'ve finished a set of changes, you check (or commit) them back into the repository. The repository then contains the changes which you have made, as well as recording exactly what you changed, when you changed it, and other such information. Note that the repository is not a subdirectory of the working directory, or vice versa; they should be in separate locations.</p>
<p>[<i>excerpt from <a href="http://www.loria.fr/~molli/cvs/doc/cvs_1.html#SEC9">Version Management with CVS</a> by Per Cederqvist et al</i>]');

$table->table_full('What is a commit?', '
A commit incorporates changes from developer local working source files into the source repository.
<p>[<i>excerpt (with minor modifications) from <a href="http://www.loria.fr/~molli/cvs/doc/cvs_1.html#SEC118">Version Management with CVS</a> by Per Cederqvist et al</i>]');

$table->table_full('What is a commiter?', '
A commiter is the person who does a commit.');

$table->table_full('What is considered as a Line of Code (LOC)?', '');

$table->table_full('What is COCOMO?', '');

$table->table_full('What is the Gini Coefficient?', '');

$table->table_full('What is the Lorenz curve?', '');

$table->table_full('How do I read the generation graphs?', '');

$table->table_full('What are the generations?', '');

$table->table_full('How are the generations computed?', '');


?>
