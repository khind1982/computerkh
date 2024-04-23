# -*- mode: python -*-

from commonUtils.textUtils import cleanAndEncode as clean

def title(value):
    # Pass the value through textUtils.cleanAndEncode,
    # and remove a trailing backslash. This is necessary
    # because in the event a string ends in '\', it mangles
    # any SQL it is injected into.
    return _debackslash(clean(value))

sanitized_text = title

def _debackslash(value):
    return value if not value.endswith('\\') else _debackslash(value[0:-1])

# This is used in the APSMapping module in the _buildLayoutInfo method. In AAA,
# we sometimes need to add a letter to the record and image identifiers to
# distinguish issues published on the same day. This function returns the last
# digit in a string, or None if no digit is found.
def get_last_digit(string):
    try:
        return string[-1] if string[-1].isdigit() else get_last_digit(string[0:-1])
    except IndexError:
        return None
