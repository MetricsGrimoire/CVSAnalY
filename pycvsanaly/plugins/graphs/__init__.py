import os,sys

from pycvsanaly.plugins import Plugin, register_plugin

import pycvsanaly.database as database

# Local import only for graph plugin
import intermediate_tables as intmodule
import tables_skeleton as tables

import graph_global as g_global
import graph_pie as g_pie
import graph_gini as g_gini
import graph_activity as g_activity
import graph_inequality as g_inequality
import graph_heatmaps as g_heatmaps

graphs_directory = 'graphs'

class GraphsPlugin (Plugin):

    def __init__ (self, db = None):
        Plugin.__init__ (self, db)

        self.name = "Graphs"
        self.author = "Alvaro Navarro and Alvaro del Castillo"
        self.description = "Graphs and intermediate tables for cvsanaly-web"
        self.date = "23/01/07"

    def run (self):
        # Fun starts here. We received a database descriptor.
        self.db.create_table('commiters_module', tables.commiters_module)
        #db.create_table('comments', tables.comments)
        self.db.create_table('cvsanal_fileTypes', tables.cvsanal_fileTypes)
        self.db.create_table('cvsanal_temp_commiters',tables.cvsanal_temp_commiters)
        self.db.create_table('cvsanal_temp_modules', tables.cvsanal_temp_modules)
        self.db.create_table('cvsanal_temp_inequality',tables.cvsanal_temp_inequality)

        #intmodule.intermediate_table_commitersmodules(db)
        intmodule.intermediate_table_commiters(self.db)
        intmodule.intermediate_table_fileTypes(self.db)
        intmodule.intermediate_table_modules(self.db)

        # Create and change
        if not os.path.isdir (graphs_directory):
            os.mkdir (graphs_directory)

        try:
            os.chdir (graphs_directory)
        except:
            pass

        # Print graphs
        print "Plotting globals grahps"
        g_global.plot (self.db)
        g_pie.plot (self.db)
        g_gini.plot (self.db)
        g_activity.plot (self.db)
        g_inequality.plot (self.db)
        g_heatmaps.plot (self.db)

register_plugin ('graphs', GraphsPlugin)
