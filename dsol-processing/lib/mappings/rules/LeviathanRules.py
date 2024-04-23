# -*- mode: python -*-

from decorators import catchEmptyList
from mappings.rules import general


@catchEmptyList('[untitled]')
def title(xml):
    try:
        _title = general.title(xml.find('.//title').text.rstrip())
    except AttributeError:
        _title = ''
    if _title == '':
        _title = doctype(xml)

    # print "TITLE: %s" % _title  # noqa
    return _title


def doctype(xml):
    x = xml.find('.//doctype1').text
    if '_' in x:
        w = x.split('_')
    else:
        w = x.split(' ')
    return (' ').join([word.capitalize() for word in w if word not in ['of']])


def pmid(_product, xml):
    return xml.findtext('.//journal/journalid')


def articleid(idstring):
    return idstring


def pcid(_product, filename):
    return '_'.join(filename.split('_')[0:-1])


def apdf(_product, xml):
    # If the source document has //apdf_available, use its value.
    # If it doesn't, set it to false as a safe default.
    apdf_available = xml.findtext('.//journal/apdf_available')
    if not apdf_available:
        apdf_available = "false"

    return apdf_available


pcid_img_path = pcid
