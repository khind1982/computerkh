#!/usr/local/bin/python2.7

"""This module is for one-off data cleanup functions that
can be applied to the Innodata cache for IIMP and IIPA.

"""
import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/python'))

from innodata_cache_reader import innodata_cache_reader, update_cache

def apply_all_fixes(cachepath):

    fixlist = [
            remove_top_of_page_links,
            remove_duplicate_image_components
            ]

    for recpath, recdata in innodata_cache_reader(cachepath, printfiles=True):
        for fix in fixlist:
            recdata = fix(recdata)
        #recdata = specific_record_fixes(recpath, recdata)
        update_cache(recpath, recdata)    
    
def specific_record_fixes(recpath, recdata):
    """Apply specific fixes to records that no other existing function
    fixes. This tests whether the current record is a known problem
    record and if so applies the relevant fix.
    
    Currently redundant - previous fixes to be applied by this are
    now covered by remove_duplicate_image_components.
    
    """
    
    # 483191_1: remove a duplicated component
    #if os.path.basename == '483191_1':
    #    if len(recdata[0]) == 3:
    #        del recdata[0][1]
            
    # 129819: remove a duplicated component
    #if os.path.basename == '129819':
    #    if len(recdata[0]) == 46:
    #        del recdata[0][30]
                        
    return recdata

def _set_inlineimagecount(components):

    inlineimagecount = unicode(len([c for c in components
                                if c[u'ComponentType'] == u'InlineImage']))
    for c in components:
        if c[u'ComponentType'] == u'InlineImage':
            c[u'InlineImageCount'] = inlineimagecount

def remove_top_of_page_links(recdata):
    """Remove the 'top of page' text and the two surrounding images
    from Innodata records that still have them in.
    
    Remove these directly from the full text section, and update the
    components section to match.
     
    """
    
    #Try to make the regex to match Top of Page links intelligible
    #by breaking it down into constituent parts.
    paramregex = '<param[^<]+</param>'
    objectregex = '<object class="mstar_link_to_media">(%s)+</object>' \
                                                            % paramregex
    
    toplinkre = re.compile('%s\s*Top of Page\s*%s'
                                        % (objectregex, objectregex))
                                
    endre = re.compile('<center>\s*<h3>\s*END\s*</h3>\s*</center>', re.I|re.S)
    
    ft = recdata[1]['fullText']['value']
    ft, linksremovedcount = toplinkre.subn('', ft)
    ft = endre.sub('', ft)
    recdata[1]['fullText']['value'] = ft
    
    #only look at components if change occurred in ft
    components = recdata[0]
    if linksremovedcount > 0:
        components = [c for c in components
                if c[u'ComponentType'] != u'InlineImage'
                or c[u'InnoImgReprs'][u'values'][u'MediaKey']
                != u'/media/ch/iimpa/images/ch/iimpft/images/top.gif']
        
        _set_inlineimagecount(components)
        
        #inlineimagecount = unicode(len([c for c in components
        #                        if c[u'ComponentType'] == u'InlineImage']))
        #for c in components:
        #    if c[u'ComponentType'] == u'InlineImage':
        #        c[u'InlineImageCount'] = inlineimagecount
    
    return components, recdata[1]
    
def remove_duplicate_image_components(recdata):
    """If any image component contains the same image link as an
    earlier component in the same record, remove it.
    
    """
    
    imagepaths = {}
    deduped_components = []
    for comp in recdata[0]:
        if comp[u'ComponentType'] == u'InlineImage':
            imagepath = comp[u'InnoImgReprs'][u'values'][u'MediaKey']
            if not imagepath in imagepaths:
                imagepaths[imagepath] = ''
                deduped_components.append(comp)
        else:
            deduped_components.append(comp)
    _set_inlineimagecount(deduped_components)
    return deduped_components, recdata[1]
        
    
if __name__ == '__main__':

    apply_all_fixes(sys.argv[1])