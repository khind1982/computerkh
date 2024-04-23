#!/usr/bin/env python

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

from optparse import OptionParser

import lxml.etree as ET

from commonUtils.fileUtils import locate  #pylint:disable=F0401

opts = OptionParser()
opts.add_option(
    '-o', dest='outputdestination', default=None,
    help="The root directory beneath which to write corrected files.")
opts.add_option(
    '-s', dest='source', default=None,
    help="The short code for the source institution supplying this conent.")

(options, args) = opts.parse_args()

def setoutput(outputdestination):
    if outputdestination is None:
        return os.path.join(target_directory, '__output')
    else:
        return outputdestination

def setsource(sourcecode):
    if sourcecode is None:
        print >> sys.stderr, "Please provide a source institution code"
        exit(1)
    elif sourcecode not in ['IWM', 'BL', 'LOC', 'SSB']:
        print >> sys.stderr, "Invalid source code: %s" % options.source
        exit(1)
    else:
        return sourcecode

def settarget(arglist):
    try:
        return arglist[0]
    except IndexError:
        return os.path.curdir

sourceinst = setsource(options.source)
target_directory = settarget(args)
output_directory = setoutput(options.outputdestination)

doc_types = {
    'advertisement': 'Ad',
    'article':       'Article',
    'back_matter':   'Back matter',
    'comic':         'Comic',
    'cover':         'Cover',
    'editorial_cartoon': 'Editorial cartoon',
    'front_matter':  'Front matter',
    'illustration':  'Illustration',
    'letter':        'Letter',
    'obituary':      'Obituary',
    'other':         'Other',
    'photograph':    'Photograph',
    'poem':          'Poem',
    'recipe':        'Recipe',
    'review':        'Review',
    'tbl_of_contents': 'Tbl of contents',
}

mapped_doc_types = [v for k, v in doc_types.items()]

def write_corrected_xml(outputfile, fixed_xml):
    output_dir = os.path.dirname(outputfile)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    with open(outputfile, 'w') as outf:
        fixed_xml.write(outf, pretty_print=True)

for filename in locate('*.xml', root=target_directory):
    # __output is the default output directory if none is
    # explicitly supplied. We don't want to descend into
    # these directories.
    if '__output' in filename: continue

    # Read in the file and parse it. Remove blank text
    xml = ET.parse(filename, ET.XMLParser(remove_blank_text=True))

    aps_article = xml.getroot()

    # Find the APS_vendor element
    aps_vendor = xml.find('APS_vendor')
    # Create the APS_source element, and assign its value
    if xml.find('.//APS_source') is None:
        source = ET.Element('APS_source')
        source.text = sourceinst
        # Insert the new APS_source element before the APS_vendor element.
        # We do this by finding the location of the APS_vendor within the
        # document, and inserting APS_source at that location. Everything
        # else gets pushed down.
        aps_article.insert(aps_article.index(aps_vendor), source)

    # Change the type attribute value to one of the controlled list
    # in the doc_types dict.
    doc_type = aps_article.attrib['type']
    try:
        aps_article.attrib['type'] = doc_types[doc_type.lower()]
        #aps_article.attrib['type'] = doc_types[aps_article.attrib['type']]
    except KeyError:
        if doc_type not in mapped_doc_types:
            raise


    # Find all image file names, and change 'APS_' to 'TRJ'
    for page_image in xml.findall('.//APS_page_image'):
        page_image.text = page_image.text.replace('APS_', 'TRJ')

        # The transformation app expects zone image file names to be of
        # the form PMID_ISSUE-SEQ.jpg. What we get for trench, though,
        # is PMID_ISSUE_SEQ.jpg. Rather than modifying the app, fix the
        # file names here.
        if page_image.text[-8] == '_':
            page_image.text = page_image.text[0:-8]+'-'+page_image.text[-7:]

    # For zone with a type of "image", check the length of its child
    # APS_content element. If it is 0, this zone has been incorrectly
    # captured as an image, and should instead be captured as "text"
    # (This happens in cases where no OCR data is available because
    # the source is too foxed, creased or otherwise machine illegible)
    # for zone in xml.findall('.//APS_zone[@type="image"]'):
    #     aps_content = zone.find('APS_content')
    #     if len(aps_content) == 0:
    #         zone.attrib['type'] = "text"

    # Zones.
    # For each zone, check the type attribute.
    # If it is "header", move on.
    # If it is "text", check to see if it contains APS_para elements.
    #    If it does, it is a "text" zone, and should have APS_zone_credit removed
    #    If it doesn't, it is an "image" and needs to be modified accordingly
    #       (add APS_caption, APS_zone_imagetype. Build caption from the content of
    #       any subsequent "caption" zone.)
    # If it is "image", and it is the only zone in the doc, it should be "text"
    zones = xml.findall('.//APS_zone')
    for idx, zone in enumerate(zones):
        zone_credit = zone.find('.//APS_zone_credit')

        if zone.attrib['type'] == 'header':
            zone.remove(zone_credit)
            
        elif zone.attrib['type'] == 'text':
            aps_paramap = zone.findall('.//APS_paramap')
            if len(aps_paramap) == 0:
                # We have an image zone
                zone.attrib['type'] = "image"
                zone.remove(zone.find('.//APS_content'))
                imagetype = ET.Element('APS_zone_imagetype')
                imagetype.text = "Photograph"
                zone.insert(zone.index(zone_credit) + 1, imagetype)

                # Add an APS_feature element to the doc
                doc_feature = ET.Element('APS_feature')
                doc_feature.text = "Photographs"
                root = xml.getroot()
                root.insert(root.index(xml.find('.//APS_title')), doc_feature)

                # Check to see if the next zone is a caption, and grab its contents
                # to put in the APS_zone_caption element
                try:
                    if zones[idx + 1].attrib['type'] == "caption":
                        captiontxt = ' '.join([word.text.strip() for word in zones[idx + 1].findall('.//APS_text')])
                        caption = ET.Element('APS_zone_caption')
                        caption.text = captiontxt
                        zone.insert(zone.index(zone_credit), caption)
                except IndexError:
                    pass

                # If APS_zone_credit is empty, remove it.
                if zone_credit.text == None:
                    zone.remove(zone_credit)

            else:
                zone.remove(zone_credit)

            
        # If the zone is a "caption", remove the APS_zone_credit element
        elif zone.attrib['type'] == "caption":
            zone.remove(zone_credit)
            
        elif zone.attrib['type'] == "image":
            zone_content = zone.find('.//APS_content')
            if len(zones) == 1:
                zone.attrib['type'] = "text"

            zone.remove(zone_content)
            zone.remove(zone_credit)
            

    # output_filename needs to be the filename from locate, with the
    # target_directory portion removed. Then, prepend the output directory
    # to it.
    # target_directory = /data/trench/src/by_pmid
    # output_directory = /data/trench/src/by_pmid/__output
    #    output_filename = os.path.join(output_directory, '/'.join(filename.split('/')[-3:]))
    output_filename = filename.replace(target_directory, output_directory)
    write_corrected_xml(output_filename, xml)
