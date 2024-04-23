import os, re, EntityShield
from amara import binderytools
from GS3Mappings.proxy_mapping import ProxyMapping

class AbstractParser:
    '''Split the given document into chunks at the level of the given element.
    
    Takes an XML document, and splits it into a parsed tree of amara objects,
    split around the specified +element+ argument.
    
    The document to split and the element to split on is provided by our
    subclasses' call up to __init__.
    '''
    def __init__(self, document, element):
        self.records = []
        if os.path.exists(document):
            '''Run the input file through the EntityShield.protect function to
            keep us safe from any unicode stuff. We don't do this inplace - that's
            just nasty.'''
            EntityShield.protectFile(document)
            self.do_binding(document, element)
            EntityShield.unprotectFile(document)
        elif type(document) is str:
            ''' In case we just get given a string '''
            self.do_binding(document, element)
        else:
            print "File " + document + " does not exist"

    def do_binding(self, document, element):
        for elem in binderytools.pushbind(document, element):
            self.records.append(elem)
            #record_type = self.__class__
            
            
class AbstractRecord:
    '''Take each record from a parsed AbstractParser object and do stuff to it.
    
    __init__ requires the parsed document and a list of  XPath compatible paths.
    Sets up a __getitem__ method so we can easily address the data from subclasses
    by iterating over the list of field XPaths.
    '''
    def __init__(self, parsedDoc, fields):
        self.parsedDoc = parsedDoc
        self.fields = fields
        
        if fields.__class__ is not list:
            print "'fields' parameter should be a list"
        
        self.extractedData = {}
        
        for field in fields:
            '''Store the extracted data, and define a simple method to retrieve
            it from the object. Metaprogramming, in Python? Nah.'''
            self.extractedData[field] = parsedDoc.xml_xpath(field)
            
            '''Get the last purely alphabetic sequence of letters from the XPath 
            specification, and use that as the name of the attribute to define
            on the object. This is essentially just a short-hand way of saying the
            more verbose thing.extractedData[XPath] '''
            meth = [thing for thing in re.split('[^a-zA-Z_]', field) if thing][-1]
            def extract(self, field):
                return unicode(self.__getitem__(field))
            
            setattr(self, meth, extract(self, field))

    ''' Return a stringified representation of the xpath data '''
    def __getitem__(self, key): 
        if self.extractedData[key]:
            return self.extractedData[key][0]
        else:
            return u''

