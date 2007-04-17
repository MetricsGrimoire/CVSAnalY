import os

from pycvsanaly.plugins import Plugin, register_plugin

import generations

class GenerationsPlugin (Plugin):

    def __init__ (self, db = None, opts = []):
        Plugin.__init__ (self, db)

        self.output_dir = None
        for opt, value in opts:
            if opt in ("--output-dir"):
                self.output_dir = value
        # TODO: periods as command line arguments

        self.name = "generations"
        self.author = "Jesus M. Gonzalez-Barahona"
        self.description = "Commiters generations"
        self.date = ""

    def get_options (self):
        return ["output-dir="]

    def usage (self):
        print """Generations:

  --output-dir      Output directory [./generations]
"""

    def run (self):
        if self.output_dir is None:
            gens_directory = 'generations'
        else:
            gens_directory = self.output_dir

        if not os.path.isdir (gens_directory):
            os.mkdir (gens_directory)

        period = generations.periodSlots(10)
        gen = generations.generations (self.db, gens_directory, period)
        period = generations.periodDays(300)
        gen = generations.generations (self.db, gens_directory, period)
        period = generations.periodDays(200)
        gen = generations.generations (self.db, gens_directory, period)
        period = generations.periodQuarter()
        gen = generations.generations (self.db, gens_directory, period)

register_plugin ('generations', GenerationsPlugin)
