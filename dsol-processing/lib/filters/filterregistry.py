# pylint:disable-msg=W0612
# If you ever need to register a new Stream type,
# here's the place to do it. You MUST follow the same
# format as those below, or things will break.

registry = {
#   filter     module name     class name

    'gs4xml':  ['gs4xml',      'GS4Xml'],
    'iimpref': ['iimpref',     'IIMPRef'],
    'vogue':   ['voguefilter', 'VogueFilter'],
    'oupfil':  ['oxupfilter',  'OxupFilter'],
    'dev':     ['devfilter',   'DevFilter'],
}

import sys
def import_filter(filtername):
    outputfilter = __import__(registry[filtername][0], globals(), locals(), [registry[filtername][1]], level=1)
    sys.modules['FilterProxy'] = eval("outputfilter.%s" % registry[filtername][1])
