from gluetheos import *

def main():

    user = "root"
    password = "root"
    host = "localhost"
    database = "pgsql_cvsanaly"

    cvsroot = "/home/herraiz/mirror/postgres/cvs/pgsql"
    module_name = "src"
    
    app = GlueTheosApp(cvsroot,
                       user,
                       password,
                       host,
                       database,
                       module_name)

    app.run()


if __name__ == '__main__':

    main()
    
