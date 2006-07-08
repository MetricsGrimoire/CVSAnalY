<?php
/*
 * Session Management for PHP3
 *
 * Copyright (c) 1998-2000 NetUSE AG
 *                    Boris Erdmann, Kristian Koehntopp
 *
 * $Id: local.inc,v 1.1.1.1 2006/06/08 11:12:03 anavarro Exp $
 *
 */ 

######################################################################
# SourceWell Database Configuration
#
# For using SourceWell, you only have to fill in the appropriate
# parameters that fit your database
#
# The default (and recommended) configuration is the one with
# 'sourcewell' as the database name. Do better not change it ;-)
#
######################################################################

class DB_SourceWell extends DB_Sql {
    var $Host     = '';
    var $Database = '';
    var $User     = 'operator';
    var $Password = 'password';
}

/*********************************************************************/
/* If you've finished configuring the Database, you can login as an  */
/* administrator. To do so, just launch your web browser pointing to */
/* http://yourdomain.com/login.php3 and login as the default admin   */
/* with user,editor,admin permissions.                               */
/*                                                                   */
/* At the prompt use the following ID to login (case sensitive):     */
/*                                                                   */
/*         Username: oldfish                                         */
/*         Password: oldfish                                         */
/*                                                                   */
/* Vert important:                                                   */
/* Be sure of inmediately changing the login & password by clicking  */
/* on User Admin. You'll notice this is quite easy to do ;-)         */
/*								     */
/*               Thanks for having chosen SourceWell                 */
/*********************************************************************/


######################################################################
# SourceWell Advanced Database Configuration
#
# If you've chosen 'sourcewell' as your database name, you don't
# need to worry about the rest of the file ;-)
#
# If you've chosen another database name, you'll have to change this
# file and config.inc in the pint 'Database Name Config'.
######################################################################

class SourceWell_CT_Sql extends CT_Sql {
    var $database_class = 'DB_SourceWell';   ## Which database to connect...
    var $database_table = 'active_sessions'; ## and find our session data in this table.
}

class SourceWell_Session extends Session {
  var $classname = 'SourceWell_Session';

  var $cookiename     = '';                ## defaults to classname
  var $magic          = 'Hocuspocus';      ## ID seed
  var $mode           = 'cookie';          ## We propagate session IDs with cookies
#  var $mode = 'get';
  var $fallback_mode  = 'get';
  var $lifetime       = 0;                 ## 0 = do session cookies, else minutes
  var $that_class     = 'SourceWell_CT_Sql'; ## name of data storage container
  var $gc_probability = 5;  
}

class SourceWell_User extends User {
  var $classname = 'SourceWell_User';

  var $magic          = 'Abracadabra';     ## ID seed
  var $that_class     = 'SourceWell_CT_Sql'; ## data storage container
}

class SourceWell_Auth extends Auth {
  var $classname      = 'SourceWell_Auth';

  var $lifetime       =  30;

  var $database_class = 'DB_SourceWell';
  var $database_table = 'auth_user';
  
  function auth_loginform() {
    global $sess;
    global $_PHPLIB;

    include('loginform.ihtml');
  }
  
  function auth_validatelogin() {
    global $username, $password;

    if(isset($username)) {
      $this->auth['uname']=$username;        ## This provides access for 'loginform.ihtml'
    }
    
    
    $uid = false;
    
    $this->db->query(sprintf('select user_id, perms '.
                             "        from %s ".
                             "       where username = '%s' ".
                             "         and password = '%s'",
                          $this->database_table,
                          addslashes($username),
                          addslashes($password)));

    while($this->db->next_record()) {
      $uid = $this->db->f('user_id');
      $this->auth['perm'] = $this->db->f('perms');
    }
    return $uid;
  }
}

class SourceWell_Default_Auth extends SourceWell_Auth {
  var $classname = 'SourceWell_Default_Auth';
  
  var $nobody    = true;
}

class SourceWell_Challenge_Auth extends Auth {
  var $classname      = 'SourceWell_Challenge_Auth';

  var $lifetime       =  1;

  var $magic          = 'Simsalabim';  ## Challenge seed
  var $database_class = 'DB_SourceWell';
  var $database_table = 'auth_user';

  function auth_loginform() {
    global $sess;
    global $challenge;
    global $_PHPLIB;
    
    $challenge = md5(uniqid($this->magic));
    $sess->register('challenge');
    
    include($_PHPLIB['libdir'] . 'crloginform.ihtml');
  }
  
  function auth_validatelogin() {
    global $username, $password, $challenge, $response;

    if(isset($username)) {
      $this->auth['uname']=$username;        ## This provides access for 'loginform.ihtml'
    }
    $this->db->query(sprintf("select user_id,perms,password ".
                "from %s where username = '%s'",
                          $this->database_table,
                          addslashes($username)));

    while($this->db->next_record()) {
      $uid   = $this->db->f('user_id');
      $perm  = $this->db->f('perms');
      $pass  = $this->db->f('password');
    }
    $exspected_response = md5("$username:$pass:$challenge");

    ## True when JS is disabled
    if ($response == '') {
      if ($password != $pass) {
        return false;
      } else {
        $this->auth['perm'] = $perm;
        return $uid;
      }
    }
    
    ## Response is set, JS is enabled
    if ($exspected_response != $response) {
      return false;
    } else {
      $this->auth['perm'] = $perm;
      return $uid;
    }
  }
}

##
## SourceWell_Challenge_Crypt_Auth: Keep passwords in md5 hashes rather 
##                           than cleartext in database
## Author: Jim Zajkowski <jim@jimz.com>

class SourceWell_Challenge_Crypt_Auth extends Auth {
  var $classname      = 'SourceWell_Challenge_Crypt_Auth';

  var $lifetime       =  1;

  var $magic          = 'Frobozzica';  ## Challenge seed
  var $database_class = 'DB_SourceWell';
  var $database_table = 'auth_user_md5';

  function auth_loginform() {
    global $sess;
    global $challenge;
    
    $challenge = md5(uniqid($this->magic));
    $sess->register('challenge');
    
    include('crcloginform.ihtml');
  }
  
  function auth_validatelogin() {
    global $username, $password, $challenge, $response;

    $this->auth['uname']=$username;        ## This provides access for 'loginform.ihtml'
    
    $this->db->query(sprintf('select user_id,perms,password '.
                "from %s where username = '%s'",
                          $this->database_table,
                          addslashes($username)));

    while($this->db->next_record()) {
      $uid   = $this->db->f('user_id');
      $perm  = $this->db->f('perms');
      $pass  = $this->db->f('password');   ## Password is stored as a md5 hash
    }
    $exspected_response = md5("$username:$pass:$challenge");

    ## True when JS is disabled
    if ($response == '') {
      if (md5($password) != $pass) {       ## md5 hash for non-JavaScript browsers
        return false;
      } else {
        $this->auth['perm'] = $perm;
        return $uid;
      }
    }
    
    ## Response is set, JS is enabled
    if ($exspected_response != $response) {
      return false;
    } else {
      $this->auth['perm'] = $perm;
      return $uid;
    }
  }
}

class SourceWell_Perm extends Perm {
  var $classname = 'SourceWell_Perm';
  
  var $permissions = array(
                            'user_pending' => 1,
                            'anonymous' => 2,
                            'user'       => 4,
                            'editor'     => 8,
                            'admin'      => 16
                          );

  function perm_invalid($does_have, $must_have) {
    global $perm, $auth, $sess;
    global $_PHPLIB;
    
    include($_PHPLIB['libdir'] . 'perminvalid.ihtml');
  }
}

?>
