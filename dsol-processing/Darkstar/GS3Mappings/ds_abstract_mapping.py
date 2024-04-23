'''
  DataStore Abstract Mapping. All the general mapping functionality lives
  here and is inherited by our subclasses.
  
'''

import amara, re, os
from SequenceDict import SequenceDict
import DateConverter
from miscUtils import *
from EntityShield import *
from entityrefs import name2num

class DSAbstractMapping:
    ''' Common setup for all objects that live in the GSv3 format. '''
    def __init__(self, record):
        self.author_count = 0
        self.record = record

    def do_mapping(self):
        ''' This only creates a new amara document, stows it in the object
        as self.xmlDoc, and returns a two element list containing amara objects,
        one anchored at self.xmlDoc.RECORD.ControlStructure, the other at
        self.xmlDoc.RECORD.ObjectInfo. 
        All subclasses should know how to populate this document appropriately. 
        '''
        self.xmlDoc = amara.create_document(u'RECORD')
        return [self.xmlDoc.RECORD.xml_append(
                    self.xmlDoc.xml_create_element(u'ControlStructure')),
                self.xmlDoc.RECORD.xml_append(
                    self.xmlDoc.xml_create_element(u'ObjectInfo'))]
                    
                    
    def buildControlStructure(self, xmlCstruct):
        self.build_part(xmlCstruct, 'cs')
            
    def buildObjectInfo(self, xmlObject):
        self.build_part(xmlObject, 'oi')

    def build_part(self, what, prefix):
        ''' Look in self's dir() for methods named oi_* or cs_*. Call them in
        order. If you want to add more, make sure to adjust the number to
        get the order of output you want, and include them in the correct
        section! Numbers in the range 001-099 should be considered reserved
        for use in this module only. That leaves 100-999 for use in subclasses,
        which should, really, be enough! '''
        regex = re.compile(prefix+'_')
        for method in sorted([method for method in dir(self)
              if regex.match(method)]):
            eval('self.'+method+'(what)')
    
            
            
    def cs_001_add_ActionCode(self, xmlCstruct):
        actionCode = xmlCstruct.xml_create_element(u'ActionCode', content=u'add')
        xmlCstruct.xml_append(actionCode) 
            
    def cs_002_add_LegacyPlatform(self, xmlCstruct):
        legacyPlatform = xmlCstruct.xml_create_element(u'LegacyPlatform',
            content=u'CH')
        xmlCstruct.xml_append(legacyPlatform)
        
    def cs_003_add_LegacyID(self, xmlCstruct):
        legacyId = xmlCstruct.xml_create_element(u'LegacyID')
        xmlCstruct.xml_append(legacyId)
    
    def cs_011_insert_parent(self, xmlCstruct):
        xmlCstruct.xml_append(self.xmlDoc.xml_create_element(u'Parent'))
        
    def cs_012_insert_parentInfo(self, xmlCstruct):
        xmlCstruct.Parent.xml_append(self.xmlDoc.xml_create_element(u'ParentInfo'))
        
    def cs_013_insert_AlphaPubDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
            u'AlphaPubDate'))
   
    def cs_014_insert_RawPubDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
            u'RawPubDate'))
    
    def cs_015_insert_StartDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
            u'StartDate'))
            
    def Xcs_016_insert_EndDate(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
            u'EndDate'))
            
    def cs_017_insert_Volume(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
            u'Volume'))
    
    def cs_018_insert_Issue(self, xmlCstruct):
        xmlCstruct.Parent.ParentInfo.xml_append(self.xmlDoc.xml_create_element(
            u'Issue'))
            
    def cs_019_insert_PublicationInfo(self, xmlCstruct):
        xmlCstruct.xml_insert_after(xmlCstruct.LegacyID, self.xmlDoc.xml_create_element(u'PublicationInfo'))
    
    def cs_020_insert_LegacyPlatform(self, xmlCstruct):
        legacyPlatform = xmlCstruct.xml_create_element(u'LegacyPlatform',
            content=u'CH')
        xmlCstruct.Parent.ParentInfo.xml_insert_before(
            xmlCstruct.Parent.ParentInfo.AlphaPubDate, legacyPlatform)
        
    
            
    def cs_030_insert_Component(self, xmlCstruct):
        component = xmlCstruct.xml_create_element(u'Component',
            attributes={u'ComponentType':u'Citation'})
            
        representation = xmlCstruct.xml_create_element(u'Representation',
            attributes={u'RepresentationType':u'Citation'})
        mimetype = xmlCstruct.xml_create_element(u'MimeType', content=u'text/xml')
        resides = xmlCstruct.xml_create_element(u'Resides', content=u'FAST')
        representation.xml_append(mimetype)
        representation.xml_insert_after(mimetype, resides)
        component.xml_append(representation)
            
        xmlCstruct.xml_append(component)
        
    def Xcs_031_insert_ComponentRepresentation(self, xmlCstruct):
        representation = xmlCstruct.xml_create_element(u'Representation',
            attributes={u'RepresentationType':u'Citation'})
        xmlCstruct.Component.xml_append(representation)
        
    def Xcs_032_insert_MimeType(self, xmlCstruct):
        mimetype = xmlCstruct.xml_create_element(u'MimeType', content=u'DsolFIXME')
        xmlCstruct.Component.Representation.xml_append(mimetype)
        
    def Xcs_033_insert_Resides(self, xmlCstruct):
        resides = xmlCstruct.xml_create_element(u'Resides', content=u'DsolFIXME')
        xmlCstruct.Component.Representation.xml_append(resides)
        
    def oi_001_insert_Title(self, xmlObject):
        xmlObject.xml_append(self.xmlDoc.xml_create_element(u'Title'))
        
    def oi_002_insert_Title_cht(self, xmlObject):
        titleCht = xmlObject.xml_create_element(u'cht')
        xmlObject.Title.xml_append(titleCht)
        
    def oi_003_insert_legacyProductMapping(self, xmlObject):
        legacyProductMapping = xmlObject.xml_create_element(u'LegacyProductMapping')
        groupName = xmlObject.xml_create_element(u'GroupName')
        legacyProductMapping.xml_append(groupName)
        xmlObject.xml_insert_before(xmlObject.Title, legacyProductMapping)
        
    def oi_010_insert_Language(self, xmlObject):
        for lang in self.languages():
            langElem = xmlObject.xml_create_element(u'Language')
            
            if lang == '':
                lang = u"Undefined"
            #elif re.match("French-based", lang):
            #    lang = u"Creoles and Pidgins, French-based"
            
            rawLangElem = xmlObject.xml_create_element(u'RawLang',
                content = lang)
            
            isoElem = xmlObject.xml_create_element(u'ISO')
            isoCodeElem = xmlObject.xml_create_element(u'ISOCode',
                content = self.lang_iso(lang))
            isoElem.xml_append(isoCodeElem)
            
            langElem.xml_append(rawLangElem)
            langElem.xml_append(isoElem)
            
            xmlObject.xml_append(langElem)
        
    def oi_015_insert_Copyright(self, xmlObject):
        copyright = xmlObject.xml_create_element(u'Copyright')
        copyrightData = xmlObject.xml_create_element(u'CopyrightData')
        copyrightCht = xmlObject.xml_create_element(u'cht')
        #copyrightVsmark = xmlObject.xml_create_element(u'vsmark')
        copyrightData.xml_append(copyrightCht)
        #copyrightData.xml_append(copyrightVsmark)
        copyright.xml_append(copyrightData)
        #xmlObject.xml_insert_after(xmlObject.Language, copyright)
        xmlObject.xml_append(copyright)
        
    def oi_022_insert_PrintLocation(self, xmlObject):
        xmlObject.xml_insert_after(xmlObject.Copyright, self.xmlDoc.xml_create_element(u'PrintLocation'))
    
    def oi_023_insert_Pagination(self, xmlObject):
        xmlObject.PrintLocation.xml_append(self.xmlDoc.xml_create_element(u'StartPage'))
        xmlObject.PrintLocation.xml_append(self.xmlDoc.xml_create_element(u'EndPage'))
        xmlObject.PrintLocation.xml_append(self.xmlDoc.xml_create_element(u'Pagination'))
        
        
    def oi_034_insert_Contributors(self, xmlObject):
        xmlObject.xml_append(self.xmlDoc.xml_create_element(u'Contributors'))
    
    def oi_045_insert_ObjectIds(self, xmlObject):
        xmlObject.xml_insert_after(xmlObject.PrintLocation, xmlObject.xml_create_element(u'ObjectIds'))
        
    def oi_056_insert_Abstracts(self, xmlObject):
        xmlObject.xml_append(self.xmlDoc.xml_create_element(u'Abstracts'))
    
    '''----------------------------------------------------------------------'''

    ''' A simple helper method to handle date conversions '''
    def helper_normalise_date(self, datestring):
        day, months, seasons, year, quarters = self.set_regexes()
        #if re.search(r'^\d{1,2} [A-Za-z]{3,} \d{4}-\d{1,2} [A-Za-z]{3,} \d{4}', datestring):
        if datestring == "n.d.":
            return u"Jan 1, 1111"
        elif re.search(r'^n\.d\.[- ]' + year + '$', datestring):
            return re.search(r'^n\.d\.[- ](' + year + ')$', datestring).group(1)
        elif re.search(r'^n\.d\.[- ]\(' + year + '\)$', datestring):
            return re.search('^n\.d\.[- ]\((' + year + ')\)$', datestring).group(1)
        elif re.search(r'^' + months + ' \[' + year + '\]$', datestring):
            m, y = re.search(r'^(' + months + ') \[(' + year + ')\]$', datestring).group(1, 2)
            return DateConverter.conv_my_pqan(m + ' ' + y)
        elif re.search(r'^' + day + ' ' + months + ' ' + year + '-' + day + ' ' + months + ' ' + year, datestring):
            date1, date2 = datestring.split('-')
            return DateConverter.conv_dmy_pqan(date1) + '-' + DateConverter.conv_dmy_pqan(date2)
        elif re.search(r'^' + months + ' *' + year + '$', datestring):
            m, y = re.search('^(' + months + ') *(' + year + ')', datestring).group(1, 2)
            return DateConverter.conv_my_pqan(m + ' ' + y)
        elif re.search(r'^' + months + ' ' + year + '/' + year + '$', datestring):
            m, y = re.search(r'^(' + months + ') (' + year + ')/' + year +'$', datestring).group(1, 2)
            return DateConverter.conv_my_pqan(m + ' ' + y)
        elif re.search(r'^' + months + ' ?-' + months + ' ?' + year, datestring):
            m, y = re.search('^(' + months + ').*(' + year + ')$', datestring).group(1, 2)
            return DateConverter.conv_my_pqan(m + ' ' + y)
        elif re.search(r'^' + seasons + ' ' + year + '$', datestring):
            return DateConverter.conv_season2pqan(datestring)
        elif re.search(r'^' + seasons + '[/-]' + seasons + ' ' + year + '$', datestring):
            return datestring
        elif re.search(r'^' + seasons + ' ' + year + '-' + year + '$', datestring):
            return DateConverter.conv_season2pqan(datestring)
        elif re.search(r'^' + seasons + ' ' + year + '-' + seasons + ' ' + year + '$', datestring):
            s, y = re.search(r'^(' + seasons + ') (' + year + ')-' + seasons + ' ' + year + '$', datestring).group(1, 2)
            return DateConverter.conv_season2pqan(s + ' ' + y)
        elif re.search(r'^' + seasons + '-' + year + ':' + seasons + ' ' + year + '$', datestring):
            s, y = re.search(r'^(' + seasons + ')-.*(' + year + ')$', datestring).group(1, 2)
            return DateConverter.conv_season2pqan(s + ' ' + y)
        #elif re.search(r'^' + seasons + ' ' + year + '/' + year '$', datestring):
        elif re.search(r'^' + day + ' ' + months + ' ' + year + '$', datestring):
            return DateConverter.conv_dmy_pqan(datestring)
        elif re.search(r'^' + months + ' ' + day + ',? ' + year + '$', datestring):
            return DateConverter.conv_mdy_pqan(datestring)
        elif re.search(r'^' + months + ' ' + year + '[/-]' + months + ' ' + year + '$', datestring):
            date1, date2 = re.split('[/-]', datestring)
            return DateConverter.conv_my_pqan(date1) + '-' + DateConverter.conv_my_pqan(date2)
        elif re.search(r'^' + months + ' ' + year + '$', datestring):
            return DateConverter.conv_my_pqan(datestring)
        elif re.search(r'^' + months + ' ?/ ?' + months + ' \d{4}', datestring):
            datestring = datestring.replace(' /', '/')
            months, year = datestring.split(' ')
            month1, month2 = months.split('/')
            retval = DateConverter.num_to_abbrev(DateConverter.name_to_num(month1[:3]))
            retval += '/'
            retval += DateConverter.num_to_abbrev(DateConverter.name_to_num(month2[:3]))
            retval += ', ' + year
            return retval
        elif re.search(r'^' + months + ' ?- ?' + months + ' ?\d{4}', datestring):
            months, year = datestring.split(' ')
            month1, month2 = months.split('-')
            retval = DateConverter.num_to_abbrev(DateConverter.name_to_num(month1))
            retval += '-'
            retval += DateConverter.num_to_abbrev(DateConverter.name_to_num(month2))
            retval += ', ' + year
            sys.stderr.write(retval + ' --- ' + datestring)
            return retval
        elif re.search(r'^' + year + '$', datestring):
            return datestring
        elif re.search(r'^' + year + '-' + months + ' \d{2}$', datestring):
            y, m = re.search(r'^(' + year + ')-(' + months + ') \d{2}$', datestring).group(1, 2)
            return DateConverter.conv_my_pqan(m + ' ' + y)
        elif re.search(r'^' + year + '-' + year + '$', datestring):
            return ('/').join(datestring.split('-'))
        elif re.search(r'^' + year + ', ' + year + '$', datestring):
            return ('/').join(datestring.split(', '))
        elif re.search(r'^' + year + '/' + year + '$', datestring):
            return datestring
        elif re.search(r'^' + seasons + '\] *\[' + year, datestring):
            s, y = re.search(r'^(' + seasons + ')\] *\[(' + year + ')', datestring).group(1, 2)
            return DateConverter.conv_season2pqan(s + ' ' + y)
        elif re.search(r'^' + quarters + ' ' + year + '$', datestring):
            return DateConverter.quarter2pqan(datestring)
        elif re.search(r'^Holiday ' + year + '$', datestring):
            return DateConverter.conv_my_pqan(datestring.replace('Holiday', 'December'))
        elif re.search('^' + day + '\d?$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^' + day + ' ' + months + ' ' + day + '$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^' + seasons + ' | ' + day + '$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^' + seasons + '[- /]' + seasons + ' ' + year + '$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^' + months + ' |  ' + day + '[0-9]?$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^' + months + '[- /]' + months + ' ' + day + '$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^\d{,3}-\d{,3}$', datestring):
            return u"Jan 1, 1111"
        elif re.search(r'^\d \d{4}$', datestring):
            return re.search(r'^\d (\d{4})$', datestring).group(1)
        elif re.search(r'^' + year + '-' + year + ' Nueva .*$', datestring):
            return re.search(r'^(' + year + ').*$', datestring).group(1)
        else:
            return datestring
            
    def pq_numeric_date(self, datestring):
        day, months, seasons, year, quarters = self.set_regexes()
        ''' datestring should be a ProQuest standardised alpha-numeric string '''
        if re.search(r'^\[?\d{4}\]?$', datestring):
            return DateConverter.year_only(re.sub(r'\[|\]', '', datestring))
        elif re.search(r'^' + seasons + ' ' + year + '$', datestring):
            return DateConverter.conv_season(datestring)
        elif re.search(r'^' + seasons + ' \[' + year + '\]$', datestring):
            return DateConverter.conv_season(re.sub('\[|\]', '', datestring))
        elif re.search(r'^' + seasons + ' ' + year + '-' + year + '$', datestring):
            return DateConverter.conv_season(datestring.split('-')[0])
        elif re.search(r'^' + seasons + ' ' + year + '/' + year + '$', datestring):
            return DateConverter.conv_season(datestring.split('/')[0])
        elif re.search(r'^' + seasons + '/' + seasons + ' ' + year + '/' + year + '$', datestring):
            s, y = re.search(r'^(' + seasons + ')/[A-Za-z]+ (' + year + ')/\d{4}$', datestring).group(1, 2)
            return DateConverter.conv_season(s + ' ' + y)
        elif re.search(r'^' + seasons + '/' + seasons + ' ' + year, datestring):
            return DateConverter.conv_season_double(datestring)
        elif re.search(r'^' + seasons + '-' + seasons + ' ' + year + '$', datestring):
            return DateConverter.conv_season_multiple(datestring)
        elif re.search(r'^' + seasons + '-' + seasons + ' ' + year + '-' + year + '$', datestring):
            s = datestring.split(' ')[0].split('-')[0]
            y = datestring.split(' ')[1].split('-')[0]
            return DateConverter.conv_season(s + ' ' + y)
        elif re.search(r'^' + seasons + ' ' + year + '-' + seasons + ' ' + year + '$', datestring):
            return DateConverter.conv_season(datestring.split('-')[0])
        elif re.search(r'^' + seasons + '/' + seasons + '-' + year + ':' + seasons + '/' + seasons + ' ' + year + '$', datestring):
            s, y = re.search(r'^(' + seasons +').*(' + year + ')$', datestring).group(1, 2)
            return DateConverter.conv_season(s + ' ' + y)
        elif re.search(r'^' + months + ' ' + day + ',? ' + year + '-' + months + ' ' + day + ',? ' + year, datestring):
            return DateConverter.conv_mdy(datestring.split('-')[0])
        elif re.search(r'^' + months + ' ' + day + ',? ' + year + '$', datestring):
            return DateConverter.conv_mdy(datestring)
        elif re.search(r'^' + day + ' ' + months + ' ' + year + '$', datestring):
            return DateConverter.conv_dmy(datestring)
        elif re.search(r'^' + months + '[-/]' + months + ' ' + year + '$', datestring):
            month, year = re.search(r'([A-Za-z]+)[-/][A-Za-z]+,? (\d{4})', datestring).group(1,2)
            return DateConverter.conv_my(month + ' ' + year)
        elif re.search(r'^\[?' + months + '\]? ' + year + '$', datestring):
            return DateConverter.conv_my(re.sub(r'\[|\]', '', datestring))
        elif re.search(r'^' + months +'-' + year + ':' + months + ' ' + year, datestring):
            m, y = re.search('^(' + months + ').*(' + year + ')$', datestring).group (1, 2)
            return DateConverter.conv_my(m + ' ' + y)
        elif re.search(r'^' + months + ' ' + year + '[-/]' + months + '( ' + year + ')?', datestring):
            return DateConverter.conv_my(re.search(r'([A-Za-z]+ \d{4}).*', datestring).group(1))
        elif re.search(r'^' + year + '/' + year + '$', datestring):
            return DateConverter.year_only(datestring)
        elif re.search(r'^' + quarters + ' ' + year + '$', datestring):
            return DateConverter.quarter(datestring)
        #elif re.search('^' + months + '-' + months + year, datestring):
        #    m, y = re.search('^(' + months + ').*(\d{4})', datestring).group(1, 2)
        #    return DateConverter.conv_my(m + ' ' + y)
        else:
            import sys
            sys.stderr.write(datestring)
            return u'FIXME - ' + unicode(datestring)
        
    def set_regexes(self):
        return [u'\d{1,2}', u'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[,.]?',
                u'(?:Spr(?:ing)?|Sum(?:mer)?|Autumn|Fall?|Win(?:ter)?)', u'\d{4}',
                u'(?:First|Second|Third|Fourth)(?: Quarter)?']
        
        
    def helper_startPage(self, paginationString):
        if paginationString == '': return u''
        return unicode(re.match('^[A-Za-z0-9]{1,}', paginationString).group(0))
        
        # Not required at this stage.
        #match = re.match('^[iIvVxXlLcCdDmM]+', paginationString)
        #if match:
        #    pageNumber = get_roman(match.group(0))
        #elif re.match(r'^[0-9]+', paginationString):
        #    pageNumber = re.match(r'^[0-9]+', paginationString).group(0)
        #else:
        #    pageNumber = ''
        #return pageNumber
        
    def helper_endPage(self, paginationString):
        if paginationString == '': return u''
        return unicode(re.search(r'([A-Za-z0-9]{1,})[? .,+_-]*$', paginationString).group(1) if paginationString else u'')
        
        # Not required at this stage.
        #match = re.search('[iIvVxXlLcCdDmM]+$', paginationString)
        #if match:
        #    pageNumber = get_roman(match.group(0))
        #elif re.search(r'[0-9]+$', paginationString):
        #    pageNumber = re.search(r'[0-9]+$', paginationString).group(0)
        #else:
        #    pageNumber = ''
        #return unicode(pageNumber)
        
        
        
    def contributor_template(self, contrRoleName, contrData):
        ''' Since we might need an unpredictable number of these in any given
        record, it is safer to construct the whole thing as a string and have
        amara parse it as a fragment - it means that we are always assured of
        having the attributes added to the right tags, without having to worry
        about indexing the Contributor and ContribData tags. '''
        
        doc_frag = self.xmlDoc.xml_create_element(u'Contributor',
            attributes = {u'RoleName':unicode(contrRoleName)})
        for k,v in contrData.items():
            doc_frag.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator':unicode(k)},
                content = unicode(v)))
        if contrRoleName == "Author":
            doc_frag.xml_append(self.xmlDoc.xml_create_element(u'ContribData',
                attributes={u'MarkupIndicator':u'AuthorOrder'},
                content = unicode(str(self.author_count))))
        return doc_frag
        
    def component_template(self):
        component = self.xmlDoc.xml_create_element(u'Component',
            attributes = {u'ComponentType':u'Abstract'})
        representation = self.xmlDoc.xml_create_element(u'Representation',
            attributes = {u'RepresentationType':u'Abstract'})
        mimetype = self.xmlDoc.xml_create_element(u'MimeType', content = u'text/xml')
        resides = self.xmlDoc.xml_create_element(u'Resides', content = u'FAST')
        representation.xml_append(mimetype)
        representation.xml_append(resides)
        component.xml_append(representation)
        return component
        
        
    def add_fulltext_components(self, fullTextData, pqid):
        for representation in fullTextData.xml_xpath(
            '//Component[@ComponentType="FullText"]/Representation'):
            component = self.xmlDoc.xml_create_element(u'Component',
                attributes = {u'ComponentType':u'FullText'})
            if "PDFFullText" in representation.xml_properties.values():
                component.xml_append(self.make_CHImageIds_elem(pqid))
            component.xml_append(representation)
            self.xmlDoc.RECORD.ControlStructure.xml_append(component)
            
    def add_graphics_components(self, fullTextData, pqid):
        for inlineImage in fullTextData.xml_xpath(
            '//Component[@ComponentType="InlineImage"]'):
            if 'ObjectSeqNumber' in inlineImage.xml_child_elements:
                inlineImage.xml_insert_after(inlineImage.ObjectSeqNumber,
                    self.make_CHImageIds_elem(pqid))
            else:
                inlineImage.xml_insert_after(inlineImage.InlineImageCount,
                    self.make_CHImageIds_elem(pqid))
            self.xmlDoc.RECORD.ControlStructure.xml_append(inlineImage)
            
            
    def make_CHImageIds_elem(self, pqid):
        chimageids = self.xmlDoc.xml_create_element(u'CHImageIds')
        pqid = self.xmlDoc.xml_create_element(u'pqid', content = pqid)
        chimageids.xml_append(pqid)
        return chimageids

    def mappingClass(self):
        return str(self.__class__)


    def language(self):
        if self.record.documentlanguage:
            return self.record.documentlanguage
        else:
            return self.record.language

    def languages(self):
        return str_to_list(self.language(), self.lang_delimiter())
            
    def lang_iso(self, lang):
        return unicode(lang_to_iso(lang))


    def to_list(self, string, delimiter=None, maxsplit=-1):
        list = [word.lstrip() for word in string.split(delimiter, maxsplit)]
        return list
        
    ''' Any string can be passed through this to replace entity references with 
    their UTF-8 equivalent. It handles both named refs ('&eacute;') and numeric 
    refs ('&#233;'), provided there is a mapping in the list of known entities.
    In the case of no mapping, we output '???', and print the offending entity to
    a file for later consideration. '''
    def replace_entityrefs(self, string):
        numentrefre = re.compile('&#(\d+);')
        entrefnamere = re.compile('(&[A-Za-z0-9]+;)')
        rstring = unprotect(string)
        matches = entrefnamere.search(rstring)
        if matches:
            if matches.group(0) in name2num.keys():
                rstring = entrefnamere.sub(lambda match: name2num.get(match.group(0)), rstring)
            else:
                rstring = entrefnamere.sub(lambda match: u'???', rstring)
                enterrors = open(os.path.expanduser('~') + '/entreferrors.txt', 'a')
                print >>enterrors, matches.group(0)
                enterrors.close()
        return numentrefre.sub(lambda match: unichr(int(match.group(1))), rstring)
            

