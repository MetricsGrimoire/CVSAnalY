
def db_module(module):
        """
        Given the natural module name (string) it returns the module name
        that is used in the database. For different purposes, database
        table names cannot contain certain characters

        @type module: string
        @param :

        @rtype: string
        @return:
        """

        moduleName = module.replace('-', '_minus_')
        moduleName = moduleName.replace('+', '_plus_')
        moduleName = moduleName.replace('@', '_at_')
        moduleName = moduleName.replace('.', '_dot_')
        moduleName = moduleName.replace(':', '_ddot_')
        moduleName = moduleName.replace(' ', '_space_')
        moduleName = moduleName.replace('  ', '_doblespace_')
        moduleName = moduleName.replace('/', '_slash_')

        return moduleName

