#!/usr/local/bin/python2.6
# -*- mode: python -*-
# pylint: disable = no-member

import sys, os, re
#sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))
sys.path.insert(1, '/packages/dsol/lib/python')

import lxml.etree as ET
from xml.sax.saxutils import unescape

from lxml.builder import E

from commonUtils import textUtils
from SequenceDict import SequenceDict  # pylint:disable=F0401
from EntityShield import protect  # pylint:disable=F0401
from lutbuilder import buildLut   # pylint:disable=F0401


# This file contains helper functions to help abstract display logic out of the template files,
# allowing them to concentrate on layout and not processing.

class GS4XMLHelper(object):
    # Set shared state to an initial empty dict. This allows us to
    # populate it at first instantiation with dicts that refer to
    # methods on the class that are not available when the class
    # is first being parsed and processed.
    _dict = {
        }

    def __init__(self):
        # Set __dict__ to the empty _dict, defined above.
        self.__dict__ = self._dict
        # We can now force populating __dict__ by accessing a member we know
        # won't be defined the first time through. This works because __dict__
        # is a reference to _dict, initialised in the class-level scope to the
        # empty dict. It is the same object. Resistance is futile. You will be
        # assimilated.
        try:
            self.vogue_deep_indexing_elements
        except AttributeError:
            # To implement Vogue deep indexing, we need to be careful that all
            # the parts go in the output in the right order. Use a dispatch
            # table to call the appropriate render function. We'll go through
            # the dispatch table's keys by iterating over a list that holds the
            # elements in the desired order.
            self.vogue_deep_indexing_elements = [
                'ImageSequence', 'ImageStartPage', 'ImageCategory', 'Credits',
                'Caption', 'Description', 'Copyright', 'Pictured',
                'DesignerBrand', 'DesignerPerson', 'Material', 'Trend', 'Color',
                'Print', 'ImageKeywords', 'ImageCreator', 'ImageTag',
                ]

            self.vogue_deep_indexing_function_mapping = {
                'ImageSequence': GS4XMLHelper.render_vogue_image_string,
                'ImageStartPage': GS4XMLHelper.render_vogue_image_string,
                'ImageCategory': GS4XMLHelper.render_vogue_image_string,
                'Credits': GS4XMLHelper.render_vogue_image_string,
                'Caption': GS4XMLHelper.render_vogue_image_string,
                'Description': GS4XMLHelper.render_vogue_image_string,
                'Copyright': GS4XMLHelper.render_vogue_image_string,
                'Pictured': GS4XMLHelper.render_vogue_image_list,
                'DesignerBrand': GS4XMLHelper.render_vogue_image_list,
                'DesignerPerson': GS4XMLHelper.render_vogue_image_list,
                'Material': GS4XMLHelper.render_vogue_image_list,
                'Trend': GS4XMLHelper.render_vogue_image_list,
                'Color': GS4XMLHelper.render_vogue_image_list,
                'Print': GS4XMLHelper.render_vogue_image_list,
                'ImageKeywords': GS4XMLHelper.render_vogue_image_keywords,
                'ImageCreator': GS4XMLHelper.render_vogue_image_string,
                'ImageTag': GS4XMLHelper.render_vogue_image_list,
                }

            self.vogue_namespaces = buildLut('mstar/vogue_xml_namespaces.lut')

            # This is a little strained, due to limitations in the
            # implementation in SequenceDict.  I will try to find a better
            # implementation...
            self._compTypes = SequenceDict()
            self._compTypes['mstar_lm_media_id'] = GS4XMLHelper._buildSimpleValue
            self._compTypes['InlineImageCount'] = GS4XMLHelper._buildSimpleValue
            self._compTypes['ImageOrder']       = GS4XMLHelper._buildImageOrder
            self._compTypes['OrderCategory']    = GS4XMLHelper._buildSimpleValue
            self._compTypes['Order']            = GS4XMLHelper._buildSimpleValue
            self._compTypes['PageCount']        = GS4XMLHelper._buildSimpleValue
            self._compTypes['CHImageIDs']       = GS4XMLHelper._buildCHImageIDs
            self._compTypes['Representation']   = GS4XMLHelper._buildRepresentation
            # This is a special case for the multiple representations needed for
            # inline images in IIMPA/Inno
            self._compTypes['InnoImgReprs']   = GS4XMLHelper._buildInnoImgReprs
            # Vogue has multiple Representations for images. This is an attempt
            # at a more abstracted approach than that employed by
            # GS4XMLHelper._buildInnoImgReprs
            self._compTypes[
                'MultipleComponents'] = GS4XMLHelper._buildMultipleComponents

            self._textInfoTypes = {'fullText': u'Text',
                                   'dirtyAscii': u'HiddenText'}

            # A list of the allowed elements that can appear under
            # //Contributors/Contributor.  These will be needed for PAO/PIO, so
            # we can be sure we get the values out of the contributor dict in
            # the right order. Therefore, if you need to add a new element to
            # this list, make sure it is the right place, or your output will
            # fail schema validation and won't pass through ingest.
            self._contrib_elements = [
                'PersonTitle',
                'NameSuffix',
                'ContribCompanyName',
                'OrganizationName',
                'OriginalForm',
                ]

    def insertDate(self, date, tag, indent=4, undated=False):
        ret = ' ' * indent +   '<' + tag
        if undated == True:
            ret += ' Undated="true"'
        ret += '>' + date + '</' + tag + '>\n'
        return ret

    def buildObjectBundleData(self, bundle):
        ret = '  <ObjectBundleData>\n'
        for attr in bundle.keys():
            ret += '    <' + attr + '>' + bundle[attr] + '</' + attr + '>\n'
        ret += '  </ObjectBundleData>\n'
        return textUtils.cleanAndEncode(ret, strip=False, escape=False)

    def _buildObjectID(self, objectid):
        # If the link is a JSTORSICI, the content should be escaped
        pre = '      <ObjectID'
        for attr in '''IDOrigin IDType'''.split():
            if attr in objectid:
                pre += ' ' + attr + '="' + objectid[attr] + '"'
        pre += '>'
        post = '</ObjectID>\n'
        if 'IDType' in objectid and objectid['IDType'] == 'JSTORSICI':
            val = textUtils.cleanAndEncode(objectid['value'])
        else:
            val = textUtils.cleanAndEncode(objectid['value'], strip=False, escape=False)
        pre = textUtils.cleanAndEncode(pre, strip=False, escape=False)
        post = textUtils.cleanAndEncode(post, strip=False, escape=False)
        return pre + val + post

    @staticmethod
    def buildObjectID(objectid):
        objectid_fragment = E.ObjectID(
            objectid['value'], IDType=objectid['IDType'])
        if 'IDOrigin' in objectid.keys():
            objectid_fragment.set('IDOrigin', objectid['IDOrigin'])
        return ET.tostring(
            objectid_fragment, pretty_print=True).replace('amp;amp;', 'amp;')

    def buildTerms(self, terms):
        terms_data = ET.Element('Terms')
        for term in terms:
            terms_data.append(self.buildTerm(term))
        return ET.tostring(terms_data, pretty_print=True)
        # termsForTemplate = ''
        # pre = textUtils.cleanAndEncode('    <Terms>\n', strip=False, escape=False)
        # for term in terms:
        #     termsForTemplate += self.buildTerm(term)
        # post = textUtils.cleanAndEncode('    </Terms>\n', strip=False, escape=False)
        # return pre + termsForTemplate + post

    # def _buildTerm(self, term):
    #     print term
    #     pre = '      <' + term['TermType']
    #     if 'attrs' in term.keys():
    #         for k,v in term['attrs'].items():
    #             pre += ' ' + k + '="' + v + '"'
    #     pre += '>\n'
    #     val = ''
    #     for k,v in term['values'].items():
    #         val += '        <' + k + '>' + v + '</' + k + '>\n'
    #     post = '      </' + term['TermType'] + '>\n'
    #     return pre + val + post

    @staticmethod
    def buildTerm(term):
        term_elem = ET.Element(term['TermType'])
        if 'attrs' in term.keys():
            for k, v in term['attrs'].items():
                try:
                    # If an attribute comes in with a value of None,
                    # we want to ignore it, and not fail.
                    term_elem.set(k, v)
                except TypeError:
                    pass
        for k, v in term['values'].items():
            ET.SubElement(term_elem, k).text = v
        return term_elem
            #return ET.tostring(term_elem, pretty_print=True)


    def _tidyFullTextEntities(self, fullText):
        # All full text gets filtered through this before it is returned to the template, so
        # here is the place to put any code that needs to be run to tidy up weird markup etc.

        # This currently just clears up a problem in single IIPA record. It now only gets called for IIPA
        # records, as tested in the calling method (buildFullText)
        return re.sub(r'<(\[[^>]*)>', r'&lt;\1&gt;', textUtils.cleanAndEncode(fullText, strip=False, escape=False))

    def renderFullText(self, fullText):
        ret = '    ' + fullText #+ '\n'
        return textUtils.cleanAndEncode(ret, strip=False, escape=False, entities={'&': u'&amp;'})
        #return self._tidyFullTextEntities(ret)

    def buildFullText(self, textInfo, product=None):
        ret = '    <TextInfo>\n'
        for text in textInfo.keys():
            if type(textInfo[text]) is dict:
                # If we are dealing with IIMP or IIPA, the full text should not be escaped,
                # if it comes from the Innodata cache.
                # This is possibly also true of PRISMA, but I haven't yet tested it...
                # I'm using `escapep' for the flag, since escape is a keyword argument name and
                # so would collide. It follows the LISPish habit of shoving a `p' on to a name
                # to turn it into a predicate, since we can't use the Rubyish approach of adding
                # a question mark...
                if product == 'iipa' or product == 'iimp':
                    escapep = False
                else:
                    escapep = True
                # If it's a dict, break up the bits (This is for PRISMA full text)
                ret += '      <' + self._textInfoTypes[text]
                try:
                    for k in textInfo[text]['attrs'].keys():
                        ret += ' ' + k + '="' + textInfo[text]['attrs'][k] + '"'
                except KeyError:
                    pass
                ret += '>\n<![CDATA['
                ret += textUtils.cleanAndEncode(textInfo[text]['value'], escape=escapep).strip() + ']]>\n      </Text>'
            else:
                # Otherwise, it's a simple string
                ret += '      <' + self._textInfoTypes[text] + '><![CDATA['
                ret += textInfo[text].strip()
                ret += ']]></' + self._textInfoTypes[text] + '>\n'
        ret += '\n    </TextInfo>\n'
        if product == 'iipa' or product == 'iimp':
            return self._tidyFullTextEntities(ret)
        else:
            return ret

    def buildLink(self, link):
        # These need to be built in three parts, because we need to strip and escape the value,
        # but NOT the surrounding markup.
        linkType = link['linkType']
        pre  = '      <' + linkType + ' '
        for attr in link['attrs'].keys():
            pre += attr + '="' + link['attrs'][attr]
        pre += '">'
        pre = textUtils.cleanAndEncode(pre, strip=False, escape=False)
        val = textUtils.cleanAndEncode(link['linkValue'])
        post = textUtils.cleanAndEncode('</' + linkType + '>\n', strip=False, escape=False)
        return  pre + val + post


    def buildComponent(self, component):
        ret = '  <Component ComponentType="' + component['ComponentType'] + '">\n'
        for compType in self._compTypes.keys():
            if compType in component.keys():
                if type(component[compType]) is list:
                    for item in component[compType]:
                        ret += '    ' + self._compTypes[compType](self, item)
                elif type(component[compType]) is dict:
                    ret += '    ' + self._compTypes[compType](self, component[compType])
                else:
                    ret += '    ' + self._compTypes[compType](self, compType, component[compType])
        ret += '  </Component>\n'
        return textUtils.cleanAndEncode(ret, strip=False, escape=False)
#        return ret

    def _buildCHImageIDs(self, component):
        ret = '<CHImageIDs>\n      <CHID>' + component['values']['CHID'] + '</CHID>\n    </CHImageIDs>\n'
        return textUtils.cleanAndEncode(ret, strip=False)
        #return ret

    def _buildInnoImgReprs(self, component):
        ret = ''
        for reprType in component['RepresentationTypes']:
            # To get things lined up nicely in the output.
            if reprType == 'Full':
                ret += '<Representation RepresentationType="' + reprType + '">\n'
            else:
                ret += '    <Representation RepresentationType="' + reprType + '">\n'
            for item in ['MimeType', 'Resides', 'MediaKey']:
                ret += '      <' + item + '>' + component['values'][item] + '</' + item + '>\n'
            ret += '    </Representation>\n'
        return textUtils.cleanAndEncode(ret, escape=False, strip=False)

    def _buildRepresentation(self, component):
        ret = '<Representation RepresentationType="' + component['RepresentationType'] + '">\n'
        for item in ['MimeType', 'Resides', 'ImageType', 'WordMapCoords', 'Color', 'LayoutInfo', 'Options', 'Bytes', 'PDFType', 'Misc', 'Seconds', 'RepId', 'ResourceId', 'Scanned', 'LegacyFormat', 'CHImageHitHighlighting', 'MediaKey', 'IllustrationInfo']:
            if item in component['values'].keys():
                ret += '      <' + item + '>' + component['values'][item] + '</' + item + '>\n'
        ret += '    </Representation>\n'
        return textUtils.cleanAndEncode(ret, escape=False, strip=False)

    # In order to trigger this method, package up your Components in a list in your Mapping class,
    # keyed with the string 'MultipleComponents'.
    # The list is exploded in buildComponent, with each item being passed in here. It takes a reference
    # to the component type, then tries first to treat the passed component as a complex type, then as
    # a simple value type.
    def _buildMultipleComponents(self, component):
        compType = component.keys()[0]
        try:
            return self._compTypes[compType](self, component[compType])
        except TypeError:
            # This falls through to the buildSimpleValue cases (PageCount, etc)
            return self._compTypes[compType](self, compType, component[compType])

    def _buildImageOrder(self, component):
        ret = '<Name>' + component['values']['Name'] + '</Name>\n'
        ret += '  <OrderCategory>' + component['values']['OrderCategory'] + '</OrderCategory>\n'
        ret += '  <Order>' + component['values']['Order'] + '</Order>\n'
        return textUtils.cleanAndEncode(ret, False)

    def _buildSimpleValue(self, compType, component):
        ret = '<' + compType + '>' + component + '</' + compType + '>\n'
        return ret

    # This implementation is now deprecated - the new implementation below,
    # buildProduct(), should be used instead. This is left here until we are
    # happy the new versin works correctly.
    def _buildProduct(self, product):
        ret = ''
        for prod in product.keys():
            ret += '    <' + prod + '>\n'
            for item in product[prod].keys():
                if item == 'CHIMPA-AltJrnlTitles':
                    ret += '      <CHIMPA-AltJrnlTitles>\n'
                    for altTitle in product[prod][item]:
                        ret += '        <CHIMPA-AltJrnlTitle>' + altTitle + '</CHIMPA-AltJrnlTitle>\n'
                    ret += '      </CHIMPA-AltJrnlTitles>\n'
                elif type(product[prod][item]) == list:
                    for thing in product[prod][item]:
                        for bit in thing.split('/'):
                            ret += '      <' + item + '>' + bit + '</' + item + '>\n'
                elif type(product[prod][item]) == dict:
                    for k,v in product[prod][item]:
                        ret += '      <' + item + '>\n'
                        ret += '        <' + k + '>' + v + '</' + k + '>\n'
                        ret += '      </' + item + '>\n'
                else:
                    ret += '      <' + item + '>' + product[prod][item] + '</' + item + '>\n'
            ret += '    </' + prod + '>\n'
        # Need to pass the value from cleanAndEncode through protect to safely shield
        # ampersands embedded in some of these fields.
        return protect(textUtils.cleanAndEncode(ret, strip=False, escape=False))

    def buildProduct(self, product):
        elems = ''
        for prod in product.keys():
            elem = ET.Element(prod)
            for item in product[prod].keys():
                if item == 'CHIMPA-AltJrnlTitles':
                    alt_titles_elem = ET.Element('CHIMPA-AltJrnlTitles')
                    elem.append(alt_titles_elem)
                    for alt_title in product[prod][item]:
                        alt_title_elem = ET.Element('CHIMPA-AltJrnlTitle')
                        alt_title_elem.text = alt_title
                        alt_titles_elem.append(alt_title_elem)
                elif type(product[prod][item]) == list:
                    for thing in product[prod][item]:
                        for part in thing.split('/'):
                            sub_elem = ET.Element(item)
                            sub_elem.text = part
                            elem.append(sub_elem)
                elif type(product[prod][item]) == dict:
                    for k, v in product[prod][item]:
                        sub_elem = ET.Element(item)
                        sub_sub_elem = ET.Element(k)
                        sub_sub_elem.text = v
                        sub_elem.append(sub_sub_elem)
                        elem.append(sub_elem)
                else:
                    sub_elem = ET.Element(item)
                    sub_elem.text = product[prod][item]
                    elem.append(sub_elem)
            elems = '%s%s' % (elems, ET.tostring(elem, pretty_print=True))
        return elems

    def renderImageInfo(self, image, productID):
        ret = '    <ImageInfo TermVocab="%s">\n' % productID.upper()
        for element in self.vogue_deep_indexing_elements:
            try:
                ret += self.vogue_deep_indexing_function_mapping[element](self, image, element)
            except KeyError:
                # We get here if the current element doesn't appear in the
                # image that was passed in.
                pass

        ret += '    </ImageInfo>\n'
        return ret

    def render_vogue_image_string(self, image, element):
        # This renders out all items that are just simple strings
        try:
            value = textUtils.cleanAndEncode(image[element])
        except TypeError:
            value = unicode(image[element])
        if value == '':
            return ''
        return "      <%s>%s</%s>\n" % (element, value, element)

    def render_vogue_image_list(self, image, element):
        # This renders out those elements that can occur more than once.
        value = ''
        if len(image[element]) > 0:
            for item in [item for item in image[element] if item is not None]:
                value += "      <%s>%s</%s>\n" % (element, item, element)
        return value

    def render_vogue_image_keywords(self, image, element):
        # Image keywords are a bit more complex.
        # We need to iterate over the image['imageCategory'] lxml.etree._Element, extracting
        # each imageCategoryName, and each contained imageKeyword and imageDescriptor.

        ret = '      <ImageKeywords>\n'

        # We need to keep track of the "SetNumber" so the app can figure out which groups of terms
        # belong to same hierarchy.
        for set_number, item in enumerate(image[element], 1):
            # Grab the category name (the top level keyword)
            category_name = item.xpath('cnp:imageCategoryName', namespaces=self.vogue_namespaces)[0].text
            # Grab the imageKeywords under this imageCategory
            keywords = item.xpath('cnp:imageKeyword', namespaces=self.vogue_namespaces)
            ret += '        <ImageKeyword Level="1" SetNum="%s">%s</ImageKeyword>\n' % (set_number, category_name)

            # Iterate over the keywords, adding the appropriate imageKeywordName value, and
            # extracting the contained imageDescriptors.
            for keyword in keywords:
                keyword_text = keyword.xpath('cnp:imageKeywordName', namespaces=self.vogue_namespaces)[0].text
                # We can have empty second level elements here. Don't include them in the output.
                if keyword_text is not None:
                    ret += '        <ImageKeyword Level="2" SetNum="%s">%s</ImageKeyword>\n' % (set_number, keyword_text)
                for descriptor in [kw.text for kw in keyword.xpath('cnp:imageDescriptor', namespaces=self.vogue_namespaces) if kw.text is not None]:
                    ret += '        <ImageKeyword Level="3" SetNum="%s">%s</ImageKeyword>\n' % (set_number, descriptor)

        ret += '      </ImageKeywords>\n'
        return ret

    def buildContributors(self, contributors, otherAuthors=None, preformatted=None):
        if preformatted is not None:
            contribs = ET.Element('Contributors')
            if otherAuthors is not None:
                contribs.set('AndOtherAuthors', 'true')
            for contributor in contributors:
                for elem in contributor:
                    elem.text = unescape(elem.text)
                contribs.append(contributor)
            return ET.tostring(contribs)

        # Take the contributors data and render it.
        if otherAuthors is not None:
            ret = '    <Contributors AndOtherAuthors="true">\n'
        else:
            ret = '    <Contributors>\n'

        for contributor in contributors:
            if textUtils.isStringy(contributor['contribvalue']):
                contributor['contribvalue'] = {'OriginalForm': contributor['contribvalue']}

            ret += '      <Contributor ContribRole="%s" ContribOrder="%s">\n' % (contributor['ContributorRole'], contributor['ContribOrder'],)
            for element_name in self._contrib_elements:
                try:
                    if contributor['contribvalue'][element_name] is not None:
                        try:
                            if contributor['IsNormalized'] is not None:
                                ret += '        <%s IsNormalized="%s">%s</%s>\n' % (element_name, contributor['IsNormalized'], contributor['contribvalue'][element_name], element_name,)
                        except KeyError:
                            ret += '        <%s>%s</%s>\n' % (element_name, contributor['contribvalue'][element_name], element_name,)
                except KeyError:
                    # If contributor['contribvalue'] doesn't have a key
                    # "element_name", do nothing.
                    pass

            try:
                if textUtils.isStringy(contributor['ContribDesc']):
                    contributor['ContribDesc'] = [contributor['ContribDesc']]
                for contrib_desc in [cd for cd in contributor['ContribDesc'] if cd is not None]:
                    ret += '        <ContribDesc HTMLContent="true"><![CDATA[%s]]></ContribDesc>\n' % textUtils.cleanAndEncode(contrib_desc)  #contributor['ContribDesc']
            except KeyError:
                # Nothing to do if we don't have a ContribDesc member.
                pass

            try:
                if textUtils.isStringy(contributor['MiscRoleDesc']):
                    contributor['MiscRoleDesc'] = [contributor['MiscRoleDesc']]
                    for misc_role_desc in [mrd for mrd in contributor['MiscRoleDesc'] if mrd is not None]:
                        ret += '        <MiscRoleDesc>%s</MiscRoleDesc>\n' % misc_role_desc
            except KeyError:
                pass

            ret += '      </Contributor>\n'
        ret += '    </Contributors>\n'

        return ret


    def template_path(self, pathspec):
        # Construct the correct template path and return it.
        # For use in the display templates to tidy up include statements.
        # If pathspec contains a '/' character, assume we are calling for
        # a non-standard view from a directory other than ./lib/views/gs4xml
        # and pass pathspec unmolested. If it contains no '/', we want a
        # template from the standard location and need to add 'gs4xml'
        # to get the correct path.
        if '/' not in pathspec:
            pathspec = os.path.join('gs4xml', pathspec)
        return os.path.join(os.path.dirname(__file__), '../views', pathspec)


    def buildLanguageData(self, language):
        ret = ''
        if 'langName' in language.keys():
            ret += '      <RawLang>%s</RawLang>\n' % language['langName']
        ret += '      <ISO>\n'
        ret += '        <ISOCode>%s</ISOCode>\n' % language['langISOCode']
        ret += '      </ISO>\n'
        return ret

    # Have changed this to make it non product specific
    def insert_source_types(self, source_types, source_origin):
        if source_types is None:
            return
        ret = ''
        for item in source_types:
            ret += '    <SourceType SourceTypeOrigin="%s">%s</SourceType>' % (source_origin, item)
        return ret
