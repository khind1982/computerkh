''' A module containing CStore specific errors and exceptions '''

class CStoreError(Exception): pass

class CStoreDataStreamError(CStoreError): pass
class CStoreDataStreamSuffixError(CStoreError): pass

class PrismaXmlStreamException(CStoreDataStreamError): pass
class PrismaSQLStreamException(CStoreDataStreamError): pass

class PrismaSQLStreamUnknownVariantError(PrismaSQLStreamException): pass

class XmlStreamArgumentError(CStoreError): pass

class CStoreMappingError(CStoreError): pass

class SkipRecordException(Exception): pass

class PrismaHapiRecordException(SkipRecordException): pass

class UndefinedHookException(CStoreError): pass

class HookException(CStoreError): pass

class BeforeHookException(HookException): pass
class RunCompleteException(BeforeHookException):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class FilterError(CStoreError): pass


class UnknownFilterError(FilterError): pass


import StringIO
class InvalidTransformationError(FilterError):
    def __init__(self, msg, record=None, original_msg=None, text=None, lineno=None):
        self.msg = msg
        self.record = record
        self.original_msg = original_msg
        self.text = text
        self.lineno = lineno
        self.bad_line = StringIO.StringIO(self.record).readlines()[self.lineno-1]


class XmlValidationError(CStoreError): pass

class SteadyStateUnchanged(CStoreError): pass

class PagefileEmptyWordError(CStoreError): pass

class RescaleFactorUndefinedError(CStoreError): pass

class CorruptXMLError(CStoreError): pass

class ImageFileMismatchError(CStoreError): pass

class DateError(CStoreError): pass
class UnhandledDateFormatException(DateError): pass
class IncompleteTextualDateError(DateError): pass
