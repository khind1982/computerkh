# -*- mode: python -*-

import collections
import lxml.etree as ET

from commonUtils.fileUtils import buildLut

# Utility for reordering the fields inside a single occurring parent xml tag
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

# Utility for reordering the fields inside a multiply occurring parent xml tag
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

# Utility to retrieve the text of a tag if it exists, otherwise return an empty string.
def presenceTestSingle(element):
    if element is not None and element.text is not None:
        return element.text
    else:
        return ''



