# -*- mode: python -*-
# pylint: disable = E1101, E0203, W0201

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

import lxml.etree as ET

from collections import defaultdict

from commonUtils.textUtils import cleanAndEncode
from confreader import ConfReader
from dbcache import DBCacheManager
from decorators import catchEmptyList

appconfig = ConfReader()

class PageMap(object): # pylint: disable = R0902
    '''Pagemap files are built up per image, including information about
    all zones that appear on the page. This requires that we build a
    dict per issue, keyed on image name, where the value is a list of
    probably etree objects encapsulating each zone.
    '''

    __shared_state = {
        'issue_images': defaultdict(list),
        'handled_docs': 0,
    }

    def __init__(self, dest_root, nsmap, messagequeue):
        self.__dict__ = self.__shared_state
        self.dest_root = dest_root
        self.nsmap = nsmap
        self.msq = messagequeue
        self.coord_points = {
            'top': '{%s}uly' % nsmap['pq'],
            'left': '{%s}ulx' % nsmap['pq'],
            'bottom': '{%s}lry' % nsmap['pq'],
            'right': '{%s}lrx' % nsmap['pq'],
        }

    def handle_document(self, document, issueid, articles_in_issue):
        for pq_zone in document.xpath('.//pq:zone', namespaces=self.nsmap):
            image_name = pq_zone.attrib['{%s}src' % self.nsmap['pq']]
            self.issue_images[image_name].append(
                self.build_zone(pq_zone, document)
            )
        self.handled_docs += 1
        if self.handled_docs == articles_in_issue:
            self.flush_to_disk(issueid)
            self.handled_docs = 0
            self.issue_images = defaultdict(list)

    def build_zone(self, pq_zone, document):
        doctitle = self.get_document_title(document)
        docid = document.xpath('//dc:identifier', namespaces=self.nsmap)[0].text
        return {
            'doctitle': doctitle,
            'docid': docid,
            'zone': pq_zone
        }

    @catchEmptyList('[untitled]')
    def get_document_title(self, document):
        try:
            _title = document.xpath('//dc:title', namespaces=self.nsmap)[0].text
        except AttributeError:
            _title = ''
        if _title is None:
            _title = ''
        return cleanAndEncode(_title, escape=False)

    def flush_to_disk(self, issueid):
        # open the article's rescale cache file
        rescale_db = os.path.join(appconfig.get('vogue', 'rescalecacheroot'))
        year = issueid[0:4]
        month = issueid[4:6]

        pagemap_dir = os.path.join(self.dest_root, year, month, 'xml/pagemap')
        os.makedirsp(pagemap_dir)

        self.rescale_cache = DBCacheManager(
            '%s_%s' %(year, month), '700',
            os.path.join(rescale_db, year, '%s.%s' % (month, '700'))
        )

        for seq, image in enumerate(sorted(self.issue_images.keys()), start=1):
            pm = ET.Element('PageMap')
            pcid = ET.SubElement(pm, 'PcId')
            pcid.text = issueid.zfill(15)
            pageno = ET.SubElement(pm, 'PageNum')
            pageno.text = str(seq)

            for zone in self.issue_images[image]:
                pm.append(self.make_zone(zone))

            pagemap_file_name = '%s/%s.xml' % (pagemap_dir, image)
            with open(pagemap_file_name, 'w') as outf:
                outf.write(ET.tostring(pm, pretty_print=True,
                                       xml_declaration=True,
                                       encoding='UTF-8'))

    def make_zone(self, zone):
        coords = self.get_coords_for_zone(zone['zone'])
        z = ET.Element('Zone')
        docid = ET.SubElement(z, 'DocId')
        docid.text = zone['docid']
        doctitle = ET.SubElement(z, 'Title')
        doctitle.text = zone['doctitle']
        blocked = ET.SubElement(z, 'Blocked')
        blocked.text = 'false'
        for point in ['top', 'left', 'bottom', 'right']:
            point_tag = ET.SubElement(z, point.capitalize())
            point_tag.text = coords[point]
        return z


    def get_coords_for_zone(self, zone):
        image = zone.attrib['{%s}src' % self.nsmap['pq']]
        coords = {}
        for point in ['top', 'bottom', 'left', 'right']:
            numerator = float(zone.attrib[self.coord_points[point]])
            try:
                denominator = float(self.rescale_cache[image])
            except TypeError:
                denominator = 1
                self.msq.append_to_message(
                    "No 700 pixel rescale number. Assuming 1.", image
                )
            integral = int(numerator/denominator)
            coords[point] = str(integral)
        return coords
