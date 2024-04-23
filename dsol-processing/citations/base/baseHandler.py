import amara
from mod_python import apache, util

def handler(req):
    """This is the main function that apache calls.
    What it does is just check the username again because we might need it at a later point
    and then creates an instance of the action class. And then it gets XML content back
    from the action class"""
    req.content_type = 'text/xml'
    #pw = req.get_basic_auth_pw()
    #user = req.user
    myaction = action(util.FieldStorage(req))
    req.write(myaction.getXML().xml())
    return apache.OK    
        
class action:
    """This is the class for all the actions performed by the server. It's main purpose is to return some XML."""

    def __init__(self, fields):
        self.fields = fields
        self.doc = amara.create_document()
        self.initSpecifics()

    def initSpecifics(self):
        """Override this method on a product-by-product basis."""
        # import xyz
        self.recordsetclass = None
        self.tablename = None
        self.recordclass = None

    def getXML(self):
        """The idea is to return some XML but we also want to render it into HTML for the user interface.
        The way this is done is to supply the stylesheet location as a processing instruction.
        To make changes to the way the XML is interpreted and ultimately displayed the thing to do is to
        make changes to the stylesheet and css respectively."""
       
        stylesheet = 'default.xsl'
        
        if self.fields.has_key('xsl'):
            if self.fields['xsl'].endswith('.xsl'):
                stylesheet = self.fields['xsl']

        if not self.fields.has_key('xml'):
            pi = amara.bindery.pi_base(u"xml-stylesheet", u'href="'+stylesheet+'" type="text/xsl"')
            self.doc.xml_append(pi)

        self.doc.xml_append(self.doc.xml_create_element(u"response"))
        self.DoResponseSpecifics()
        
        self.fielddict = {}
        for key in self.fields.keys():
            self.fielddict[key] = self.fields[key]
        
        #assert self.fielddict
        if self.fields.has_key('action'):
            if hasattr(self, self.fields['action']):
                getattr(self, self.fields['action'])()
            else:
                self.DoDefaultAction(self.fields['action'])

        self.doc.response.xml_append(
            self.doc.xml_create_element(u"parameters")
        )
        
        for key in self.fields.keys():
            if type(self.fields[key]) is list:
                for item in self.fields[key]:
                    self.doc.response.parameters.xml_append(
                        self.doc.xml_create_element(unicode(key), content=unicode(item))
                    )                
            else:
                self.doc.response.parameters.xml_append(
                    self.doc.xml_create_element(unicode(key), content=unicode(self.fields[key]))
                )
        
        return self.doc

    def DoResponseSpecifics(self):
        self.doc.response.xml_append(
            self.doc.xml_create_element(u"recordset", content=unicode(self.recordsetclass.__name__))
        )
        self.doc.response.xml_append(
            self.doc.xml_create_element(u"record", content=unicode(self.recordclass.__name__))
        )
        self.doc.response.xml_append(
            self.doc.xml_create_element(u"tablename", content=unicode(self.tablename))
        )
    
    def DoDefaultAction(self, action):
        """This is essentially the do-nothing version of the action.
        You get back XML with just one element and therefore whatever is displayed by default by the stylesheet."""
        self.doc.response.xml_append(self.doc.xml_create_element(action))

    def search(self):
        """This method creates the XML for a set of search results. You need to have the title field defined in
        the request because that's what it uses to do the search.
        But in practice title is a bit misleading because it searches over volume and author fields too.
        It calls separate functions to bring back the search results and another function to bring back genres
        assigned to each of those search results.
        """
        # Get the search results
        
        self.PopulateSearchResultSet()
        self.doc.response.xml_append(self.doc.xml_create_element(u"search"))
        self.doc.response.search.xml_append(self.doc.xml_create_element(u"results"))
        
        self.doc.response.search.results.xml_append(self.resultset.xml())

    def MultiSearchResultSet(self):
        """This method populates the search result set by iterating over a list of views
        rather than restricting itself to just one table."""
        self.resultset = self.recordsetclass()
        for view in self.views:
            self.resultset.tablename = view
            self.resultset.recordclass = self.recordclass
            self.resultset.indexsearch(**self.fielddict)        
    
    def PopulateSearchResultSet(self):
        """Methods in a subclass may prefer to call this rather than search so that they can
        do some postprocessing of their own before returning the xml."""
        self.resultset = self.recordsetclass()
        self.resultset.tablename = self.tablename
        self.resultset.recordclass = self.recordclass
        self.resultset.indexsearch(**self.fielddict)
    
    def PopulateFullRecordSet(self):
        self.resultset = self.recordsetclass()
        self.resultset.tablename = self.tablename
        self.resultset.recordclass = self.recordclass
        self.resultset.keysearch(**self.fielddict)
    
    def fullRecord(self):
        """This method creates the XML for a full view of a particular record. What you get here is basically the
        same as you got for the search result except there's only one. But you also get a list of all the available
        genres.
        The thing to note is that the actual display of the fullrecord with all the buttons and whatnot is mainly
        handled by the stylesheet.
        """

        # Get the search results
        self.PopulateFullRecordSet()
        self.doc.response.xml_append(self.doc.xml_create_element(u"fullRecord"))
        self.doc.response.fullRecord.xml_append(self.resultset[0].xml())

    def updateRecord(self):
        resultset = self.recordsetclass()
        resultset.tablename = self.tablename
        resultset.recordclass = self.recordclass
        
        resultset.getdbindexes()
        resultset.getdbfields()
        
        # Filter out parameters which don't correspond to fieldnames in the target table
        editdict = {}
        for key in self.fields.keys():
            if key in resultset.fieldnames:
                editdict[key] = self.fields[key]
        
        temprecord = self.recordclass()
        temprecord.tablename = self.tablename
        temprecord.updateDB(primary=resultset.primary.pop(), **editdict)
        self.fullRecord()

class ajaxAction(action):
    """This is a subclass for ajax-type responses which probably want a good deal less information passed 
    in the xml."""
    def getXML(self):
        self.doc.xml_append(self.doc.xml_create_element(u"response"))
        if self.fields.has_key('action'):
            if hasattr(self, self.fields['action']):
                getattr(self, self.fields['action'])()
            else:
                self.DoDefaultAction(self.fields['action'])
        return self.doc
        