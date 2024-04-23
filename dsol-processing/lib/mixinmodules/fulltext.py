#!/usr/local/bin/python2.6
# -*- mode: python -*-
# pylint: disable=W0201

import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.insert(0, '/packages/dsol/lib/python')
sys.path.insert(0, '/packages/dsol/lib/python2.6/site-packages')

from bs4 import BeautifulSoup

from SequenceDict import SequenceDict #pylint: disable=F0401
from commonUtils import textUtils

import codecs
from glob import glob
import mimetypes
# This so we can write out converted full text and Components
import cPickle

# We need this so we can catch an error from module re. Don't ask.
import sre_constants

import lxml.etree as ET

import logging
log = logging.getLogger('tr.mixins.fulltext')

# Full text functions mixin.

# This is used in the pqFullText method below, to ensure
# the CHIMageIDs element we need to add goes in the right
# place.
COMPONENT_ELEMENTS = [
    'mstar_lm_media_id',
    'InlineImageCount',
    'PageCount',
    'Name',
    'CSAImageKey',
    'OrderCategory',
    'Order',
    'CHImageIDs',
    'DSMediaLocatorID',
    'LinkedComponentID',
    'Representation'
    ]

# The methods on this class are mixed in to the including class, and are attached as
# true methods. Therefore, there is no need to pass "self" as the first argument,
# because Python will do it automatically.
class FullTextMixin(object):
    def insertFullText(self, idval, fttype='pq'):
        log.debug("checking for %s full text, %s" % (fttype, idval,))
        if fttype == 'pq':
            self.pqFullText(idval)
        elif fttype == 'inno':
            self.innoFullText(idval)
        elif fttype == 'pdf':
            self.pdfFullText(idval)

    def innoFullText(self, idval):
        # This holds the path to the InnoData cache on disk.
        # /dc/scratch/vega/innodata/cache/{iimp,iipa}/${journalAbbreviation}
        #self.innodataCache = os.path.join('/dc/scratch/vega/innodata/cache', self.record.productid, self._journalAbbrevs[self.issn_jid])
        self.innodataCache = os.path.join(self._cfg['innodataft'], self.record.productid, self._journalAbbrevs[self.issn_jid])
        if self.gs4.volume:
            self.volInfo = self.gs4.volume
        else:
            self.volInfo = self.record.volissue

        self.innoRecordCache = os.path.join(self.innodataCache, self.volInfo, self.chid())

        #
        # CODE SMELL! This is too coupled to the including module. But then again, only IIMP/IIPA have innodata to worry about.
        # This should be refactored at some point to keep things clean.
        #
        if 'rebuildcache' in self.cfg['mappingOptions']:
            log.info("forcing rebuild of InnoData cache")
            for f in glob(os.path.join(self.innoRecordCache, '*')):
                os.unlink(f)
            log.info("Deleted cached full text for %s",
                     self.gs4.originalCHLegacyID)
        if os.path.exists(os.path.join(self.innoRecordCache, 'fulltext.pickle')):
            log.debug("InnoData from cache: %s (%s)" % (
                self.record.articleid,
                os.path.join(self.innoRecordCache, 'fulltext.pickle')))
            self.innoFullTextFromCache(self.innoRecordCache)
        elif self.issn_jid in self._journalAbbrevs.keys():
            log.debug("InnoData from source on disk: %s", self.record.articleid)
            self.innoFullTextFromSource(idval)
        else:
            log.debug("Oops. %s", self)

    def innoFullTextFromCache(self, cacheDir):
        log.info("inserting InnoData from cache: %s in file %s" % (
            self.gs4.originalCHLegacyID, self._cfg['basename']),)
        old =  os.path.join(cacheDir, 'fulltext.pickle')
        ft = open(os.path.join(cacheDir, 'fulltext.pickle'), 'r')
        try:
                self.gs4.textInfo = cPickle.Unpickler(ft).load()
        except EOFError:
                bkp_pickle_fname = old.replace('innodata', 'innodata_bkp')
                log.info("Pickle error. reverting to: %s" % (bkp_pickle_fname))
                bkp_pickle_data = open(bkp_pickle_fname, 'r')
                self.gs4.textInfo = cPickle.Unpickler(bkp_pickle_data).load()
        ft.close()
        if os.path.exists(os.path.join(cacheDir, 'components.pickle')):
            comp = open(os.path.join(cacheDir, 'components.pickle'), 'r')
            for component in cPickle.Unpickler(comp).load():
                self.gs4.components.append(component)
            comp.close()

    def innoFullTextFromSource(self, idval):
        log.info("Attempting to locate InnoData for %s", self.record.articleid)
        # The location in disk of the SOURCE, not the CACHE
        innoDataRoot = os.path.join(
            '/products/impa/build',
            self.record.productid, 'crawl', self._journalAbbrevs[self.issn_jid]
        )
        aid = idval
        self.innoComponents = []

        self.innoDataDir = os.path.join(innoDataRoot, self.volInfo, aid)
        if os.path.exists(self.innoDataDir):
            log.info(
                "inserting InnoData from crawled webfarm data: %s in file %s" %
                (
                    self.gs4.originalCHLegacyID, self._cfg['basename']
                ),
            )
            innoFtFile = os.path.join(self.innoDataDir, aid + '.htm')
            if os.path.exists(innoFtFile):
                innoFtData = [line for line in open(innoFtFile)]
            else:
                html_path = os.path.join(self.innoDataDir, aid[0:-1] + '.htm')
                try:
                    innoFtData = [line for line in open(html_path)]
                except IOError:
                    log.warn("Couldn't find html file for %s in %s (Looked for %s)" % (self.gs4.originalCHLegacyID, self._cfg['basename'], html_path))
                    return
            textData = u''
            for line in innoFtData:
                textData += textUtils.cleanAndEncode(line + '\n', escape=False)
            textData = self._removeTopOfPageLink(textData)
            textData = self._formatImageLinks(textData)
            # Remove any empty <p></p> tags
            textData = self._removeEmptyParaTags(textData)
            # Disabled, per Matt Kibble's advice about not conflating copyright notices
            #self._extractCopyright(textData)
            attrs = SequenceDict()
            attrs['Source'] = u'IMPAInno'
            attrs['HTMLContent'] = u'true'
            soup = BeautifulSoup(textData)
            pretty_textData = soup.prettify()
            self.gs4.textInfo = {'fullText': {'value': pretty_textData, 'attrs': attrs}}
            self.innoComponents.append(
                self._buildComponent(
                    u'FullText',
                    {u'Representation': {
                        u'RepresentationType': u'FullText',
                        u'values': {
                            u'MimeType': u'text/xml', u'Resides': u'FAST'}}}))
            for comp in self.innoComponents:
                self.gs4.components.append(comp)

            # Now write out the mangled full text and associated
            # component elements out to disk for reuse next time
            # through.
            self._writeCache(self.gs4.textInfo, self.innoComponents)

        else:
            log.info("crawled data not found for %s. File or directory missing: %s" % (self.record.articleid, self.innoDataDir,))

    def _writeCache(self, fulltext, components):
        log.debug("writing processed InnoData to cache: %s" % self.gs4.originalCHLegacyID)
        self._writePart(fulltext, 'fulltext')
        # No need to preserve empty component lists
        if components is not None:
            self._writePart(components, 'components')

    def _writePart(self, data, name):
        targetDir = self.innoRecordCache
        try:
            os.makedirs(targetDir)
        except OSError:   ## No need to crap out just because the targetDir already exists.
            pass
        preserve = open(os.path.join(targetDir, name + '.pickle'), 'w')
        print data
        cPickle.Pickler(preserve, 0).dump(data)
        preserve.close()

    def _removeEmptyParaTags(self, textData):
        return re.sub(r"<[Pp]></[Pp]>", '', textData)

    def _removeTopOfPageLink(self, textData):
        # For some reason, this doesn't work as a single return statement, hence the otherwise redundant assignment...
        text = re.sub(r'<IMG SRC="/images/ch/iimpft/images/top.gif" WIDTH=14 HEIGHT=14 BORDER=0><A HREF="#top">Top of Page</A> <IMG SRC="/images/ch/iimpft/images/top.gif" WIDTH=14 HEIGHT=14 BORDER=0>', '', textData)
        return text

    def _extractCopyright(self, textData):
        copyright_text = re.search(r'.*<EM>.+(Copyright.*)</EM>', textData)
        if copyright_text:
            self.gs4.copyrightData = textUtils.cleanAndEncode(copyright_text.group(1))

    def _formatImageLinks(self, textData):
        # First, get rid of <a.*> and </a>
        textData = re.sub(r'<a [^>]+>', '', textData, re.I)
        textData = re.sub(r'</a>', '', textData, re.I)
        self.links = re.findall(r'<img [^>]+>', textData)
        # It turns out to be MUCH easier to replace a known string with the post-processed link data...
        textData = re.sub(r'<img [^>]+>', r'IMGHERE', textData)

        if len(self.links) > 0:
            for index, link in enumerate(self.links):
                parts = {'id': index}
                for bit in link.split():
                    matchData = re.search(r'(?P<attribute>[^ ]*)="?(?P<value>[^ ">]*)', bit)
                    if matchData:
                        parts[matchData.group('attribute').lower()] = matchData.group('value')
                try:
                    textData = re.sub('IMGHERE', self._replaceImageTag(parts), textData, 1)
                except sre_constants.error:
                    # We don't want to do this by default, because it sends RAM usage through the roof...
                    textData = re.sub('IMGHERE', self._replaceImageTag(parts), re.escape(textData), 1)
#        try:
        return textData
#        except:
#            print textData

    def _replaceImageTag(self, imgAttrs):
        imgHtml = self._buildImage(imgAttrs)
        return imgHtml

    def _metaFilePath(self, src, kind):
        return os.path.join(self.innoDataDir, os.path.splitext(src.split('/')[-1])[0] + '.' + kind)

    def _buildImage(self, imgAttrs):
#        metafiles = {}
        if os.path.exists(self._metaFilePath(imgAttrs['src'], 'xml')):
            return self._buildImageFromXML(imgAttrs, self._metaFilePath(imgAttrs['src'], 'xml'))
        else:
            name, ext = os.path.splitext(imgAttrs['src'].split('/')[-1])
            name = name[:-1]
            path = self._metaFilePath(''.join([name, ext]), 'xml')
            if os.path.exists(path):
                return self._buildImageFromXML(imgAttrs, path)
            elif os.path.exists(self._metaFilePath(imgAttrs['src'], 'htm')):
                return self._buildImageFromHTML(imgAttrs, self._metaFilePath(imgAttrs['src'], 'htm'))
            else:
                return self._buildImageWithoutMetaData(imgAttrs)

    def _buildImageWithoutMetaData(self, img):
        metadata = {}
        for key in img.keys():
            metadata[key] = img[key]
        return self._buildImageTag(img, metadata)

    def _buildImageFromHTML(self, img, html):
        try:
            mdat = [line for line in open(html)]
            metadata = {}
            for line in mdat:
                titleMatch = re.search('<TITLE>(.*)</TITLE>', line)
                if titleMatch:
                    metadata['title'] = titleMatch.group(1)
                copyrightMatch = re.search('.*>(Copyright [^>]+)</', line)
                if copyrightMatch:
                    metadata['copyright'] = copyrightMatch.group(1)
            return self._buildImageTag(img, metadata)
        except IOError:
            raise

    def _buildImageFromXML(self, img, xml):
        mdat = [line for line in open(xml)]
        metadata = {}
        for line in mdat:
            matchData = re.search(r'<(?P<tagname>.*)>(?P<content>.*)</(?P=tagname)>', line)
            if matchData:
                content = re.sub(r'<!\[CDATA\[', '', matchData.group('content'))
                content = re.sub(r'\]\]>', '', content)
                content = textUtils.cleanAndEncode(content).strip()
                metadata[matchData.group('tagname')] = content
        return self._buildImageTag(img, metadata)

    def _buildImageTag(self, img, metadata):
        tag  = '<div>\n'
        tag += '<object class="mstar_link_to_media">\n'
        tag += '<param name="mstar_lm_media_type" value="Graphic"/>\n'
        tag += '<param name="mstar_lm_media_id" value="' + str(img['id'] + 1) + '"/>\n'
        try:
            tag += '<param name="mstar_lm_alignment" value="' + img['align'].capitalize() + '"/>\n'
        except KeyError:
            pass
        tag += '<param name="mstar_lm_display_control" value="Embed"/>\n'
        #if 'title' in metadata.keys():
        #    tag += '<div class="mstar_lm_title"><p>' + textUtils.cleanAndEncode(metadata['title']) + '</p></div>\n'
        try:
            if len(metadata['caption']) > 0:
                tag += '<div class="mstar_lm_caption"><p>' + metadata['caption'] + '</p></div>\n'
        except KeyError:
            pass
        try:
            tag += '<div class="mstar_lm_copyright"><p>' + metadata['copyright'] + '</p></div>\n'
        except KeyError:
            # copyright isn't in the metadata for this image.
            # get over it and move on.
            pass
        except AttributeError:
            # copyright is in the metadata, but is an empty string.
            # Log it, get over it, and move on.
            log.debug("%s: copyright element in image metadata, but contains an empty string." % self.gs4.legacyID)
        except Exception as e:
            print >> sys.stderr, ("DEBUG: %s" % e)
            print >> sys.stderr, (self.gs4.objectIDs)
            print >> sys.stderr, (metadata)

        tag += '</object>\n</div>\n'
        self.innoComponents.append(self._buildImageComponent(img))
        return tag

    def _imageMimeType(self, path):
        return unicode(mimetypes.guess_type(path)[0])

    def _buildImageComponent(self, img):
        return self._buildComponent(
            u'InlineImage', {
                u'mstar_lm_media_id': unicode(img['id'] + 1),
                u'InlineImageCount':  unicode(len(self.links)),
                u'OrderCategory':     u'Graphic',
                u'Order':             unicode(img['id'] + 1),
                u'InnoImgReprs': {
                    u'RepresentationTypes': ['Full', 'Inline', 'Pinky', 'Thumb'],
                    u'values': {
                        u'MimeType': self._imageMimeType(img['src']),
                        u'Resides': u'CH/IIMPA',
                        u'MediaKey': self._constructMediaKey(img['src'])}}})

    def id2FullTextPath(self, idval):
        ftDir1 = idval[-3]
        ftDir2 = idval[-3:-1]
        ftFileName = idval + '.xml'
        return os.path.join(self._cfg['fulltextpath'], ftDir1, ftDir2, ftFileName)

    def pdfFullText(self, idval):
        # Extract the PDF full text representation from the PQ feed.
        ftFullPath = self.id2FullTextPath(idval)
        if os.path.exists(ftFullPath):
            log.info("Inserting PDF linking info from PQ feed for %s in file %s" % (self.gs4.originalCHLegacyID, self._cfg['basename'],))
            for _, ftData in ET.iterparse(ftFullPath, tag="IngestRecord"):
                for representation in ftData.xpath('//Representation[@RepresentationType="PDFFullText"]'):
                    comp = ET.Element('Component', ComponentType="FullText")
                    comp.append(self.chiElem(idval))
                    comp.append(ET.fromstring(ET.tostring(representation, pretty_print=True)))
                    comp = ET.tostring(comp, pretty_print=True).strip()
                    self.gs4.preformattedComponents = [comp]

    def pqFullText(self, idval):
        # Find full text information in the PQ feed. We need to extract the TextInfo element (and wrap the contained <Text>
        # element's contents in <![CDATA[]]>), and then get any Components so we can get the Representations.
        ftFullPath = self.id2FullTextPath(idval)
        log.debug("Checking for full text file at %s" % ftFullPath)
        # print ftFullPath
        # print os.path.exists(ftFullPath)
        if os.path.exists(ftFullPath):
            log.info("inserting full text info from PQ feed for %s in file %s" % (self.gs4.originalCHLegacyID, self._cfg['basename'],))
            ft = False
            for _, ftData in ET.iterparse(ftFullPath, tag="IngestRecord"):
                #                print ftData.xpath('//ObjectInfo')
                ftInfo = ftData.xpath('//ObjectInfo/TextInfo')
                if len(ftInfo) >= 1:
                    ft = codecs.decode(ET.tostring(ftInfo[0], pretty_print=True).strip(), 'utf-8')
                    ft = re.sub(r"(<Text [^>]+?>)\n", r"\1\n<![CDATA[", ft)
                    ft = re.sub(r"(</Text>)", r"]]>\1", ft)
                    self.gs4.fullText = self.removeEmptyLines(ft)
                #print self.gs4.fullText
                components = []
                for comptype in ['FullText', 'Pages', 'InlineImage']:
                    components.append(self.extractComponent(ftData, comptype))
                for complist in components:
                    for component in complist:
                        # We need to insert a CHImageIDs element, but
                        # it needs to go in the right place.  In order
                        # to do that, we need to know what order the
                        # permitted child elements of Component must
                        # appear - that's what the COMPONENT_ELEMENTS
                        # list is for. For each element in the
                        # component, check its index in
                        # COMPONENT_ELEMENTS to see if it comes before
                        # or after the CHImageIDs element. We also
                        # need to make sure we only insert one
                        # instance of CHImageIDs, so we need to use a
                        # boolean check.
                        chimageids_already_inserted = False
                        comp = ET.fromstring(ET.tostring(ET.Element('Component', component.attrib), pretty_print=True))
                        for _e in component.getchildren():
                            if COMPONENT_ELEMENTS.index(_e.tag) > COMPONENT_ELEMENTS.index('CHImageIDs'):
                                if chimageids_already_inserted == False:
                                    chimageids_already_inserted = True
                                    comp.append(ET.fromstring(ET.tostring(self.chiElem(idval), pretty_print=True)))
                            comp.append(ET.fromstring(ET.tostring(_e, pretty_print=True)))
                        comp = ET.tostring(comp, pretty_print=True).strip()
                        try:
                            self.gs4.preformattedComponents.append(comp)
                        except AttributeError:
                            self.gs4.preformattedComponents = [comp]
            else:
                if ft is False:
                    log.debug("No TextInfo in %s for record %s" % (ftFullPath, self.gs4.originalCHLegacyID,))
        else:
            log.debug("File not found: %s" % ftFullPath)

    def extractComponent(self, ftData, comptype):
        return ftData.xpath('//ControlStructure/Component[@ComponentType="%s"]' % comptype)

    def chiElem(self, idval):
        chi = ET.Element('CHImageIDs')
        pqid = ET.SubElement(chi, 'PQID')
        pqid.text = unicode(idval)
        return chi

    def removeEmptyLines(self, text):
        # Convert the string to an array, iterate over the array discarding blanks,
        # appending the rest to a new string. Return the new string.
        textArray = text.split('\n')
        ret = ''
        for w in textArray:
            if not w == '':
                ret += w + '\n'
        return ret
