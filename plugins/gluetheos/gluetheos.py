import os
from Crypto.Hash import SHA
from myDatabase import *

TMPDIR = "/tmp/"

class GlueTheosApp:

    def __init__(self, cvsroot = None,
                 user = None,
                 password = None,
                 host = None,
                 database = None,
                 module_name = None):

        self.db = MyDatabase()
        self.db.user = user
        self.db.password = password
        self.db.host = host
        self.db.name = database

        self.db.connect()

        self.cvsroot = cvsroot
        self.module_name = module_name

        self.tmpdir = TMPDIR

    def run(self):

        self.populate()

    def populate(self):

        
        self.db.getFilenameRevisionList()

        # fetchone broken??
        #pair = self.db.cursor.fetchone()

        #while pair:
        for pair in self.db.cursor.fetchall():

            filename = pair[0]
            # Check if module_name must be added to filename
            if self.module_name:
                orig_filename = filename
                filename = self.module_name+"/"+filename
            
            revision = pair[1]
            rev_date = pair[2]
            rev_time = pair[3]

            print "Retrieving "+filename+" @ "+revision


            try:
                # Getting
                self.CVSCheckout(filename,revision)
                sha1 = self.getSHA1(filename)
                nilsimsa = self.getNilsimsa(filename)

                comp_filename = filename+'.gz'

                # Storing
                self.compressFile(filename)
                try:
                    self.db.insertFile(orig_filename,comp_filename,revision,rev_date,rev_time,sha1,nilsimsa,self.tmpdir)
                except:
                    print "   Error inserting this file"

                # Cleaning out
                self.db.connection.commit()
                self.cleanFile(filename)
            except IOError:
                print "   Error retrieving file"

            # Go for the next pair file-revision

            #pair = self.db.cursor.fetchone()
            #print pair

    def compressFile(self,filename):
        os.chdir(self.tmpdir)
        os.system('gzip -f9 '+filename)
        
    def cleanFile(self,filename):
        os.chdir(self.tmpdir)
        os.remove(filename+'.gz')
            

    def getSHA1(self,filename):

        filepath = self.tmpdir + filename
        fileobj = open(filepath,'r')
        content = ''.join(fileobj.readlines())
        fileobj.close()

        h = SHA.new()
        h.update(content)

        return h.hexdigest()

    def getNilsimsa(self,filename):

        filepath = self.tmpdir + filename
        cmd = "nilsimsa "+filepath
        output = self.getCommandOutput(cmd)
        line = output[0]

        code = line.split(' ')[0]

        return code

    def getCommandOutput(self,cmd):
        pipe = os.popen(cmd)
        output = pipe.readlines()
        pipe.close()

        return output

    def CVSCheckout(self,filename,revision):

        cvsroot = self.cvsroot
        os.chdir(self.tmpdir)
        cvs_cmd = "cvs -d "+cvsroot+" checkout -r "+revision+" "+filename
        os.system(cvs_cmd)

        
