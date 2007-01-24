import os,sys

# Obligatory
try:
    import pycvsanaly.database as database
except:
    print "\nNo pycvsanaly library found!. Please install cvsanaly first!\n"
    sys.exit(0)

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

def info ():

    print "Name: graphs"
    print "Author(s): Alvaro Navarro y Alvaro del Castillo"
    print "Description: Graphs and intermediate tables for cvsanaly-web"
    print "Last Updated: 23/01/07"

def run (db):

    # Fun starts here. We received a database descriptor.
    db.create_table('commiters_module', tables.commiters_module)
    #db.create_table('comments', tables.comments)
    db.create_table('cvsanal_fileTypes', tables.cvsanal_fileTypes)
    db.create_table('cvsanal_temp_commiters',tables.cvsanal_temp_commiters)
    db.create_table('cvsanal_temp_modules', tables.cvsanal_temp_modules)
    db.create_table('cvsanal_temp_inequality',tables.cvsanal_temp_inequality)

    #intmodule.intermediate_table_commitersmodules(db)
    intmodule.intermediate_table_commiters(db)
    intmodule.intermediate_table_fileTypes(db)
    intmodule.intermediate_table_modules(db)

    # Create and change
    if not os.path.isdir (graphs_directory):
        os.mkdir (graphs_directory)

    try:
        os.chdir (graphs_directory)
    except:
        pass

    # Print graphs
    print "Plotting globals grahps"
    g_global.plot (db)
    g_pie.plot (db)
    g_gini.plot (db)
    g_activity.plot (db)
    g_inequality.plot (db)
    g_heatmaps.plot (db)

