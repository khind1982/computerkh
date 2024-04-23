import MySQLdb
import amara 
import pprint
pp = pprint.PrettyPrinter(indent = 4)


    
class BaseRecordSet(list):

    """This is a class to describe a set of records typically populated from a MySQL database.
    
    When you instantiate or subclass it there are a few attributes you should set:
    1. databaseConnection should be a function which returns a MySQLdb connection object
    2. tablename should be the name of the main relational table that the database will query

    This class is a subclass of list so has all the list methods such as append and pop, iteration and subscriptability.
    Note that the ordering of records is usually important which is why we subclass list and not set.

    The methods consist of a set of tools for finding out information about the database and a set
    of tools for querying that database. For sophisticated queries it is possible to explicitly set 
    this information and avoid calling any of the methods.
    
    The principle behind this class is to try and put all the MySQL database stuff in one place.
    
    Attributes: 
    databaseConnection: function
    fieldnames: list
    recordclass: class used to create list members (hcppRecord, bpRecord etc)
    tablename: string
    
    - database indexes stored in sets of strings by type
    fulltexts: set      
    primary: set
    btrees: set


    Methods: 
        getdbfields
        getdbindexes
        keysearch
        indexsearch
        freesearch
        populatefromdb
        fulltextsearch
        xml
        generate_citations
    
    """

    def getdbfields(self):
        """Get the field names for the table. This assumes that you have indicated what the table
        is called.
        
        It allows methods that create the record objects to give names to the attributes in those objects
        e.g. if it finds that the fields for that table are id, title, author then it will create attributes
        id, title and author in the objects.
        
        This will probably be only a subset of the fields. You can also consider setting the fieldnames attribute
        manually and using the optionalFields and requiredFields attributes.
        
        At some point those should probably all be tied together.
        """
        assert self.tablename
        db = self.databaseConnection()
        cu = db.cursor()
        cu.execute("""DESCRIBE %s;""" % (self.tablename,))
        self.fieldnames = [row[0] for row in cu.fetchall()]
        cu.close()
        db.close()

    def getdbindexes(self):
        """Get the index names for the table. 
        
        This is similar to the field names above but this returns the indexes on a table. This is useful for
        putting together a generic search function that is just going to look at indexes without needing to 
        know what sort of index it's looking at.
        
        So it would allow you to change the type of index without affecting that higher layer.
        """
        assert self.tablename
        db = self.databaseConnection()
        self.btrees = set()
        self.fulltexts = set()
        self.primary = set()
        cu = db.cursor()
        cu.execute("""SHOW INDEX FROM %s;""" % (self.tablename,))
        for row in cu.fetchall():
            if row[-2] == 'BTREE':
                self.btrees.add(row[4])
            elif row[-2] == 'FULLTEXT':
                self.fulltexts.add(row[4])
            if row[2] == 'PRIMARY':
                self.primary.add(row[4])
        cu.close()
        db.close()
        
    def keysearch(self, **conditions):
        """This is a very simple search which fills the record set with records which have a
        particular primary key.
        
        That's probably just going to be one record. So it's useful as a way of just pulling back a single record,
        for example to display a full record in a UI.
        """
        if not hasattr(self, 'primary'):
            self.getdbindexes()
        searchterms = set(conditions.keys())
        fieldnames = searchterms.intersection(self.primary)
        sqlconditions = ["`%s`='%s'" % (field, conditions[field].replace("\\", "\\\\").replace("'", "\\'")) for field in fieldnames]
        querystring = """SELECT * FROM %s WHERE %s""" % (
            self.tablename, " AND ".join(sqlconditions)
        )
        self.freesearch(querystring)        

    def indexsearch(self, **conditions):
        """Populate on the basis of a set of conditions targetted at btree or fulltext indexes.
        
        This is the function to call to actually do a search on the indexes in a table. If the object doesn't
        think it knows what indexes it has then it calls getdbindexes() to find out.
        
        The conditions that you pass to this record are normally in the form fieldname='value' but there's
        also a special "orderby" condition that allows you to determine the order of the records in the set.
        """
        assert self.tablename
        if not hasattr(self, 'btrees'):
            self.getdbindexes()
        searchterms = set(conditions.keys())
        fieldnames = searchterms.intersection(self.btrees)
        fulltextnames = searchterms.intersection(self.fulltexts)
        sqlconditions = ["`%s`='%s'" % (field, conditions[field].__str__().replace("\\", "\\\\").replace("'", "\\'")) for field in fieldnames] + \
                        ["MATCH (`%s`) AGAINST ('%s')" % (ftindex, conditions[ftindex]) for ftindex in fulltextnames]
        orderby = ""
        if conditions.has_key('orderby'):
            orderby = " ORDER BY " + conditions['orderby']

        if conditions.has_key('limit'):
            orderby += " LIMIT 0," + conditions['limit']
        
        if conditions.has_key('distinct'):
            self.fieldnames = [conditions['distinct']]
            whereclause = ''
            if len(sqlconditions) > 0:
                whereclause = " WHERE " + " AND ".join(sqlconditions)
            querystring = """SELECT DISTINCT %s FROM %s %s %s""" % (conditions['distinct'], self.tablename, whereclause, orderby)
        else:
            querystring = """SELECT * FROM %s WHERE %s %s""" % (self.tablename, " AND ".join(sqlconditions), orderby)
        self.freesearch(querystring)        
    
    def freesearch(self, querystring, substitutions=None):
        """Populate on the basis of any sql query. 
        This is the method called by all the search-type methods here to actually do the SQL. The other methods
        build the SQL as a string and then send it to this method.
        
        This just provides an easy way to populate a record set on the basis of an SQL query which may be extremely
        sophistciated.        
        
        Has the option of querying with direct query, or with a format string + arguments
        """
        if not hasattr(self, 'fieldnames'):
            self.getdbfields()
        db = self.databaseConnection()
        cu = db.cursor()
        #print "Base: " , querystring.encode('latin-1')
        if substitutions is not None: 
            cu.execute(querystring, tuple(substitutions))
        else: 
            cu.execute(querystring) 
        for values in cu.fetchall(): 
            newrecord = self.recordclass()
            newrecord.populateKeywords(**dict(zip([str(field) for field in self.fieldnames], values)))
            self.append(newrecord)
        cu.close()
        db.close()

    def populatefromdb(self, **conditions):
        """Append a set of records specified by the conditions
        Could do with null conditions option
        """
        
        
        if not hasattr(self, 'fieldnames'):
            self.getdbfields()
        assert self.tablename
        querystring = """SELECT * FROM %s WHERE %s""" % (self.tablename,   \
                   " AND ".join(["`%s`='%s'" % (name, unicode(value).replace("\\", "\\\\").replace("'", "\\'"))                \
                   for name, value in conditions.items()]))
        self.freesearch(querystring)
        
    def fulltextsearch(self, searchstring):
        """Populate the result set by searching the fulltext fields."""
        assert self.tablename
        assert self.fulltextfields
        # Add optional relevance score?
        # Add optional query expansion?
        querystring = """SELECT * FROM %s WHERE MATCH (%s) AGAINST ('%s');""" \
                   % (self.tablename, ", ".join(self.fulltextfields), searchstring)
        self.freesearch(querystring)
        
    def xml(self):
        """This method uses the amara module to return an xml representation of the record set object.
        It's pretty simple because it calls the xml method of each record in the set individually and nests
        the node set returned in a node named after whatever the class is called.
        
        This means that whatever you call the subclass that you derive from this one will be the name of the root
        node of the document.
        """
        doc = amara.create_document()
        container = doc.xml_append(
            doc.xml_create_element(
                unicode(self.__class__.__name__)
            )
        )
        for item in self:
            container.xml_append(item.xml())

        return container
    


    def propogate(self, attribute): 
        """Propogates an attribute of the record set to each member"""
        for item in self: 
            setattr(item, attribute, getattr(self, attribute))



class RelatedRecordSet(dict):
    """This class is intended to be a record set that is more like a dictionary where the keys
    are specified at init time.
    The idea is that you can read a set of related records into memory rather than having to hammer
    the MySQL database record by record."""   
       
    def freesearch(self, querystring, keyfield = None):
        """Populate on the basis of any sql query. 
        This is the method called by all the search-type methods here to actually do the SQL. The other methods
        build the SQL as a string and then send it to this method.
        
        This just provides an easy way to populate a record set on the basis of an SQL query which may be extremely
        sophisticated.        
        """
        if not hasattr(self, 'fieldnames'):
            self.getdbfields()
        if keyfield is not None:
            self.keyfield = keyfield
        
        db = self.databaseConnection()
        cu = db.cursor()
       
        cu.execute(querystring)
        for values in cu.fetchall(): 
            newrecord = self.recordclass()
            newrecord.populateKeywords(**dict(zip([str(field) for field in self.fieldnames], values)))
            if self.has_key(getattr(newrecord, self.keyfield)):
                self[getattr(newrecord, self.keyfield)].append(newrecord)
            else:
                self[getattr(newrecord, self.keyfield)] = [newrecord]
        cu.close()
        db.close()



        
        
        
class BaseRecord:
    """A bibliographic record; core data held as base-level attributes. 
    
    
    Attributes:
        - Auxilliary elements
        databaseConnection: function
        optionalFields: list   [Typically set by the subclass]
        requiredFields: list  [Typically set by the subclass]
        
        -  Attributes for the record proper
        <field>: unicode string  
        
        
    Methods: 
        populateKeywords(keywords) - sets keywords as attributes

        - Various elements to do with output to MySQL database
        getupdatefields
        InsertIntoDB
        RealInsertIntoDB
        updateDB
        doSQL
    
        - Other output formats
        fillTemplate - output in Cheetah template
        xml - output as xml
        
    """

    def populateKeywords(self, **keywords):
        """This simple method sets attribute values in the object based on keywords passed to it."""
        for name, value in keywords.items():
            setattr(self, name, value)

    def getupdatefields(self, desiredFields):
        """This is a method to help with the construction of SQL queries. It takes a set of field names and returns
        them in the format `name`='value' separated by commas so you could put them in a SET clause.
        Part of the idea here is to keep the bits that do character escaping all in the same place.
        
        Option: don't escape anything; rather let MySQL.execute() take care of everthing...
        """
        
        self.updatefields = set(desiredFields).intersection(dir(self))
        
        #This is not unicode safe - but not clear why...
    
        #return ", ".join([u"`%s`='%s'" % (name, unicode(value).replace("\\", "\\\\").replace("'", "\\'"))                   \
        #     for name, value in zip(self.updatefields,                \
        #      [getattr(self, attr) for attr in self.updatefields])])
        
        #try this
        try:   return u", ".join([u"`%s`='%s'" % (name, MySQLdb.escape_string(unicode(value)))                   \
                      for name, value in zip(self.updatefields,                \
               [getattr(self, attr) for attr in self.updatefields])])
          
        except  UnicodeDecodeError, UnicodeEncodeError:  
            #would like to pass here, but everything will probably burn - so give something a go!
            return ", ".join([u"`%s`='%s'" % (name, MySQLdb.escape_string(unicode(value, errors='replace')))      \
                      for name, value in zip(self.updatefields,                \
               [getattr(self, attr) for attr in self.updatefields])])
        
    def getupdatefieldsandvalues(self, desiredFields):
    

    
        self.updatefields = set(desiredFields).intersection(dir(self))
        
        values = []
        for name, value in zip(self.updatefields,                \
               [getattr(self, attr) for attr in self.updatefields]):
            values += [value]
        #print "\nGot these values", values
        return self.updatefields, values

    def InsertIntoDB_new(self, fieldnames=None, command="REPLACE", show_query="N"):
        """Makes MySQL insertion query using REPLACE and executes it.
        
        Changed to allow different insert commands (INSERT, INSERT IGNORE, etc)
        """
        
        
        
        if fieldnames is not None:
            fields, values = self.getupdatefieldsandvalues(
                desiredFields=fieldnames
            )            
        else:
            fields, values = self.getupdatefieldsandvalues(
                desiredFields=self.requiredFields + self.optionalFields
            )
        

        
        substitutionstring = ", ".join([field+"""=%s""" for field in fields])
        query = """%s INTO %s SET %s ; """ % (command, self.tablename, substitutionstring)
        
        if show_query == "Y": print query
        

        self.doSQL_new(query, values)
        
        #self.doSQL_new(
        #    """REPLACE INTO """+self.tablename+""" SET """ + \
        #    substitutionstring + ";",
        #    values)
            
            
            
                       
              
    def InsertIntoDB(self):
        """Generates an SQL query to put records into the database, and executes it. The method chosen is
        to use the REPLACE instruction. This means that if a row with the same primary key already exists in
        the database it will be overwritten so if you don't want bits overwritten you may well want to move 
        information into a different table.

        """

        
        querystring = """REPLACE INTO %s SET %s;""" % (
            self.tablename,
            self.getupdatefields(desiredFields=self.requiredFields + self.optionalFields)
        )
        

        self.doSQL(querystring)
    
    def RealInsertIntoDB(self, fieldnames):
        """Creates MySQL insertion query and executes it"""
        querystring = """INSERT INTO %s SET %s;""" % (
            self.tablename,
            self.getupdatefields(fieldnames)
        )
        # print "doSQL - this is the query\n", querystring
        self.doSQL(querystring)

    def updateDB_new(self, primary, **updates):

        self.populateKeywords(**updates)
        #print updates
        #print updates.keys()
        desiredFields = updates.keys()
        desiredFields.remove(primary)

        fields, values = self.getupdatefieldsandvalues(
            desiredFields=desiredFields
        )
        
        substitutionstring = ", ".join([field+"""=%s""" for field in fields])
        self.doSQL_new(
            """UPDATE """+self.tablename+""" SET """ + \
            substitutionstring +  \
            """ WHERE `"""+primary+"""`=%s;""",
            values + [updates[primary]])
    
    def updateDB(self, primary, **updates):
        """This method updates a set of fields in the database.
        You give it a set of field, value pairs and tell it which of those fields is the primary key.
        It then generates the SQL to use the primary key and value as a condition in the WHERE clause
        and all the other field, value pairs are updated.
        """
        self.populateKeywords(**updates)
        #print updates
        #print updates.keys()
        desiredFields = updates.keys()
        desiredFields.remove(primary)
        #print desiredFields
        querystring = """UPDATE %s SET %s WHERE `%s`='%s';""" % (
            self.tablename,
            self.getupdatefields(desiredFields=desiredFields),
            primary,
            updates[primary]
        )
        #print querystring
        self.doSQL(querystring)

    def doSQL(self, querystring):
        """This method just pulls together the dance steps to actually run a MySQL query against a database."""
        db = self.databaseConnection()
        cu = db.cursor()
        try:
            cu.execute(querystring)
        except:
            print repr(querystring)
        return cu.fetchall()
        cu.close()
        db.close()

    def doSQL_new(self, querystring, substitutions):
        """This method just pulls together the dance steps to actually run a MySQL query against a database."""
        db = self.databaseConnection()
        cu = db.cursor()
        results = []
        #print querystring, substitutions
        try:
            cu.execute(querystring, tuple(substitutions))
            results = cu.fetchall()
           
        except:
            print "\n\nFailed insert", repr(querystring % tuple([""" \"%s\" """ % item for item in substitutions])).encode("latin-1")
        return results
        cu.close()
        db.close()

    
    def FillTemplate(self):
        """This method uses the cheetah templating library to fill out a template with the values in the python
        object.
        
        The system is to create an instance of the template class, then copy all the attributes defined as
        required or optional fields across to the template class where they are referenced by placeholders
        in the template.
        
        In the process of doing this copying there is an option to call various services such as one which
        would replace extended characters with entity references or where the attribute is missing populate
        it with a default value.
        """
        assert self.templateclass
        t = self.templateclass()
        allfields = self.requiredFields + self.optionalFields
        if hasattr(self, 'xmlFields'):
            allfields += self.xmlFields
        for field in allfields:
            if hasattr(self, field):
                value = getattr(self, field)
                if hasattr(self, "entityconverter"):
                    if type(value) is unicode or type(value) is str:
                        value = getattr(self, "entityconverter").convert(value)
                    #print field
                    elif hasattr(value, "entityconvert"):
                        #print "got here test"
                        value.entityconvert()
                setattr(t, field, value)
            else:
                setattr(t, field, "unknown")
        return t.respond()
        del t
        
    def xml(self):
        """This method uses the amara module to return an xml representation of the object.
        For each attribute that has been defined as an optional or required field the method checks to see
        if the value of that attribute has an xml method and calls it if it does. Otherwise you just get value
        of the attribute.
        
        This is because record objects may have attributes which are themselves record sets. For example, an object
        may have an attribute 'subjects' whose value is a recordset object containing a set of subjects.
        
        Still to do here is the character encoding piece.
        """
        doc = amara.create_document() 
        container = doc.xml_append(
            doc.xml_create_element(
                unicode(self.__class__.__name__)
            )
        )
        
        allfields = []
        allfields += self.requiredFields
        if hasattr(self, 'optionalFields'):
            allfields += self.optionalFields
        if hasattr(self, 'xmlFields'):
            allfields += self.xmlFields
        
        for field in allfields:
            if hasattr(self, field):
                if hasattr(getattr(self, field), 'xml'):
                    innercontainer = container.xml_append(
                        doc.xml_create_element(
                            unicode(field)
                        )
                    )

                    innercontainer.xml_append(
                        getattr(self, field).xml()
                    )
                else:
                    content = getattr(self, field)
                    try:
                        content = unicode(content)
                    except UnicodeDecodeError:
                        content = content.decode('utf8')
                    except AttributeError:
                        pass
                    container.xml_append(
                        doc.xml_create_element(
                            unicode(field), content=content
                        )
                    )
        return container




    def generate_citations(self, out, databaseConnection, textsource="rawfile"):
        """Extract citations from your text and write to db or xml
        
        The 'out' is just a place holder for the moment - should be the name of the xml file - not yet implemented
        
        To do: 
        1. Add xml output
        2. Add control of output format
        
        There is a slight complication here in that PAIO and PQ objects hold their full text and ids in different places. 
        Also, since CitationRecordSet and CitationRecord are derived from base, the import needs to be done on the fly (I think).
       
       The database connection would normally be set already - sort that out.
       
        """
        from citations.holdall.citation import CitationRecordSet, CitationRecord
        
        
    
        #Get id if not already available as id attribute
        if not getattr(self, "id", None): 
            id = self.getID()
        else: id = self.id
        
        #this assumes that the candidates have already been loaded
        #clean up the flow on this switch
        if textsource == "candidatefile": 
            self.fulltext = "see candidate list - from base.generate_citations"
        

        
        
        
        
        #Get text if not already there
        if not getattr(self, "fulltext", None): 
            self.get_fulltext()
            #if hasattr(self, "rawtext"): 
                #print "This is the raw text", 
                #print self.rawtext.encode('latin-1')

        
                
        #The logic here is messy - could do with a tidy


           

        #Extract from relevant text section
        #Could fire off text population method if text missing...
        #This test is not right for loaded candidate set
        if getattr(self, 'fulltext', None) and not hasattr(self, "citations"):
            self.citations = CitationRecordSet(text = self.fulltext)        
        
        #pp.pprint(self.__dict__)     
        #pp.pprint(self.citations.__dict__)

        print "This is the list of citations"
        pp.pprint(self.citations)         

        if hasattr(self, "citations"):    
            
            
            
            #Pass over source info
            self.citations.sourceid = id  
            self.citations.source = self.tablename
            self.citations.databaseConnection = databaseConnection
            self.citations.generate_citations()      
            

            #Create the citations + write to db
            self.citations.reclassify() # turn into instance of relevant class
            
            #Propogate the database connection - this should be in the generate citations method
            for item in self.citations: 
                item.databaseConnection = databaseConnection
           
            
            self.citations.write_citations_to_db()  
            
            #Need to add some control here - if the record is a duplicate, or fails to write, don't write relship.
            #If a duplicate is overwritten, need to adjust relships - or could just do it in the final cleanup.
            self.citations.write_cites_rels_to_db()
            print "Citations extracted", len(self.citations)


    def load_candidates(self): 
        """Uses pre-extracted candidates saved to file. 
        Reads in each line as and stores in self.candidates. 
        Sets text to something (need this to be something to prevent loading of raw text
        
        This belongs in a generic journal record.
        
        """
        import codecs
        from citations.holdall.citation import CitationRecordSet, CitationRecord        
        path = "/dc/holdall/data/preprocessed/" #location of candidates files
        filename = self.id + ".txt"
        self.citations = CitationRecordSet()
        print "Candidate file", path + filename
        try:
            file = codecs.open(path + filename, "r", "latin-1")
            print path + filename
        except IOError: 
            print "No such candidate file"
            return   #with no candidates loaded this will usually default to looking at the raw text file
        
        
        lines = file.readlines()
        lines = [item for item in lines if not item.isspace()]  #cull empty lines
        #print "Lines", lines
        
     
        self.citations.candidates = lines
        self.citations.text = "see candidate list"
        self.text = "see candidate list"  #this is set as a switch to avoid fetching raw text later on