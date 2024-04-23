# -*- mode: python -*-

''' Functions for manipulating characters.

So far we only have a new error handler for the codecs module,
which prints unencodable characters as hexadecimal character
references.
'''

import codecs

def xmlcharrefreplacehex_errors(exc):
    '''Error handler for the codecs module. The function is triggered when
    codecs.encode encounters a character that can't be represented in
    the requested encoding. It receives an instance of
    UnicodeEncodeError and returns a tuple containing the hexadecimal
    character reference, ready for use in an XML document, and the
    position in the string after the character that caused the exception
    to be raised, so the encode method knows where to resume processing.
    '''

    problem_char = exc.object[exc.start]
    hexed = str(hex(ord(problem_char))).replace('0x', '').upper()
    if len(hexed) == 2:
        hexed = "00%s" % hexed
    return (u"&#x%s;" % hexed, exc.end)

codecs.register_error('xmlcharrefreplacehex', xmlcharrefreplacehex_errors)


