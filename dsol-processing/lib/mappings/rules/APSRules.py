# -*- mode: python -*-

from mappings.rules import general


# from commonUtils.textUtils import cleanAndEncode as clean
from decorators import catchEmptyList

# Rules for APS derived content sets.

# In APS derived sets, the document title is the text value of
# the APS_title element, or, if that's empty or not present,
# take the value of the "type" attribute on the APS_article
# element - essentially making a blank title the same as the
# document type.


@catchEmptyList('[untitled]')
def title(xml):
    try:
        _title = general.title(xml.find('APS_title').text.rstrip())
    except AttributeError:
        _title = ''
    if _title == '':
        _title = doctype(xml)

    return _title


def doctype(xml):
    try:
        x = xml.getroot().attrib['type']
    except AttributeError:
        x = xml.attrib['type']
    if '_' in x:
        w = x.split('_')
    else:
        w = x.split(' ')
    return ' '.join([word.capitalize() for word in w if word not in ['of']])


def pmid(product, xml):
    # EIMA doesn't (yet) use the product name as a prefix for its journal
    # identifiers.
    if product == "eima":
        product = ''
    try:
        ret = ''.join(
            [product.upper(),
             xml.getroot().attrib['pmid'].rstrip().replace(
                 product.upper(), '')])
    except AttributeError:
        ret = ''.join(
            [product.upper(),
             xml.attrib['pmid'].rstrip().replace(product.upper(), '')])
    return ret


def articleid(idstring):
    return _de_aps_ify(idstring)


jid = issueid = articleid


def pcid(_product, filename):
    return '_'.join(_de_aps_ify(filename).split('_')[0:-1])


def apdf(_product, xml):
    # APS-based products don't (yet) support APDF, so just return "false"
    # See the LeviathanRules file for an actual implementation, if needed.
    return "false"


# We need this as well as the function above, because EIMA is inconsistent
# in its use of the PCID. Sometimes, we need the PCID without the APS_ prefix
# (which is handled by pcid()), and sometimes we need it WITH the prefix...
# This should only affect EIMA, since everywhere else, there is no APS_
# prefix to worry about, and so both of these function will return the same
# (correct) value.
def pcid_img_path(_product, filename):
    return '_'.join(filename.split('_')[0:-1])


# used to get just the date part of issue ids, for use by the mserv
# script
def mserv_issueid(issueidstring):
    return issueidstring.split('_')[-1]


# Remove the APS_ prefix from image names/article IDs.
def _de_aps_ify(string):
    return string.replace('APS_', '')
