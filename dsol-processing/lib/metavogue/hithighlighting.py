# -*- mode: python -*-
# pylint: disable= C0301, E1101, R0201, R0914, W0201

import codecs
import os
import re

from collections import defaultdict

from confreader import ConfReader
from dbcache import DBCacheManager

appconfig = ConfReader()

class HitHightlighting(object):
    __shared_state = {
        'issue_data': defaultdict(lambda: defaultdict(list)),
        'handled_docs': 0,
    }
    def __init__(self, dest_root, nsmap):
        self.__dict__ = self.__shared_state
        self.dest_root = dest_root
        self.nsmap = nsmap
        self.coord_points = {
            'uly': '{%s}uly' % nsmap['pq'],
            'ulx': '{%s}ulx' % nsmap['pq'],
            'lry': '{%s}lry' % nsmap['pq'],
            'lrx': '{%s}lrx' % nsmap['pq'],
        }

    def handle_document(self, document, issueid, articles_in_issue):
        # pylint: disable = E0203
        rescale_db = os.path.join(appconfig.get('vogue', 'rescalecacheroot'))
        docid = document.xpath('//dc:identifier', namespaces=self.nsmap)[0].text
        year = docid[0:4]
        month = docid[4:6]
        self.rescale_cache = DBCacheManager(
            '%s_%s' %(year, month), '2880',
            os.path.join(rescale_db, year, '%s.%s' % (month, '2880'))
        )

        # self.issue_data[docid]['word_offsets'] = {}
        # self.issue_data[docid]['page_offsets'] = ['0']
        self.issue_data[docid]['page_count'] = 0
        for page in document.xpath('//pq:page', namespaces=self.nsmap):
            self.issue_data[docid]['page_count'] += 1
            pgimg = page.xpath('//pq:zone/@pq:src', namespaces=self.nsmap)[0]
            words = []
            for word in page.xpath('.//pq:zone[@pq:type="Text"]/pq:zoneWord',
                                   namespaces=self.nsmap):
                word_text = self.clean_word_text(
                    word.xpath('.//pq:word', namespaces=self.nsmap)[0]
                )

                # If, after we've cleaned up the word, there are no
                # letters in the resulting string, we don't want to
                # keep it. Similarly, discard anything of length 1
                # that is not 'I'
                if self.valid_word(word_text):
                    coords = {}
                    for point in self.coord_points.keys():
                        value = word.xpath(
                            './/pq:wordPos', namespaces=self.nsmap
                        )[0].attrib[self.coord_points[point]]
                        coords[point] = str(
                            int(float(value)/float(self.rescale_cache[pgimg]))
                        )
                    for p in ['ulx', 'uly', 'lrx', 'lry']:
                        word_text = ':'.join([word_text, coords[p]])

                    words.append(word_text)
            # This must be indented one level inside the for page loop.
            # (column 12)
            self.issue_data[docid]['pages'].append(words)
        self.handled_docs += 1

        if self.handled_docs == articles_in_issue:
            self.flush_to_disk(issueid)
            self.handled_docs = 0
            self.issue_data = defaultdict(lambda: defaultdict(list))

#    @staticmethod
    def clean_word_text(self, word):
        # Clean up the word text. We don't want to include
        # these punctuatin marks, and all words should be
        # lower case.
        word_text = word.text.lower()
        word_text = re.sub(r'["~/$^(){};,\\?|_-]', '', word_text)
        word_text = re.sub(r"[.,:;!'#]*$", '', word_text)
        word_text = re.sub(r'^\.', '', word_text)
        word_text = re.sub(r"^['-]", '', word_text)
        word_text = word_text.replace('&gt', '')
        word_text = word_text.replace('&lt', '')

        # Remove trademark, registered and copyright signs,
        # emdash and pound sign
        unichar = re.compile(
            u'[\u2122|\u00ae|\u00a3|\u00a9|\u2014|\xab|\xa7|\u25a0|\xbb|\xb0|\u2022|\xb1|\u20ac]'  #.encode('utf-8')
        )
        word_text = unichar.sub('', word_text)

        return word_text

    @staticmethod
    def valid_word(word):
        if not re.search(r'[a-zA-Z]', word):
            return False
        if len(word) == 1 and word is not 'I':
            return False
        if len(word) == 0:
            return False
        return True

    def flush_to_disk(self, issueid):
        year = issueid[0:4]
        month = issueid[4:6]
        outdir = os.path.join(self.dest_root, year, month, 'coords')
        os.makedirsp(outdir)

        for article in sorted(self.issue_data.keys()):
            posfile = os.path.join(outdir, "%s.pos" % article)
            idxfile = os.path.join(outdir, "%s.idx" % article)

            word_offsets = defaultdict(list)
            page_offsets = ['0']
            with codecs.open(posfile, 'w', 'utf-8') as pos:
                for page in self.issue_data[article]['pages']:
                    if len(page) > 0:
                        for word in page:
                            offset = str(int(pos.tell()))
                            word_offsets[word.split(':')[0]] = offset
                            pos.write("%s\n" % word)
                    page_offsets.append(str(int(pos.tell())))

                if len(page_offsets) > 1:
                    offsets_for_all_pages = ':'.join(page_offsets)
                    with codecs.open(idxfile, 'w', 'utf-8') as idx:
                        idx.write("%s:%s:\n" % (str(self.issue_data[article]['page_count']), offsets_for_all_pages))
                        for word in sorted(word_offsets.keys()):
                            offsets = ':'.join(word_offsets[word])
                            idx.write("%s:%s\n" % (word, offsets))
