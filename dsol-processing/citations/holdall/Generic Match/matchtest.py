from citations.base.dbconnector import dbconnector  
from citations.base.baseRecord import *
from citations.holdall.citation import CitationRecordSet, CitationRecord
from fuzzyMatch import fuzzy, removeDiacritics, flattenText
# this is the python implementation of jarow
from jarow import jarow
import difflib
import pprint
import types
import unicodedata
pp = pprint.PrettyPrinter(indent=4)



"""
matchmaker.py identifies duplicate records either within a citation type (journal articles to journal articles etc) or between citations and primary records. 

Since there is different types of matches  multiple processes can be  run simultaneously.



TO INHERIT THIS CLASS FIRST CREATE A:


MATCH TABLE
Create the table that will store the matches with the following  command (copy and paste): The table MUST be created in the 
same database as table  A.
You may change the table name but not the field names.
this (table name)will be your table_matches attibute in the child class

CREATE TABLE `relships_sameas` (`relid` mediumint(8) unsigned NOT NULL auto_increment,
`id1` varchar(30) NOT NULL default '0',`table1` varchar(64) NOT NULL,
`id2` varchar(30) NOT NULL default '0',`table2` varchar(64) NOT NULL,
`confidence` int(3) unsigned NOT NULL default '0',PRIMARY KEY  (`relid`),
KEY `id2` (`id2`),KEY `id1` (`id1`),KEY `table1` (`table1`),
KEY `table2` (`table2`)\n) ENGINE=MyISAM DEFAULT CHARSET=latin1

"""






#1)When run cannot find method identity






class PartitionMaker(object):
    """Class to control the partitioning of data sets into manageabe
    chunks.  Idea is to run over a single field without loading the
    whole data set into objects.  Do fuzzy matching on the chosen
    field and use the results to compare subsets of data for more
    detailed match criteria.

    This is  a mixin class - no state, only methods.
    """

    
    def fetch_values(self, field1, field2=None):
        """Loads discrete values of the given field from one or two tables.
        Used for initial partitioning.  Can use different field names
        on A and B table, but default is to the same value.
        
        At the moment only field1 is sent
        """
        
        
        if field2 and self.table_A != self.table_B:
            q = """select distinct(%s) from %s union select distinct(%s) from %s""" % (field1, self.table_A, field2, self.table_B)
        else:
            q = """select distinct(%s) from %s""" % (field1, self.table_A)

        print q

        self.cuA.execute(q)
        results = self.cuA.fetchall()
        if results:
            results = [item[0] for item in results]
            return results
        else: return None
        
    def create_partition_sets(self):
        """Do some prematching to find sets of values with the same fuzzy
        profile.  Stratgy is to tick through the list and select those
        that meet the fuzzy citeria.  Repteat until no growth.  Move
        on to next item not yet done The relationship is hard_coded
        for now
        
        No distinction here is made between the A and B data
        sets. This is suboptimal, but that's the way it goes.  (So
        same partition on same fields names used for both data sets.)
        
        """
  
        #*** " ("publisher", "difflib", .85)= partition_key
        (field, metric, threshold) = self.partition_key


        valuesFromDB = self.fetch_values(field1=field)
        
        #valuesFromDB = self.fetch_values(field1="publisher")
        #will fetch all publisher from table A 
        #select distinct publisher and return [item[0] for item in results] of fetchall
        
        values = set()

        #some of the fields are badly encoded, the db engine can't
        #work out what coding they're in and so they return as
        #'NoneType', which means that difflib throws a fit when it
        #attempts to compute its length
        # here we just filter out the records that can't be cleanly
        #converted to unicode strings
        for value in valuesFromDB:
            if isinstance(value, unicode):
                # using isinstance(obj, str)
                # isinstance() calls to verify type= if unicode..save to list
                values.add(value)

        list_of_sets = []
        

        i = 1
        done = False
        while not done:
            value = values.pop()
            ##***the variable "matches" is reset after each loop
            if metric == "difflib":
                matches = set(difflib.get_close_matches(value, values, 10000, threshold))
                """
                Function get_close_matches(word, possibilities, n=3, cutoff=0.6):
                 
                    Use SequenceMatcher to return list of the best "good enough" matches.
                 
                    word is a sequence for which close matches are desired (typically a
                    string).
                 
                    possibilities is a list of sequences against which to match word
                    (typically a list of strings).
                 
                    Optional arg n (default 3) is the maximum number of close matches to
                    return.  n must be > 0.
                 
                    Optional arg cutoff (default 0.6) is a float in [0, 1].  Possibilities
                    that don't score at least that similar to word are ignored.
                 
                    The best (no more than n) matches among the possibilities are returned
                    in a list, sorted by similarity score, most similar first.

                
                """
            else:
            
                matches = set([item for item in values if metric(value, item) > threshold])
                
            
            matches.add(value)
            #from the dataset returned by the select statement(on a single field)
            #values are grouped together in "sets" accordind to their closeness 
            #example set([u'Cromwell', u'Crowell-', u'Crowell'])
            list_of_sets.append(matches)
            values = values.difference(matches)
            #***we are removing anything matched  before the next loop
            print len(values), "candidates left"

            if len(values) == 0:
                done = True

       
        print "This is the super set"
        for item in list_of_sets:
           print item
           print "\n"
        
        self.partition_sets = list_of_sets

    
    def create_partition_query(self, table, field, partition_set):
        """Interrogates for all the alternatives in a partition set"""
       
        
        q = """select * from %s where %s in (%s)"""
        conditions_sub = "%s, " * len(partition_set)
        conditions_sub = conditions_sub[:-2]
        q_filled = q % (table, field, conditions_sub )
        
        return (q_filled, tuple(partition_set))
        
        
        """
           >>> partition_key=("publisher", "difflib", .85)
           >>> field=partition_key[0]
           >>> table= "publisher"
           >>> partition_set=set([u'Cromwell', u'Crowell-', u'Crowell'])
           >>> conditions_sub = "%s, " * len(partition_set)
           >>> conditions_sub
           '%s, %s, %s, '
           
           >>> conditions_sub
           '%s, %s, %s'
           >>> q = ""select * from %s where %s in (%s)""
           >>> q_filled = q % (table, field, conditions_sub )
           >>> whatreturned=(q_filled, tuple(partition_set))
           >>> whatreturned
           
           ('select * from BOOK where publisher in (%s, %s, %s)', (u'Cromwell', u'Crowell-', u'Crowell'))   
        """

      
     
    def populate_by_partition(self, partition_set):
    
        #populate_by_partition(self,(u'Cromwell', u'Crowell-', u'Crowell'))
        """Fill the A and B lists with data using partition queries. 
        A generator - somewhat gratuitiously."
         
        """
         
        #Gets the next partition set
        #Clean out the old stuff -
        del self.records_A[:]
        del self.records_B[:]
      
        (q, c) = self.create_partition_query(self.table_A, self.partition_key[0], partition_set)
        print "Query", q, c
        #self.partition_key[0]=publisher
        #(q, c) = ('select * from Table A(citations_books) where publisher in (%s, %s, %s)', (u'Cromwell', u'Crowell-', u'Crowell'))
        self.records_A.freesearch(q, substitutions=c)
        
 
        (q, c) = self.create_partition_query(self.table_B, self.partkeydic[self.partition_key[0]], partition_set)
        #self.partkeydic[self.partition_key[0]]...get the corresponding field in table B
        self.records_B.freesearch(q, substitutions=c)
        
        #FOR RACH PARTTION WILL TRY THE SAME THING so continue with for example
        #set([u'Harvill', u'Harville'])
        #set([u'Poetry'])

       
    #metrics
    
    """ returns true of value1 is within percentage of value2, false
    otherwise """
    def within(value1, value2, percentage):
        singlePercent = value2 / 100.0
        range = percentage * singlePercent
        upperBound = value2 + range
        lowerBound = value2 - range
    
        if value1 >= lowerBound and value1 <= upperBound:
            return True
        else:
            return False
    
    def identity(text1, text2): 
    
        if text1 == text2: return 1
        else: return 0
        
     
    def levenstein(text1, text2):
        return fuzzy(text, text)[1]
      
      
    def difflib_metric(text1, text2):
        """Is there are difflib function for this which returns a metric?"""
        # AJWS - not really, we can try and work out the threshold at which
        # close_matches fails to match, but that would require successive
        # runs of close_matches and may end up being more computationally
        # more expensive than something like the levenstein
    pass        
        





        
class MatchMaker(PartitionMaker): 
    """MatchMaker class acts as a bridge betweent the two data sets.  It
    handles import of data into appropriate record sets, with
    partitioning of the data sets if appropriate

    The data for the two sets is held in two RecordSet attributes
    
    """
    
    
    def __init__(self):
    
        print "starting"
       
        
 
        
    def match(self):
        """Time to match. Tick through the records in the A list and cull the
        B list until only matches remain.  There may be a variety of
        keys - want to limit the amount of duplication here.  A match
        is something which satisfies any of the keys on offer, so need
        to refresh the B_list data for each key."""
        
        for record in self.records_A:
            print "this is record",record,"\n\n"
            matches = []  #collection of records which matched one of the keys
       
            for key in self.match_keys:
                #print "match_keys", self.match_keys
                #"match_keys":"books_amazon_isbn",
                """
                books_amazon_isbn = (  
                            (("author", jarow, .95),  ("title", jarow, .85), ("publoc", jarow, .6)),
                            )


                  key in self.match_keys    =  (("author", jarow, .95),  ("title", jarow, .85), ("publoc", jarow, .6))
                """
                #first time the variable is used
                print "this is key",key,"\n\n"
                candidates = self.records_B[:]

                for tooth in key:
                    #("author", jarow, .95),  ("title", jarow, .85), ("publoc", jarow, .6)
                    #If the field has already been used in a
                    #partition, then pass over it.  It might be the
                    #case that that a stricter value be used here than
                    #used in the partition (to compensate for data
                    #missing in other fields) - but to accomodate that
                    #should keep track of the metrics and enable
                    #branching of sub keys.
                    
                    #this should be on a switch - sometimes the
                    #partition will be used, but sometimes it won't.
                    #if tooth[0] == self.partition_key: continue
                    print "this tooth",tooth,"\n\n"
                    
                    candidates = [r for r in candidates if self.match_tooth(tooth, record, r)]
                    #compare each record in self.records_A to each record in self.records_B

                #Lump all the matches for the different keys together
                matches.extend(candidates)
                record.matches = matches
        if len(matches) > 0 :
            print "Length of matches is ", len(matches)
            print "Got these matches"
            print "Record", 
            pp.pprint (record.__dict__)
            print "Matches"
            for i in matches:
                pp.pprint(i.__dict__), "\n"
        else:
            print "No matches"


    def match_tooth(self,tooth, record1, record2):
        """Binary output on whether records match tooth of key"""
        
        (field, metric, threshold) = tooth
        
   
        text1 = getattr(record1, field)
        text2 = getattr(record2,self.partkeydic[field])
        #self.partkeydic[field] use table A field name to get table B field name
        
        bit = self.metric_binary(text1, text2, metric, threshold)
        return bit


    def metric_binary(self,text1, text2, metric, threshold):
        """Returns 1 or 0 if strings meet threshold for given metric"""
        
        #Is this optimal? If the data just doesn't exist, won't get a match
        if text1 is None or text2 is None: return 0
    
        if  metric(text1, text2)>= threshold :   #threshold  is in range [0,1]
            return 1
        else:
            return 0



    def write_matches_to_db(self):
    
        #Need to get a way to store the uniques identifier of tableA(record.id)and table B(match.id)
        """Matches for each A record stored as an attribute of that record.
        No de-duping is done at this stage - that is left to MySQL.
        It might make sense to do it here though to save processing...
        There is some flakiness here as the tablenames come from the A
        and B lists rather than the records themeselves - this info
        should be passed down.
        
        
        """
        q  = """INSERT IGNORE INTO %s (id1,table1,id2, table2,confidence) VALUES (%%s  , %%s , %%s , %%s , %%s )"""
        q_filled = q % self.records_A.table_matches
        print q_filled
        for record in self.records_A:
            
            for match in record.matches:
            
            
               #Check that this is not the same as itself in a
               #de-duping exercise
           
                if record.id == match.id:
                    continue
           

                # hmm, it looks likd the confdience value in the table
                # is never used the query tries to stuff "TBA" into an
                # integer field, resulting in the value of 0 for all
                # entries
                
                
                #
                #Do we want to store the confidence ratios?
                #
                params =  ( str(record.id ),  self.records_A.tablename,  str(match.id),
                            self.records_B.tablename,  "TBA")
    
           
                #print "\nThe stashing query is:\n" , q_filled, "\n\n\n"
                print "\n\nGot a match"
                print  q_filled % params
           

                #self.db_cu.execute(q_filled, params)  
                self.cuA.execute(q_filled, params) 
                
  
    def find_and_store_matches(self):

        print  self.__dict__
        self.set_recordset_attribs()
        for key in self.match_keys[:]:
                    print "keys", key
        print "Creating partition sets"
        self.create_partition_sets()
        print "Finished creating partition sets"

        #We have now a list of values that very close to eachover...they could be duplicates
        #(slight difference cause error: exp typing error) or point later to duplicates excluded when we used
        #distinct in the select statement  

        #write partitions to file
        print "Writing partitions"
        out = open("partition_sets", "w")
        for i in self.partition_sets:
            print "\t" + str(i)
            out.write(str(i) + "\n")
            #will write
            #set([u'Harvill', u'Harville'])
            #set([u'Poetry']).. 
            print "\t Populating"
            self.populate_by_partition(i)
            #for each element of set will find the corresponding similar records?
            print "\t Matching"
            self.match()
            print "\t Writing matches to DB"
            self.write_matches_to_db()           


    def set_recordset_attribs(self):
       # Communicates settings to A and B record sets
        current_conB = dbconnector(user=self.userB, passwd=self.passwdB, db=self.dbB, host=self.hostB)
        self.databaseConnectionB = current_conB
        current_conA = dbconnector(user=self.userA, passwd=self.passwdA, db=self.dbA, host=self.hostA)
        self.databaseConnectionA = current_conA
        self.records_A = BaseRecordSet()
        self.records_A.recordclass = BaseRecord
        self.records_B = BaseRecordSet()
        self.records_B.recordclass = BaseRecord
        self.records_A.tablename = self.table_A        
        self.records_B.tablename = self.table_B        
        self.records_A.table_matches = self.table_matches      
        self.records_A.databaseConnection = self.databaseConnectionA.MakeConnection
        self.records_B.databaseConnection = self.databaseConnectionB.MakeConnection  
        # insert in self.table_matches
        self.cuA = self.databaseConnectionA.MakeConnection().cursor()        


    
