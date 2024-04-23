# -*- mode: python -*-
import httplib
import json
import logging
import os
import sys
import time


# import re
import lxml.etree as ET

sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages/')

from collections import namedtuple  # noqa
from lxml.builder import E  # noqa
from mutagen.mp3 import MP3  # noqa
from stat import ST_SIZE  # noqa
# from xml.sax.saxutils import escape

from commonUtils.fileUtils import get_file_checksum  # noqa
from commonUtils.fileUtils import get_file_size  # noqa
from commonUtils.langUtils import lang_iso_codes  # noqa
from commonUtils.textUtils import xmlescape  # noqa
from cstoreerrors import SkipRecordException  # noqa
from mappings.leviathanmapping import LeviathanMapping  # noqa
from mappings.abstractmapping import AbstractMapping  # noqa

log = logging.getLogger('tr.mapping.dnsa')


class DNSAMapping(LeviathanMapping):  # pylint: disable = R0904
    __simpleAttrs = [
        ['object_dates/object_numdate', 'numdate'],
        ['object_dates/object_rawdate', 'rawdate'],
        ['rec_format/@formattype'],
        ['rec_format/abstract'],
        ['rec_format/cablenum'],
        ['rec_format/classification'],
        ['rec_format/collection_code'],
        ['rec_format/collection_names/long', 'coll_long_name'],
        ['rec_format/collection_names/short', 'coll_short_name'],
        ['rec_format/docid'],
        ['rec_format/docnum'],
        ['rec_format/doctype1'],
        ['rec_format/doctype_src'],
        ['rec_format/editorial_note'],
        ['rec_format/link'],
        ['rec_format/loc_of_original_audio'],
        ['rec_format/loc_of_original_doc'],
        ['rec_format/object_time'],
        ['rec_format/page_count'],
        ['rec_format/pub_note'],
        ['rec_format/title', 'doc_title'],
        ['record/rec_format/srcid'],
        ['record/rec_format/glosstype'],
        ['record/rec_format/audiofile'],
        ['bodytext', 'text']
    ]

    __noteTypes = {
        'doctype_src': ('Document', 'NSA document type: %s'),
        'editorial_note': ('Editorial', '%s'),
        'loc_of_original_audio': ('Document', 'Location of audio: %s'),
        'loc_of_original_doc': ('Document', 'Location of original: %s'),
        'object_time': ('Document', 'Time Stamp: %s'),
        'pub_note': ('Publication', '%s (previously published document)'),
    }

    __objectIDTypes = {
        'cablenum': 'CableNum',
        'docnum': 'NSADocNum',
        'srcid': 'AccNum',
    }

    __legacyPudIDs = {
        'Document': 'DNSA0001',
        'Glossary': 'DNSA0003',
        'Chronology': 'DNSA0002',
        'Bibliography': 'DNSA0002'
    }

    legacy_xpath_mapping = {
        'subjects': './/subjects/subject',
        'personal_names': './/names/personal',
        'corporate_names': './/names/corporate',
        'recipients': './/recipients/recipient',
        'code_words': './/rec_format/code_word'
    }

    def __init__(self, rawrecord):
        super(DNSAMapping, self).__init__(rawrecord)
        self.log = log

        self.xml = self.rawrecord.data
        self.assignSimpleAttrs(self.__simpleAttrs)

        self.build_legacy_record()
        self.assign_contributors()
        # self.assign_text()

        _local_dtables = {
            'dnsa': {
                'cablenum': DNSAMapping.noop,
                'doctype1': DNSAMapping.noop,
                'classification': DNSAMapping.noop,
                'code_words': DNSAMapping.noop,
                'coll_long_name': DNSAMapping.noop,
                'coll_short_name': DNSAMapping.noop,
                'collection_code': DNSAMapping.noop,
                'corporate_names': DNSAMapping.noop,
                'docnum': DNSAMapping.noop,
                'doctype_src': DNSAMapping.noop,
                'editorial_note': DNSAMapping.noop,
                'formattype': DNSAMapping.noop,
                'link': DNSAMapping.link,
                'loc_of_original_audio': DNSAMapping.noop,
                'loc_of_original_doc': DNSAMapping.noop,
                'numdate': DNSAMapping.noop,
                'object_time': DNSAMapping.noop,
                'page_count': DNSAMapping.page_numbers,
                'pagenumbers': DNSAMapping.noop,
                'personal_names': DNSAMapping.noop,
                'pub_note': DNSAMapping.noop,
                'rawdate': DNSAMapping.noop,
                'recipients': DNSAMapping.noop,
                'srcid': DNSAMapping.noop,
                'subjects': DNSAMapping.noop,
                'glosstype': DNSAMapping.noop,
                'text': DNSAMapping.noop,
                'audiofile': DNSAMapping.noop,
            }
        }

        self._merge_dtables(_local_dtables[self.productId])

        # pylint: disable = W0212
        self._computedValues = [
            self.__class__._lastUpdateTime,
            self.__class__._terms,
            self.__class__._setDates,
            self.__class__._objectIDs,
            self.__class__._objectTypes,
            self.__class__._language,
            self.__class__._product_xml_fragment,
            self.__class__._fulltext_fragment,
            self.__class__._notes,
            self.__class__._source_types,
            self.__class__._search_object_type_origin,
            self.__class__._terms,
            self.__class__._components,
            self.__class__._legacy_pub_id,
        ]

        self._after_hooks = [
            self.__class__.objectBundleData
        ]
        # pylint: enable = W0212
        self._componentTypes[
            'MultipleComponents'] = DNSAMapping._buildMultipleComponents

        self.collectionaudiodir = os.path.join(
            self._cfg['mediaroot'], self.record.collection_code, 'audio')
        self.collectionpdfdir = os.path.join(
            self._cfg['mediaroot'], self.record.collection_code, 'pdf')

        self.HMSRecipes = {
            'pdf': self._simplePDF,
            'audio': self._simpleObject,
        }

    def build_legacy_record(self):
        for var, xpath in self.legacy_xpath_mapping.items():
            setattr(self.record, var, [])
            for datum in self.xml.xpath(xpath):
                if datum.text:
                    getattr(self.record, var).append(unicode(datum.text))

    # def assign_text(self):
    #     self.record.text = []
    #     for elem in self.xml.findall('.//bodytext/*'):
    #         print elem
    #         # pylint: disable = E1101
    #         self.record.text.append(ET.tostring(elem, pretty_print=True))

    def link(self, data):
        self.gs4.linkData = [
            {u'linkType': 'OtherLink',
             u'attrs': {'LinkType': 'ResLoc'},
             'linkValue': data}
        ]

    def page_numbers(self, data):
        self.gs4.pageCount = data

    def contributors(self, data):
        self.gs4.contributors = []
        if data is not None:
            for index, contributor in enumerate(
                    data.xpath('.//contributor'), start=1):
                if contributor.attrib['role'] == "CorpAuthor":
                    contribdict = {
                        u'ContributorRole': 'Author',
                        u'IsNormalized': 'false',
                        u'ContribOrder': unicode(index),
                        'contribvalue': {u'OrganizationName': xmlescape(
                            contributor.find('.//originalform').text)}
                    }
                else:
                    contribdict = {
                        u'ContributorRole': contributor.attrib['role'],
                        u'ContribOrder': unicode(index),
                        'contribvalue': contributor.find(
                            './/originalform').text
                    }

                if 'role_desc' in [e.tag for e in contributor.getchildren()]:
                    contribdict[u'MiscRoleDesc'] = contributor.find(
                            './/role_desc').text

                self.gs4.contributors.append(contribdict)

    def _setDates(self):
        if self.record.numdate == '0001-01-01':
            self.gs4.undated = True
            self.gs4.normalisedAlphaNumericDate = self.record.rawdate
            self.gs4.numericStartDate = self.record.numdate.replace('-', '')
            self.gs4.numericObStartDate = self.record.numdate.replace('-', '')
            self.gs4.rawObjectDate = self.record.rawdate
        else:
            if self.record.numdate.endswith('00'):
                if self.record.numdate.endswith('00-00'):
                    self.gs4.numericStartDate = '%s0101' % (
                        self.record.numdate.replace('-', '')[0:4])
                    self.gs4.numericObStartDate = '%s0101' % (
                        self.record.numdate.replace('-', '')[0:4])
                else:
                    self.gs4.numericStartDate = '%s01' % (
                        self.record.numdate.replace('-', '')[0:6])
                    self.gs4.numericObStartDate = '%s01' % (
                        self.record.numdate.replace('-', '')[0:6])
            else:
                self.gs4.numericStartDate = self.record.numdate.replace(
                        '-', '')
                self.gs4.numericObStartDate = self.record.numdate.replace(
                        '-', '')

            self.gs4.rawObjectDate = self.record.rawdate
            self.gs4.normalisedAlphaNumericDate = self.record.rawdate

    def _language(self):
        self.gs4.languageData = lang_iso_codes(['English'])

    def _objectIDs(self):
        super(DNSAMapping, self)._objectIDs()
        for idtype in self.__objectIDTypes.keys():
            if getattr(self.record, idtype) != '':
                self.gs4.objectIDs.append(
                    {'value': getattr(self.record, idtype),
                     u'IDOrigin': u'CH',
                     u'IDType': self.__objectIDTypes[idtype]})

    def _objectTypes(self):
        if self.record.formattype != 'Document':
            self.gs4.searchObjectType = [self.record.formattype]
        else:
            self.gs4.searchObjectType = [self.record.doctype1]

    def _fulltext_fragment(self):
        if not self.record.text:
            pass
        else:
            textinfo = E.TextInfo(
                E.Text(HTMLContent="true")
            )

            text_elem = textinfo.xpath('.//Text')[0]

            text_elem.text = '<![CDATA[%s]]>' % ''.join(
                [i for i in self.record.text])
            # pylint: disable = E1101
            self.gs4.fullText = ET.tostring(textinfo, pretty_print=True)

    def _product_xml_fragment(self):
        product_fragment = E.Product(
            E.DNSA(
                E.Collection(
                    E.CollectionCode(self.record.collection_code),
                    E.CollectionLongName(self.record.coll_long_name),
                    E.CollectionShortName(self.record.coll_short_name)
                ),
                E.RecordFormat(self.record.formattype),
            )
        )

        prod_dnsa = product_fragment.xpath('.//DNSA')[0]

        if self.record.glosstype != '':
            glosstype = E.GlossaryRecordFormat(self.record.glosstype)
            prod_dnsa.append(glosstype)

        if self.record.classification != '':
            sec_class = E.SecClassification(
                E.Classification(self.record.classification)
            )
            prod_dnsa.append(sec_class)

        for cw in self.record.code_words:
            cw_elem = ET.Element('OpCodeWord')  # pylint: disable = E1101
            cw_elem.text = cw
            sec_class.append(cw_elem)

        # pylint: disable = E1101
        self.gs4.product_xml_fragment = ET.tostring(product_fragment,
                                                    pretty_print=True)

    def _notes(self):
        self.gs4.notesData = []
        for note_elem in self.__noteTypes.keys():
            if getattr(self.record, note_elem) != '':
                note_type = self.__noteTypes[note_elem][0]
                note_text = self.__noteTypes[note_elem][1]
                note_data = getattr(self.record, note_elem)
                self.gs4.notesData.append(
                    {'NoteType': note_type,
                     'NoteText': note_text % note_data})

    def _search_object_type_origin(self):
        self.gs4.searchObjectTypeOrigin = "DNSA"

    # FIXME: check that this actually works with changed helper
    # module _insert_source_types
    def _source_types(self):
        self.gs4.source_origin = "DNSA"
        if self.record.formattype == "Document":
            self.gs4.source_types = ['Government &amp; Official Publications']
        else:
            self.gs4.source_types = ['Encyclopedias &amp; Reference Works']

    def _terms(self):
        self.gs4.terms = []
        for recipient in self.record.recipients:
            self.gs4.terms.append(
                self._build_term(
                    termtype='FlexTerm',
                    termvalue=recipient,
                    termattr='Recipient'))

        for pn in self.record.personal_names:
            self.gs4.terms.append(
                self._build_term(
                    termtype='Term',
                    termvalue=pn,
                    termattr='Personal'))

        for cn in self.record.corporate_names:
            self.gs4.terms.append(
                self._build_term(
                    termtype='CompanyTerm', termvalue=cn))

        for subj in self.record.subjects:
            self.gs4.terms.append(
                self._build_term(
                    termtype='GenSubjTerm', termvalue=subj))

        if self.record.formattype != 'Document':
            self.gs4.terms.append(
                self._build_term(
                    termtype='GenSubjTerm', termvalue=self.record.formattype))

    def _legacy_pub_id(self):
        self.gs4.journalID = self.__legacyPudIDs[self.record.formattype]

    @staticmethod
    def _filesizer(path):
        return str(os.stat(path)[ST_SIZE])

    @staticmethod
    def _getseconds(path):
        return str(int(MP3(path).info.length))

    def _buildMediaPath(self, filename, filedir):
        return os.path.join(
            self._cfg['mediaroot'], self.record.collection_code,
            filedir, filename)

    def _components(self):
        AbstractMapping._components(self)  # pylint: disable = W0212
        if self.record.formattype == 'Document':
            self._insert_media_objects()
        else:
            self.gs4.components.append(
                self._buildComponent(
                    u'FullText',
                    {u'Representation': {
                        u'RepresentationType': u'FullText',
                        'values': {
                            u'MimeType': u'text/xml', u'Resides': u'FAST'}}}))

    def _insert_media_objects(self):
        for method in [self._pdf_component, self._audio_components]:
            timeouts = 0
            while True:
                try:
                    method()
                    break
                except OSError as e:
                    # Don't worry about a no such file error
                    if e.errno == 2:
                        log.warn("No such file %s. Continuing.", e.filename)
                        break
                    elif e.errno == 60:
                        # But if we get a timeout, we want to
                        # retry, but only 3 times. After that,
                        # raise SkipRecordException and move on.
                        timeouts += 1
                        if timeouts == 3:
                            log.error(
                                "Timed out reading %s. 3 failed attempts. "
                                "Giving up.",
                                e.filename)
                            self.msq.append_to_message(
                                "Timeout reading file", e.filename)
                            raise SkipRecordException
                        else:
                            log.warn("Timeout reading %s. Trying again.",
                                     e.filename)
                        continue
                    else:
                        # Anything else, we should probably raise it
                        # and stop...
                        raise

    def _json_file(self, docid):
        for filename in ["%s.pdf.json" % docid, "dnsa-%s.pdf.json" % docid]:
            _path = os.path.join(
                '/dc/dsol/migration/dnsa/hms',
                os.environ['HMSINSTANCE'],
                filename)
            if os.path.isfile(_path):
                with open(_path) as j:
                    return json.load(j)
        raise RuntimeError('File not found %s' % _path)

    def _pdf_component(self):
        try:
            hmsmetadata = self._json_file(self.record.docid)
        except (ValueError, RuntimeError) as e:  # noqa
            self.msq.append_to_message(
                "Missing or invalid HMS response", self.record.docid)
            log.exception("Problem with HMS JSON? %s" % e)
            return

        mediakey = hmsmetadata[0]['objects'][0]['retrieveKey']
        size = hmsmetadata[0]['objects'][0]['size']
        self.gs4.components.append(
            self._buildComponent(
                'FullText',
                {u'Representation': {
                    u'RepresentationType': u'PDFFullText',
                    'values': {
                        u'MimeType': u'application/pdf',
                        u'Resides': u'HMS',
                        u'ImageType': u'TIFF',
                        u'WordMapCoords': u'false',
                        u'Bytes': size,
                        u'PDFType': u'300PDF',
                        u'MediaKey': "/media{0}".format(mediakey)}}}))

    def _audiodir_list(self):
        return sorted([i for i in os.listdir(self.collectionaudiodir)
                       if self.record.docid in i])

    def _audio_components(self):
        for i, aud in enumerate(self._audiodir_list(), start=1):
            path = self._buildMediaPath(aud, 'audio')
            size = self._filesizer(path)
            duration = self._getseconds(path)
            hmsmetadata = self._load_object(MediaObject(
                path, self.record.collection_code, 'audio'))
            embed_key = hmsmetadata.body[0]['objects'][0]['cfretrieveKey']
            dl_key = hmsmetadata.body[0]['objects'][0]['retrieveKey']
            representations = {'MultipleComponents': [{u'Order': str(i)}]}
            for repType in ['Embed', 'Download']:
                if repType == 'Embed':
                    mediakey = embed_key
                elif repType == 'Download':
                    mediakey = dl_key
                representations['MultipleComponents'].append({
                    u'Representation': {
                        u'RepresentationType': repType,
                        'values': {
                            u'MimeType': u'mp3',
                            u'Resides': u'HMS',
                            u'Seconds': duration,
                            u'Bytes': size,
                            u'MediaKey': "/media{0}".format(
                                mediakey.replace(
                                    '/media', ''))}}})

            self.gs4.components.append(
                self._buildComponent('Audio', representations))
            break  # We only want to process the first file. THIS IS A HACK

    def objectBundleData(self):  # pylint: disable = W0221
        super(DNSAMapping, self).objectBundleData(
            "DNSA%s" % self.record.collection_code
        )

    # this will be extracted into a separate package at some point...

    # workflow
    # Determine what type of object we are dealing with.
    #
    # PDF:
    # send Lookup request for self.gs4.legacyID.
    # If response is empty
    #    send upload request
    #    send status request to get object id
    # else
    #    parse response and extract md5 checksum.
    #    If checksum in json matches that here
    #        take the object ID from the json
    #        move on
    #    else
    #        send upload request
    #        send status request to get object id
    #
    # MP3:
    # send lookup request for self.gs4.legacyID-01, -02 etc
    # If response is empty:
    #    send upload request (SimpleOnject)
    #    send status request to get object id

    @staticmethod
    def _http_lookup(idstring):
        return _http_request(
            'GET', '/Lookup?clientId=CH&uniqueId=%s' % idstring)

    @staticmethod
    def _http_status(idstring):
        return _http_request(
            'GET', '/Status?clientId=CH&uniqueId=%s' % idstring)

    def _load_object(self, media_object=None, action='upsert'):
        if media_object is None:
            raise ValueError

        # If the specified action is "insert", we know we should short-circuit
        # the lookup steps, and go straight to trying to load the object.
        if action in ['insert', 'update']:
            resp = self.HMSRecipes[media_object.object_type](
                media_object, action)
            return resp

        resp = self._http_lookup(media_object.uniqueid)
        if resp.status >= 500:
            # Oops. Server error. Let's see if we can get the loading
            # status instead, assuming this was an interrupted call to
            # store the object in the first place.
            log.warn("Lookup on %s got status %s. Trying a Status request...",
                     media_object.uniqueid, resp.status)
            resp = self._http_status(media_object.uniqueid)
            log.warn("Status for %s succeeded.", media_object.uniqueid)
            return resp

        try:
            stored_md5 = resp.body[0]['objects'][0]['md5']
            log.debug("%s found in HMS.", media_object.uniqueid)
        except IndexError:
            # If we get here, the JSON returned for our Lookup was
            # empty, and thus we simply need to load the PDF
            log.info(
                "%s not found in HMS. Submitting now.",
                media_object.uniqueid)
            resp = self.HMSRecipes[media_object.object_type](
                media_object, action='insert')
            return resp

        if stored_md5 == media_object.md5 and os.environ.get(
                'HMSRELOAD') != "1":
            log.info(
                "%s checksum test indicates no change. No reload required",
                media_object.uniqueid)
            return resp
        else:
            log.warn(
                "%s checksum mismatch. Reloading file", media_object.uniqueid)
            resp = self.HMSRecipes[media_object.object_type](
                media_object, action)
            return resp

    def _simpleObject(self, media_object, action='upsert'):
        if media_object is None:
            raise ValueError

        request = '/SimpleObject?clientId=CH&uniqueId=%(objid)s&action=%(action)s&async=Yes' % {  # noqa
            'objid': media_object.uniqueid,
            'action': action.capitalize()
        }
        headers = {'Content-type': 'application/json'}
        body = {
            'clientId': 'CH',
            'action': 'upsert',
            'retrieveRecipe': 'SimpleObject',
            'timeout': '300',
            'objects': [
                {
                    'type': 'object',
                    'size': media_object.size,
                    'md5': media_object.md5,
                    'location': media_object.uri,
                    'options': [
                        {'key': 'specifiedFileName',
                         'value': media_object.filename},
                        {'key': 'mimeType', 'value': 'audio/mpeg'},
                        {'key': 'storeCF', 'value': 'Yes'}
                    ]}]}

        resp = _http_request(rest_actions[action], request,
                             json.dumps(body), headers)
        if resp.status == 200:
            log.debug("Success from server for %s. Checking status...",
                      media_object.uniqueid)
            while True:
                time.sleep(2)
                resp = self._http_status(media_object.uniqueid)
                if resp[0] >= 500:
                    log.warn(
                        "Status request got a 500 for %s. Trying again...",
                        media_object.uniqueid)
                    continue
                elif resp[0] >= 400:
                    log.error(
                        "Status request got a 400 for %s (%s, %s). Giving up.",
                        media_object.uniqueid, resp[0], resp[1]
                    )
                    raise SkipRecordException
                elif resp[2] is None:
                    log.warn(
                        "Status request got a 200 for %s, but the response "
                        "body was empty. Trying again...",
                        media_object.uniqueid
                    )
                    continue

                resp_body = resp[2]
                hmsid = resp_body[0]['objects'][0]['retrieveKey']
                log.debug("HMS loaded %s as %s", media_object.uniqueid, hmsid)
                self.msq.append_to_message(
                    "Loaded %s file to HMS" % media_object.object_type,
                    media_object.uniqueid)
                return resp

        else:
            log.error("Error communicating with HMS. Server said %s, %s",
                      resp.status, resp.reason)
            self.msq.append_to_message(
                "Error communicating with HMS.",
                "%s (status: %s, reason: %s)" % (
                    media_object.uniqueid, resp.status, resp.reason))
            raise SkipRecordException

    def _simplePDF(self, media_object, action='upsert'):

        request = '/SimplePDF?clientId=CH&uniqueId=%(docid)s&size=%(pdfsize)s&md5=%(pdfmd5)s&objectLoc=%(pdf_uri)s&action=%(action)s&validateObject=No&storeObject=Yes&textExtract=No&linearizeObject=No&retrieveRecipe=SimplePDF&async=Yes' % {  # noqa
            'docid': media_object.uniqueid, 'pdfsize': media_object.size,
            'pdfmd5': media_object.md5,
            'pdf_uri': media_object.uri,
            'action': action.capitalize()
        }
        resp = _http_request(rest_actions[action], request)

        if resp.status == 200:
            log.debug("Success from server for %s. Checking status...",
                      self.gs4.legacyID)
            while True:
                time.sleep(2)
                resp = self._http_status(self.gs4.legacyID)
                if resp[0] >= 500:
                    log.warn(
                        "Status request got a 500 for %s. Trying again...",
                        self.gs4.legacyID)
                    continue
                elif resp[0] >= 400:
                    log.error(
                        "Status request got a 400 for %s (%s, %s). Giving up.",
                        self.gs4.legacyID, resp[0], resp[1])
                    raise SkipRecordException
                elif resp[2] is None:
                    log.warn(
                        "Status request got a 200 for %s, but the response "
                        "body was empty. Trying again...",
                        self.gs4.legacyID)
                    continue

                resp_body = resp[2]
                pdfid = resp_body[0]['objects'][0]['retrieveKey']
                log.debug("HMS loaded %s as %s", self.gs4.legacyID, pdfid)
                self.msq.append_to_message(
                    "Loaded PDF to HMS", self.gs4.legacyID)
                return resp
        else:
            log.error("Error communcating with HMS. Server said %s, %s",
                      resp.status, resp.reason)
            self.msq.append_to_message(
                "Error communicating with HMS.",
                "%s (status: %s, reason: %s)" % (
                    self.gs4.legacyID,
                    resp.status, resp.reason))
            raise SkipRecordException


# A decorator to add /media to the beginning of all keys returned by HMS
def media_key_fixer_upper(method):
    def fixer(*args):
        return "/media/%s" % method(*args)
    return fixer


# A namedtuple to make retrieving and using the value returned from HMS
# a little easier. Can access its members by index or by name.
HMSResponse = namedtuple('HMSResponse', ['status', 'reason', 'body'])

# class HMSResponse(object):
#     def __init__(self, status, reason, body):
#         self.status = status
#         self.reason = reason
#         self.body = body

#     def __get__()


def _jsonify(httpresponse):
    status = httpresponse.status
    reason = httpresponse.reason
    try:
        body = json.load(httpresponse)
    except ValueError:
        body = None
    return HMSResponse(status, reason, body)

# There are three possible hms instances to connect to: dev, pre-prod and prod
# hms-store-dev.pre.proquest.com (nightly) - uses httplib.HTTPConnection
# hms-store.pre.proquest.com (preprod) - uses httplib.HTTPSConnection
# hms-store.prod.proquest.com (prod) - uses httplib.HTTPSConnection


_instances = {
    'dev': 'hms-store.dev.proquest.com',
    'pre': 'hms-store.pre.proquest.com',
    'prod': 'hms-store.prod.proquest.com'
}


def _get_http_client():
    env = os.environ.get("HMSINSTANCE")

    # default to selecting the dev environment.
    try:
        host = _instances[env]
    except KeyError:
        host = _instances['dev']
    if env == 'dev':
        return httplib.HTTPConnection(host)
    else:
        return httplib.HTTPSConnection(host)


def _http_request(verb, request, body=None, headers={}):
    # conn = httplib.HTTPSConnection('hms-store.prod.proquest.com')
    conn = _get_http_client()
    conn.request(verb, request, body, headers)
    resp = _jsonify(conn.getresponse())
    conn.close()
    return resp


rest_actions = {
    'upsert': 'POST',
    'insert': 'POST',
    'update': 'PUT',
}


class MediaObject(object):
    '''Abstraction for handling media objects to load into HMS. It's
    easier to pass an instance around than it is to pass loads of
    different attributes.'''
    def __init__(self, path, collection, object_type, size=None, md5=None):
        self.path = path
        self.collection = collection
        self.object_type = object_type
        if size is not None:
            self.size = size
        else:
            self.size = get_file_size(path)
        if md5 is not None:
            self.md5 = md5
        else:
            self.md5 = get_file_checksum(path)
        self.uri = "http://deliver.private.chadwyck.co.uk/dnsa/%s/%s/%s" % (
            self.collection, self.object_type, self.filename
        )

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def uniqueid(self):
        return "dnsa-%s" % os.path.splitext(self.filename)[0]
