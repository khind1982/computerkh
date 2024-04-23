from citations.base import dbconnector
import MySQLdb


#will remove any duplicate matches from our self.table_matches: a log file will contain list of record deleted and kept

class singlematch():

    def __init__(self):
        
        
        print "starting..."

    def get_seed_row(self):
        #Query to select one entry; ordering is gratuitous
        #**q = """select * from %s order by id1 """ % (table) 
        q = """select * from %s order by id1 """ %(self.table_matches)

        self.cuA.execute(q)
        seed_rows = self.cuA.fetchall()
        return seed_rows


    def make_idtable_dic(self, rows):
        """Assume the input row has fields id1, table1 etc Returns a set of
        tuples
        """
        output = {}  
        for row in rows:
        #Extract info into tuples
            output[row["id1"]] = row["table1"]
            output[row["id2"]] =  row["table2"]

        return output


    #Need to pull in all entries with the existing ids
    #At this point the ids only are used - assumed to be no overlap

    def get_more_rows(self,dic_in): 
        """Send in the dictionary of idtable - pull out all the rows containing any of these, turn it into a new dictionary"""
        ids = dic_in.keys()
        #**q = "select * from %s where id1 in (%s) or id2 in (%s)" % (table, ", ".join(["'%s'" % item for item in ids]), ", ".join(["'%s'" % item for item in ids]))
        q = "select * from %s where id1 in (%s) or id2 in (%s)" % (self.table_matches, ", ".join(["'%s'" % item for item in ids]), ", ".join(["'%s'" % item for item in ids]))
        self.cuA.execute(q)
        rows = self.cuA.fetchall()
        return rows



    def cleanse(self):
        related_ids = {}  #Set of related ids: dictionary to tablename
        change='No'
        log=open("check.log",'a')
        seed_rows = self.get_seed_row()
        for seed_row in seed_rows:
            idtable_dict = self.make_idtable_dic([seed_row])
            #return dicionary wit 2 element {id1:table1,id2;table2}
            for k,v in idtable_dict.iteritems():
                related_ids =idtable_dict
            related_ids =  list(self.get_more_rows(related_ids))
            if log.closed:
                log=open("check.log",'a')
            if len(related_ids)>1:
                while len(related_ids)>1:

                    inirec=related_ids.pop()

                    for rec in related_ids:
                        if inirec ['id1']==rec['id1'] and inirec ['id2']==rec['id2'] or inirec ['id1']==rec['id2'] and inirec ['id2']==rec['id1']: 
                            log.write("\n\nKept:")
                            log.write(inirec['id1']+"/"+inirec['id2'])
                            log.write("\ndeleted:"+ rec['id1']+"/"+rec['id2'])
                            q = """delete from %s where relid= %s""" %  (self.table_matches,rec["relid"])
                            print q
                            self.cuA.execute(q)
                            related_ids.remove(rec)
                            change='yes'
                        

        if change=='yes':
            #check have we missed anything the first time round?
            log.close()
            self.cleanse()
            
            
            
    def launchcleaner(self):
        current_conA=dbconnector.dbconnector(user=self.userA, passwd=self.passwdA, db=self.dbA, host=self.hostA).MakeConnection()
        self.cuA=current_conA.cursor(MySQLdb.cursors.DictCursor)
        #will return a fetchal in the form of a dictionary not tuples:
        #{'table2': u'citations_journalarticles', 'confidence': 0L, 'relid': 624, 'id2': u'cit-ja-000225317', 'id1': u'cit-ja-000239288', 'table1': u'citations_journalarticles'}
        self.cleanse()
        