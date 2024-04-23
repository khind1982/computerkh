# -*- mode: python -*-

import collections
import lxml.etree as ET

from commonUtils.fileUtils import buildLut


def levxml(data, contenttype, fieldlookup):

    fieldmatch = buildLut(fieldlookup, value_delimiter=',')

    document = ET.Element('document')
    record = ET.SubElement(document, 'record')
    recordsource = ET.SubElement(record, contenttype)

    for element in data:
        if element.text is not None and element.text.strip() is not '':
            try:
                if fieldmatch[element.tag][0].split('@')[1] is not None:
                    attrs = fieldmatch[element.tag][0].split('@')
                    child = ET.Element(fieldmatch[element.tag][0].split('@')[0])
                    child.text = element.text
                    for attr in attrs:
                        if '=' in attr:
                            child.attrib[attr.split('=')[0]] = attr.split('=')[1]
            except IndexError:
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
            print("Not found in dictionary:", element.tag)

    for elementkey in levdict.keys():
       for item in levdict[elementkey]:
           parent[0].append(item)

    return document[0]
