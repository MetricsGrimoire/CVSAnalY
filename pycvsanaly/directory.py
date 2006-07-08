# Copyright (C) 2006 Libresoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors :
#       Jorge Gascon   <jgascon@gsyc.escet.urjc.es>
#       Alvaro Navarro <anavarro@gsyc.escet.urjc.es>

"""
Class that implements basic directories operations

@author:       Jorge Gascon and Alvaro Navarro
@organization: Grupo de Sistemas y Comunicaciones, Universidad Rey Juan Carlos
@copyright:    Universidad Rey Juan Carlos (Madrid, Spain)
@license:      GNU GPL version 2 or any later version
@contact:      jgascon,anavarro@gsyc.escet.urjc.es
"""

class node:
   """ Node of the tree hirealchy """ 

   number = 1
   left = 1
   right = 1
   children = {}
    
   def __init__(self, dir_id, dir_left, dir_right, childrens):
      self.number = dir_id
      self.left = dir_left
      self.right = dir_right
      self.children = childrens

   def __str__(self):
      return str(self.number) + " " + str(self.left) + " " + str(self.right) + " " + str(self.children)
   def __repr__(self):
      return str(self.number) + " " + str(self.left) + " " + str(self.right) + " " + str(self.children)

class tree:
   """ Tree class """

   def __init__(self,dir_id):
      self.number = dir_id
      self.root = node(self.number, 1, 2, {})
      #self.number += 1

   def destroy(self):
      self.root.children = {}
      self.root.number = 1
      self.root.left = 1
      self.root.right = 1
      self.number = 1

   def updatelr(self, right_father, node):
      """ Set left/right id."""
      if node.left > right_father:
         node.left+=2
      if node.right >= right_father:
         node.right+=2

      # we obtain the list of soons and for each child we modify
      # their left and right fields
      list_of_childs = node.children.keys()
      for child in list_of_childs:
         element = node.children[child]
         self.updatelr(right_father,element)

   def getid(self,path):
      """ Return the id of a given path """
      if path[0] != "/":
         path = "/" + path

      if path[len(path)-1] == "/":
         path = path[:-1]
      
      aux = path.split("/")

      id = 0
      node = self.root
      for n in aux[1:]:
         try:
            node = node.children[n]
            id = node.number
         except KeyError:
            id = 0
            
      #print "PATH = " + str(path) + " ID = " + str(id)
      return id

   def tree2mysql(self,db,node,name,father_id, output):
      """ Transform Tree in mysql syntax """
      if name != "":
         query = "INSERT INTO modules " +\
                 "(module_id, lft, rgt, father_dir, module) " + \
                 "VALUES ('" + \
                 str(node.number) + "','" + \
                 str(node.left)     + "','"  + \
                 str(node.right) + "','"  + \
                 str(father_id)     + "','"  + \
                 name          + "');"
         if output == "":
            db.insertData(query)
         else:
            output.write(str(query) + ";\n")
             
      list_children = node.children.keys()
      for key in list_children:
         element = node.children[key]
         self.tree2mysql(db,element, key, node.number, output)

   def addDirectory(self, path):
      """Given a path it creates its directory hierarchy"""

      print str(path)
      if path[0] != "/":
         path = "/" + path
         
      if path[len(path)-1] == "/":
         path = path[:-1]

      if path != "/":
         list = path.split('/')
         iterator = self.root

         # For each slice
         for slice in list[1:]:
            try:
               iterator = iterator.children[slice]

            # If it doesn't exists, we creat it
            except KeyError:

               right_father = iterator.right
               aux = self.root
               self.updatelr(right_father,self.root)
               
               iterator.children[slice] = node(self.number, right_father, right_father+1, {})
               self.number+=1
               iterator = iterator.children[slice]
               
            #DEBUG
            #print self.root


class Directory:
    """This class represents a directory in the repository."""

    # Static variables
    counter = 0
    created_dirs = []
    
    def __init__(self,properties_dict=None,files_list=None):
      """Constructor. Can accept a dictionary containing the properties of this commit, and a list of files objects stored in this dir."""

      if properties_dict:
         self.properties_dict = properties_dict.copy()
      else:
         self.properties_dict = {}
         
      if files_list:
         self.files_list = files_list
      else:
         self.files_list = []

      self.id = Directory.counter
      
      Directory.counter += 1
      Directory.created_dirs.append(self)

    def directory2SQL(self):
      """ Create a tree hierarchy from the created_dirs list"""
      mtree = tree(0)
      for aux in Directory.created_dirs:
         mtree.addDirectory(aux.properties_dict['name_dir'])
         #print aux.properties_dict['name_dir']
      mtree.tree2mysql(mtree.root,"",mtree.root.number,"")
	
    def search_directory(self,dir_id):
      """Looks for a directory with a given id. It returns a Directory object, or None if given id does not exist."""

      try:
         directory = Directory.created_dirs(dir_id)
      except:
         directory = None

      return directory
 
    def get_id(self):
       """Return integer id of this directory"""
       return self.id

    def add_properties(self, properties):
        """ Add properties """
        self.properties_dict = properties
	
    def add_file(self,file_obj):
      """Add a file stored in this directory."""
      self.__files_list.append(file_obj)


    def get_files(self):
      """Get a list of the files affected by this commit."""
      return self.__files_list
	
	
