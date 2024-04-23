# -*- mode: python -*-
import mappings.rules.copyrightstatements.eima as ecs

__ecs = ecs.cs

def eima_copyright_statements():
    return __ecs

def known_jids():
    return __ecs.keys()
