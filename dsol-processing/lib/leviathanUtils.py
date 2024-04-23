# -*- mode: python -*-

import collections
import lxml.etree as ET

from commonUtils.fileUtils import buildLut

def singleOccurOrder(rootxpath, dict):
    for element in rootxpath[0]:
        if element.tag in dict.keys():
            dict[element.tag].append(element)
            element.getparent().remove(element)
        else:
            print ET.tostring(rootxpath[0], pretty_print=True)
            print "\nNot found in dictionary: %s. Exiting..." % element.tag
            exit(1)

    for elementkey in dict.keys():
       for item in dict[elementkey]:
           rootxpath[0].append(item)
    
    return rootxpath
    
def multiOccurOrder(rootxpath, findall, dict):
    list = []
    try:
        for multi in rootxpath[0].findall('.//%s' % findall):
            for element in multi:
                if element.tag in dict.keys():
                    dict[element.tag].append(element)
                    element.getparent().remove(element)
                else:
                    print ET.tostring(rootxpath[0], pretty_print=True)
                    print "\nNot found in dictionary: %s. Exiting..." % element.tag
                    exit(1)

            multi.getparent().remove(multi)
            
            for elementkey in dict.keys():
                for item in dict[elementkey]:
                    multi.append(item)
                    dict[elementkey].remove(item)
        
            list.append(multi)
    
        for item in list:
            rootxpath[0].append(item)
        
        # print ET.tostring(rootxpath[0], pretty_print=True)
        return rootxpath
    except IndexError:
        pass
    



def levxml(data, contenttype, fieldlookup):

    fieldmatch = buildLut(fieldlookup, value_delimiter=',')

    document = ET.Element('document')
    record = ET.SubElement(document, 'record')
    recordsource = ET.SubElement(record, contenttype)

    for element in data:
        if element.text is not None and element.text.strip() is not '':
            try:
                if fieldmatch[element.tag][0].split('@')[1] is not None:
                    # print '1', fieldmatch[element.tag][0]
                    attrs = fieldmatch[element.tag][0].split('@')
                    child = ET.Element(fieldmatch[element.tag][0].split('@')[0])
                    child.text = element.text
                    for attr in attrs:
                        if '=' in attr:
                            child.attrib[attr.split('=')[0]] = attr.split('=')[1]
            except IndexError:
                # print '2', fieldmatch[element.tag][0]
                child = ET.Element(fieldmatch[element.tag][0])
                child.text = element.text
            except KeyError:
                pass

            try:
                if fieldmatch[element.tag][1] is not None:
                    try:
                        if fieldmatch[element.tag][1].split('@')[1] is not None:
                            parelement = ET.SubElement(recordsource, fieldmatch[element.tag][1].split('@')[0])
                            parelement.attrib[fieldmatch[element.tag][1].split('@')[1].split('=')[0]] = fieldmatch[element.tag][1].split('@')[1].split('=')[1]
                    except IndexError:
                        if recordsource.find(fieldmatch[element.tag][1]) not in recordsource:
                            parelement = ET.SubElement(recordsource, fieldmatch[element.tag][1])
                        else:
                            parelement = recordsource.find(fieldmatch[element.tag][1])

                    parelement.append(child)

            except IndexError:
                recordsource.append(child)

            except KeyError:
                pass
        else:
            pass

    if recordsource.find('contributor') in recordsource:
        contributors = ET.SubElement(recordsource, 'contributors')
        for item in recordsource:
            if item.tag == 'contributor':
                contributors.append(recordsource.find('contributor'))
    
    return document


def levorder(data, contenttype):
    altitlelist = []
 
    document = data.xpath('//document')
    parent = data.xpath('.//%s' % contenttype)

    levdict = collections.OrderedDict([('journalid', []),
                                       ('srcid', []),
                                       ('docid', []),
                                       ('accnum', []),
                                       ('supplement', []),
                                       ('country_of_publication', []),
                                       ('country_of_production', []),
                                       ('print_issn', []),
                                       ('elec_issn', []),
                                       ('peer_review', []),
                                       ('sectionheads', []),
                                       ('title', []),
                                       ('alternate_title', []),
                                       ('subhead', []),
                                       ('doctypes', []),
                                       ('nationality', []),
                                       ('birth_details', []),
                                       ('death_details', []),
                                       ('docfeatures', []),
                                       ('imagefeatures', []),
                                       ('contributors', []),
                                       ('subjects', []),
                                       ('production_roles', []),
                                       ('productions', []),
                                       ('series', []),
                                       ('volume', []),
                                       ('issue', []),
                                       ('pubdates', []),
                                       ('pagination', []),
                                       ('vendor', []),
                                       ('sourceinstitution', []),
                                       ('projectcode', []),
                                       ('languages', []),
                                       ('company', []),
                                       ('product', []),
                                       ('abstract', []),
                                       ('synopsis', []),
                                       ('scantype', []),
                                       ('notes', []),
                                       ('object_citations', [])])

    
    for element in parent[0]:
        if element.tag in levdict.keys():
            levdict[element.tag].append(element)
            element.getparent().remove(element)
        else:
            print "Not found in dictionary:", element.tag

    for elementkey in levdict.keys():
       for item in levdict[elementkey]:
           parent[0].append(item)
    
    return document[0]

def eeboutorder(data):
    document = data.xpath('//rec')
    rec_search = data.xpath('.//rec_search')
    author_main = data.xpath('.//author_main')
    itemimagefiles = data.xpath('.//itemimagefiles')
    volumeimagefiles = data.xpath('.//volumeimagefiles')

    itimlist = []
    vollist = []

    docdict = collections.OrderedDict([('itemid', []),
                                        ('subscription', []),
                                        ('rec_search', []),
                                        ('linksec', []),
                                        ('volumeimagefiles', []),
                                        ('itemimagefiles', [])
                                        ])

    imagedict = collections.OrderedDict([('itemimagefile1', []),
                                        ('volumeimagefile', []),
                                        ('order', []),
                                        ('imagenumber', []),
                                        ('orderlabel', []),
                                        ('pagecontent', []),
                                        ('colour', []),
                                        ('pagetype', [])
                                        ])
    
    authdict = collections.OrderedDict([('author_name', []),
                                        ('author_corrected', []),
                                        ('author_uninverted', []),
                                        ('lionid', []),
                                        ('author_isni', []),
                                        ('author_viaf', []),
                                        ('DoNotNormalize', []),
                                        ('last_name', []),
                                        ('first_name', []),
                                        ('middle_name', []),
                                        ('birth_date', []),
                                        ('death_date', []),
                                        ('professional_title', []),
                                        ('person_title', []),
                                        ('author_corporate', []),
                                        ('aut_cerl_mainentry', []),
                                        ('aut_other_cerl_mainentry', []),
                                        ('pub_cerl_mainentry', []),
                                        ('source', []),
                                        ('other_source', []),
                                        ('aut_cerl_variant', []),
                                        ('aut_other_cerl_variant', []),
                                        ('pub_cerl_variant', []),
                                        ('pop_cerl_mainentry', []),
                                        ('pop_cerl_variant', []),
                                        ('cop_cerl_mainentry', []),
                                        ('cop_cerl_variant', []),
                                        ('illustration', [])
                                        ])

    recserdict = collections.OrderedDict([('pqid', []),
				                       ('title', []),
				                       ('alt_title', []),
				                       ('uniform_title', []),
                                       ('author_main', []),
                                       ('author_other', []),
                                       ('aut_cerl', []),
                                       ('aut_other_cerl', []),
                                       ('startdate', []),
                                       ('enddate', []),
                                       ('displaydate', []),
                                       ('imprint', []),
                                       ('publisher_printer', []),
                                       ('pub_cerl', []),
                                       ('place_of_publication', []),
                                       ('pop_cerl', []),
                                       ('country_of_publication', []),
                                       ('cop_cerl', []),
                                       ('size', []),
                                       ('pagination', []),
                                       ('pages', []),
                                       ('ustc_bibliographic_reference', []),
                                       ('bibliographic_reference', []),
                                       ('shelfmark', []),
                                       ('general_note', []),
                                       ('content_note', []),
                                       ('edition_note', []),
                                       ('section_note', []),
                                       ('page_detail_note', []),
                                       ('incipit', []),
                                       ('explicit', []),
                                       ('source_library', []),
                                       ('source_collection', []),
                                       ('illustrations', []),
                                       ('subject', []),
                                       ('classifications', []),
                                       ('classification1', []),
                                       ('language', []),
                                       ('commentcode', []),
                                       ('ustc_number', []),
                                       ('ustc_link', [])
                                       ])


# author ordering
    multiOccurOrder(rec_search, 'author_main', authdict)
    multiOccurOrder(rec_search, 'author_other', authdict)

# rec_search ordering
    singleOccurOrder(rec_search, recserdict)

# itemimage ordering

    multiOccurOrder(itemimagefiles, 'itemimage', imagedict)

# volumeimage ordering

    multiOccurOrder(volumeimagefiles, 'volumeimage', imagedict)

#document ordering

    singleOccurOrder(document, docdict)

    return document[0]
