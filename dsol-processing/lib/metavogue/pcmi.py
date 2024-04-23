# -*- mode: python -*-

import os

import lxml.etree as ET

from collections import defaultdict
from lxml.builder import E

class PCMI(object):
    __shared_state = {
        'issue_data': defaultdict(lambda: defaultdict(str)),
        'handled_docs': 0,
    }

    def __init__(self, dest_root, nsmap):
        self.__dict__ = self.__shared_state
        self.dest_root = dest_root
        self.nsmap = nsmap

    def handle_document(self, document, issueid, articles_in_issue):
        # pylint: disable = E0203, W0201
        for page in document.xpath('//x:pagemap/x:page', namespaces=self.nsmap):
            img = os.path.splitext(page.attrib['image'])[0]
            name = page.attrib['thread']
            order = page.attrib['seq']
            self.issue_data[img]['name'] = name
            self.issue_data[img]['order'] = order
        self.handled_docs += 1

        if self.handled_docs == articles_in_issue:
            self.flush_to_disk(issueid)
            self.handled_docs = 0
            self.issue_data = defaultdict(lambda: defaultdict(str))

    def flush_to_disk(self, issueid):
        year, month = issueid[0:4], issueid[4:6]
        pcmi_dir = os.path.join(self.dest_root, year, month, 'xml/pcmi', issueid)
        os.makedirsp(pcmi_dir)  # pylint: disable = E1101
        pcmi_file_name = "%s/VOGUE_%s_PCMI.xml" % (pcmi_dir, issueid)
        mindex = ET.Element('mindex')
        for image in sorted(self.issue_data.keys()):
            mindex.append(self.build_comp(image, issueid))

        with open(pcmi_file_name, 'w') as outf:
            outf.write(ET.tostring(mindex, pretty_print=True,
                                   xml_declaration=True,
                                   encoding='UTF-8'))

    def build_comp(self, image, issueid):
        # pylint: disable = C0330
        image_dict = self.issue_data[image]
        return E.comp({'type': 'IP'},
                    E.name(image_dict['name']),
                    E.order(image_dict['order']),
                    E.rep({'type': 'THUM'},
                          E.path(self._media_key(issueid, image, 'jpg')),
                    ),
                    E.rep({'type': 'IMP'},
                          E.path(self._media_key(issueid, image, 'xml'))
                    )
                  )

    @staticmethod
    def _media_key(issueid, img_id, kind):
        root = '/media/ch/vogue/issue'
        if kind == 'xml':
            style = 'pagemap'
        elif kind == 'jpg':
            style = 'scaled'
        return '%s/%s/%s/%s.%s' % (root, issueid, style, img_id, kind)
