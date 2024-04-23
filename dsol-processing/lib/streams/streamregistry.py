# pylint:disable-msg=W0612
# If you ever need to register a new Stream type,
# here's the place to do it. You MUST follow the same
# format as those below, or things will break

registry = {
#   stream       module name           class name

    'xml':       ['xmlstream',         'XmlStream'],
    'prismaxml': ['prismaxmlstream',   'PrismaXmlStream'],
    'sql':       ['sqlstream',         'SqlStream'],
    'bp':        ['bpstream',          'BPStream'],
    'prismasql': ['prismasqlstream',   'PrismaSQLStream'],
    'text':      ['textstream',        'TextStream'],
    'xrecord':   ['multirecordstream', 'MultiRecordStream'],
    'etree':     ['etreestream',       'EtreeStream'],
    'genfile':   ['genfilestream',     'GenFileStream'],

}

import sys

def import_stream(streamtype):
    try:
        stream = __import__(registry[streamtype][0], globals(), locals(), [registry[streamtype][1]], level=1)
    except KeyError:
        print >> sys.stderr, ("%s: undefined stream type" % streamtype)
        print >> sys.stderr, ("\tTo register a new stream, place the module in lib/streams/,")
        print >> sys.stderr, ("\tand add its details to the 'registry' dict in\n\t %s" % __file__)
        exit(1)
    except ImportError as e:
        print sys.path
        print streamtype
        raise e

    sys.modules['StreamProxy'] = eval("stream.%s" % registry[streamtype][1])
