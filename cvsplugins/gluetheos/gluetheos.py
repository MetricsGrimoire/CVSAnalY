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
                results_dict = self.measureFile(filename)

                comp_filename = filename+'.gz'

                # Storing
                self.compressFile(filename)
                try:
                    self.db.insertFile(orig_filename,comp_filename,revision,rev_date,rev_time,results_dict,self.tmpdir)
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

    def measureFile(self,filename):

        # TODO: Implement the function for every metric
        # TODO: Repeat for clean code
        
        sha1 = self.getSHA1(filename)
        nilsimsa = self.getNilsimsa(filename)
        sloc, lang, sloc_output = self.measureSloc(filename)
        loc, wc_output = self.measureLoc(filename)
        functions, ctags_output = self.measureFunctions(filename,lang)
        mccabe, returns, mccabe_output = self.measureMcCabe(filename)
        length, volume, level, mental_disc, halstead_output = self.measureHalstead(filename)

        fields = ['sloc','lang','output_sloccount', \
                  'loc','output_wc', \
                  'functions','output_ctags', \
                  'mccabe','returns','output_mccabe', \
                  'length','volume','level','mental_disc','output_halstead']

        # Create temp files for the output

        fn_sloc_output = os.tmpnam()
        fn_wc_output = os.tmpnam()
        fn_ctags_output = os.tmpnam()
        fn_mccabe_output = os.tmpnam()
        fn_halstead_output = os.tmpnam()

        filenames = {fn_sloc_output:sloc_output, \
                     fn_wc_output:wc_output, \
                     fn_ctags_output:ctags_output, \
                     fn_mccabe_output:mccabe_output, \
                     fn_halstead_output:halstead_output]

        # Store output in each temp file
        for fn in filenames.keys():
            f = open(fn,'w')
            f.write(filenames[fn])
            f.close()

        # The files will be stored in the database
        contents = [sloc, lang, 'LOAD_FILE('+fn_sloc_output+')', \
                   loc, 'LOAD_FILE('+fn_wc_output+')', \
                   functions, 'LOAD_FILE('+fn_ctags_output+')', \
                   mccabe, returns, 'LOAD_FILE('+fn_mccabe_output+')', \
                   length, volume, level, mental_disc, 'LOAD_FILE('+fn_halstead_output+')']

        for i in range(len(fields)):
            field = fields[i]
            content = contents[i]

            results_dict[field] = content

        return results_dict
        
    def measureSloc(self,filename):
        pass #TODO

    def measureLoc(self,filename):
        pass #TODO

    def measureFunctions(self,filename):
        pass #TODO

    def measureMcCabe(self,filename):
        pass #TODO

    def measureHalstead(self,filename):
        pass #TODO

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

        
