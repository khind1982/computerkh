from matchtest import *
from cleaner import *





class twin (MatchMaker,singlematch):
    """
    In order to find matches :
    -within a single tables'
    -between 2 tables in the same database
    -between 2 tables in different databases
    -between a table and a set of XML files(will involve first extracting data from the files and storing them in a table is that OK with tristan?)


    Child classes like this one will only have to:
    initialise a number of attributes refering to the 
    
    -tables
    -partition key 
    -match key
    
    and make a function call:
    >>> from matchild import *
    >>> a=twin()
    >>> a.check()
    """

    def __init__(self):
    
        

        #CONNECTIONS
        
        #provide variables to create 2 connections to accommodate situations where
        #1)Matches are to be made between tables stored in different databases
        #WE SHOULD ALWAYS HAVE TWO DISTINCT CONNECTIONS EACH FOR EACH TABLE : A & B  even if table A and B are the same
        #(when looking for example for duplicates in the same table)

        #ONE:      connection variables for table A
        self.userA="holdall"
        self.passwdA="holdall"
        self.dbA="holdall_beta_2_ajws"
        self.hostA = "DSol"
        

        #TWO:   connection variable for table B
        self.userB="holdall"
        self.passwdB="holdall"
        self.dbB="holdall_beta_2_ajws"
        self.hostB = "DSol"
        
        
              

        #TABLES ATTRIBUTES
        #tables name and unique identifiers field names(table A and B only)
        table_A="citations_journalarticles" 
        table_B="citations_journalarticles"
        self.table_A = table_A
        self.table_B = table_B
        self.TAid="id"
        self.TBid="id"
        #table in which the matches will be stored: the table MUST BE in the same database as Table A(it is 
        # that database connection  that will be use to insert the matches
        #**********table_matches="ZNewrelships_sameas"
        
        table_matches="zcleanrel" 
        self.table_matches = table_matches
        
       
      
       
        """
        SELECTING THE RELEVANT  PARTITION AND MATCH KEYS
        
        KEYS FIELDS VALUES
        keys fields values(use the corresponding fields names in your table A)
        "year" = year of publication (format yyyy) ? of book only or article (in bookarticle)
        "author" = author
        "title" = journal article title  or book title  or book article title????
        "publoc" = place of  publication 
        "book" =   title of book
        "publisher" = name of the publisher
        "journal " = journal  name
 
        
        (the Partition&Match_keys.docx file will be helpful in identifying the appropriate partition and corresponding match key     
      
        The choice of appropriate partition and match on key will depend on the type of product being compared :
        Journal articles | Book articles | Book | Book(amazon_isbn) | Book(ISBNdb_isbn )
        AND the fields available in both tables being compared:
        for example the choice between Book | Book(amazon_isbn) | Book(ISBNdb_isbn )  for a book comparison 
        will depend on wether the fields containing the year and place of publication are present in both tables
        
        
        PARTITION KEY
        The partition key will be one of the following value/or if any of them is not available a common field(not necessarilly by name)
        to tables A & B
        The partition key will be either the field containing the journal name,  the name of the publisher of the book or the date of publication of the book 
        here again we have to take in account the fact that the field name might be different in the 2 tables
        """
       
        
        self.partition_key=("journal", "difflib", .85)

         
        
        
        #MATCH KEYS
        #should be the one corresponding to the partition key in the the Partition&Match_keys table
        
       
        self.match_keys = (    (("author", jarow, 0.85),  ("title", jarow, 0.85)), ) 
        
        
        #Note;
        #* other fields than those of the type in Partition&Match_keys.docx can be used as match keys
        #* do only however use tem only if these standars type of field are not available in the tables
        #* when using other type of fields the only rule to be aware of is the one relating t the type of fuzzy method to be used:
        #**USE: identity for date(in the format yyyy) and jarrow for text fields
      
      
      
        """
        VERY IMPORTANT
        THE ABOVE (elements [0] of self.partition_key and self.match_keys)ARE THE Table A fields names
        WE also need the correponding TABLE B fields names even if they are the same (as in this case)
        these corsesponding Table B fields will be obtained through a dictionary built as follow
        self.partkeydic={"tableAauXXX":"tableBauXXX","tableAjtXXX":"tableBjtXXX","tableApuXXX":"tableBpuXXX"}
        the name may be different : what is important is that both field hold the same type of values
        this dictionary will allow us to MATCH the corresponding fields in B
        The NAME of the dictionary should alway be the one given here
        """
        
        
        
        self.partkeydic={"journal":"journal","author":"author","title":"title"}
        
        #Key = table A field name.... Value = table B corresponding field's name
        
                
        
        
        
        #calling inherited method in Matchtest.py and cleaner.py to find the matches and remove duplicate matches(in match table only)
    def check(self):
        self.find_and_store_matches()
        #remove duplicate matches
        self.launchcleaner()
        
    
    
