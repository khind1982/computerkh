import sys

from confreader import ConfReader
from cstoreerrors import RescaleFactorUndefinedError, CorruptXMLError
from cstoreerrors import ImageFileMismatchError
from streams.etreestream import EtreeStream
from pagefilehandler import PagefileHandler

appconfig = ConfReader()


def build_pagefiles(product, dataroot, msq, log):
    log.debug("Test the logging")
    streamOpts = 'dataRoot=%s' % dataroot
    print('buildpagefiles', product)
    if appconfig.has_option(product, 'source_encoding'):
        streamOpts = '%s,encoding=%s' % (
            streamOpts,
            appconfig.get(product, 'source_encoding'))
    for doc in EtreeStream({'stream': '*.xml',
                            'streamOpts': streamOpts,
                            'logger': log, 'msq': msq}).streamdata():
        xml = doc.data
        docID = doc._cfg['pruned_basename']
        if product not in ['art', 'ger', 'feer']:
            product = doc._cfg['product']
        try:
            pfh = PagefileHandler(xml, doc._cfg['filename'], product)
        except ImageFileMismatchError as e:
            print >> sys.stderr, "Image mismatch: %s" % e
            msq.append_to_message('Image name mismatch', e)
            log.error("Image name mismatch: %s", e)
            continue

        try:
            print >> sys.stderr, "%s:\tpagemap..." % docID,
            pfh.update_or_create_pagefiles()
            print >> sys.stderr, " hit highlighting...",
            pfh.generate_hit_highlighting_tables()
        except RescaleFactorUndefinedError as e:
            print e
            print >> sys.stderr, "No rescale factor"
            msq.append_to_message(
                'No rescale factor for IDs (No pagefile generated)', docID)
            log.error(
                "Missing rescale factor for %s. No pagefile generated.", docID)
            continue
        except CorruptXMLError as e:
            print >> sys.stderr, "Corrupt XML: %s" % e
            msq.append_to_message(
                'Corrupt XML - illegal characters in source file %s (%s)' % (
                    docID, e.message), e)
            log.error(
                'Corrupt XML - illegal characters in source file %s? (%s)',
                docID, e.message)
            continue

        print >> sys.stderr, " done."


def build_hit_highlighting_tables(dataroot):
    streamOpts = 'dataRoot=%s' % dataroot
    for doc in EtreeStream(
            {'stream': '*.xml', 'streamOpts': streamOpts}).streamdata():
        xml = doc.data
        docID = doc._cfg['pruned_basename']

        print >> sys.stderr, "hit highlighting: %s" % docID

        product = doc._cfg['product']

        srcfile = doc._cfg['filename']

        pfh = PagefileHandler(xml, srcfile, product)

        pfh.generate_hit_highlighting_tables()
