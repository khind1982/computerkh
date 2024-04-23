# pylint:disable=W0612
# Similar to the stream importer, register new mapping types
# here. Be sure to follow the formula, or things won't work right...

registry = {
#    mappingname,  module name,    mapping class

    'impa':    ['impamapping',    'IMPAMapping'],
    'prisma':  ['prismamapping',  'PRISMAMapping'],
    'bp':      ['bpmapping',      'BPMapping'],
    'imparef': ['imparefmapping', 'IMPARefMapping'],
    'vogue':   ['voguemapping',   'VogueMapping'],
    'eima':    ['eimamapping',    'EIMAMapping'],
    'oup':     ['oupmapping',     'OupMapping'],
    'vogueetree': ['vogueetreemapping', 'VogueMapping'],
    'pio':     ['piomapping', 'PIOMapping'],

    'wwd':     ['wwdmapping', 'WWDMapping'],
    'aaa':     ['wwdmapping', 'WWDMapping'],
    'trj':     ['wwdmapping', 'WWDMapping'],

    'leviathan': ['leviathanmapping', 'LeviathanMapping'],

    'dnsa':    ['dnsamapping', 'DNSAMapping'],
    'film':    ['filmmapping', 'FilmMapping'],
    'gerritsen': ['gerritsenmapping', 'GerritsenMapping']
}

import sys
def import_mapping(mappingname):
    try:
        mapping = __import__(registry[mappingname][0], globals(), locals(), [registry[mappingname][1]], level=1)
    except KeyError:
        print >> sys.stderr, ("%s: undefined mapping type" % mappingname)
        print >> sys.stderr, ("\tTo register a new mapping, place the module in lib/mappings/,")
        print >> sys.stderr, ("\tand add its details to the 'registry' dict in\n\t %s" % __file__)
        exit(1)

    sys.modules['MappingProxy'] = eval("mapping.%s" % registry[mappingname][1])
    #sys.modules['MappingProxy'] = "mapping.%s" % registry[mappingname][1]
