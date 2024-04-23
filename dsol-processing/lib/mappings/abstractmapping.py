# -*- mode: python -*-
# pylint:disable-msg=W0201,W0142,E1101,W0212,C0301

import fnmatch
import hashlib
import inspect
import logging
import os
import re
import sys
import time
import warnings
import ConfigParser

import xml.sax.saxutils as _sutils

from collections import namedtuple
from cstoreerrors import SkipRecordException, SteadyStateUnchanged
from cstoreerrors import RunCompleteException
from cstoreerrors import UndefinedHookException
from cstoreerrors import UnhandledDateFormatException
from commonUtils import dateUtils, textUtils, miscUtils, langUtils
from commonUtils.textUtils import EntRefError

from csstruct import LegacyRecord, GS4Record

from confreader import ConfReader


log = logging.getLogger('tr.mapping.abstract')

# with warnings.catch_warnings():
#     warnings.simplefilter('ignore')
#     import MySQLdb


# This holds the app config file, cstore.config, and NOT
# the config dict that gets handed around as self._cfg.
appconf = ConfReader()

Term = namedtuple('Term', ['childelem', 'attrname'])
# Term is a namedtuple used to construct the Terms section of the document.

# Its attributes are:

# childelem - the name of the element in which the Term's value is stored.
# attrname - the name of the attribute associated with the Term itself.

# Instances of Term are used as the values in the __term_types dict, where the
# key is the name of the Term element.

# e.g. To specify a FlexTerm with child element of FlexTermValue, and an
# attribute named FlexTermType:

# {
# 'FlexTerm': Term(childelem='FlexTermValue', attrname='FlexTermType')
# }

# If the Term you are building doesn't have an attribute, set the
# attrname to None:

# {
# 'CompanyTerm': Term(childelem='CompanyName', attrname=None)
# }


# a simple convenience to convert "false, on, off, true, yes, no" etc to
# boolean
def to_bool(value):
    if value in ['1', 'yes', 'on', 'true']:
        return True
    elif value in ['0', 'no', 'off', 'false']:
        return False
    return None


# class PublicationIDs(object):
#     # We need to keep track of what publication IDs we have already seen, so
#     # that the appearance of a new one can be handled correctly. This class
#     # wraps a simple MySQL table in the mstarss db. It checks for a tuple of
#     # the publication ID and product name in the table. If it is found, no
#     # action is taken. If not found, then publication ID and product are
#     # inserted, and the publication ID is added to the 'unseen' member
#     # variable. This is then printed to STDERR upon completion of the run.

#     # The class uses the "Borg" design pattern, which appears to be somewhat
#     # simpler to implement in Python than the Singleton DP. Essentially, we can
#     # have as many instances as we like, but all share the same state - simply
#     # by rebinding the __sharedState dict to self.__dict__ upon instantiation.
#     # Since each instance holds a reference to the same __sharedState, any
#     # changes are propagated to all instances.

#     # This implementation of the Borg DP comes from
#     # http://code.activestate.com/recipes/66531/


#     connectionString = {'user': 'mstarss',
#                         'db': 'mstarss',
#                         'host': 'dsol.private.chadwyck.co.uk',
#                         'passwd': 'mstarss'}
#     dbConn = MySQLdb.connect(**connectionString)
#     __sharedState = {
#         'connectionString': connectionString,
#         'dbConn': dbConn,
#         'cursor': dbConn.cursor(),
#         'unseen': [],
#         }

#     def __init__(self):
#         self.__dict__ = self.__sharedState

#     def checkPubID(self, pubId, product):
#         # We are only interested in contents of one table - publicationids
#         queryString = """SELECT publicationid FROM publicationids WHERE publicationid = '%s' AND product = '%s';"""  # noqa
#         try:
#             self.dbConn.ping()
#         except:  # noqa
#             self.connect()
#         self.cursor.execute(queryString % (pubId, product))
#         data = self.cursor.fetchone()
#         if data is None or data == '':
#             self.unseenPubID(pubId, product)

#     def unseenPubID(self, pubId, product):
#         self.unseen.append(pubId)
#         self.cursor.execute(
#             """INSERT INTO publicationids (publicationid, product)
#             VALUES ('%s', '%s');""" % (pubId, product))
#         self.dbConn.commit()

#     def connect(self):
#         self.dbConn = MySQLdb.connect(**self.connectionString)
#         self.cursor = self.dbConn.cursor()


class AbstractMapping(object):
    __blocklist = {'empty': ''}
    __configFiles = {}
    for file in os.listdir('/packages/dsol/etc/mstar/'):
        if fnmatch.fnmatch(file, '*.conf'):
            config = ConfigParser.SafeConfigParser()
            config.optionxform = str  # Make options case sensitive
            config.read(os.path.join('/packages/dsol/etc/mstar', file))
            __configFiles[file.split('.')[0]] = config

    __term_types = {
        'FlexTerm': Term(childelem='FlexTermValue', attrname='FlexTermName'),
        'Term': Term(childelem='TermValue', attrname='TermType'),
        'CompanyTerm': Term(childelem='CompanyName', attrname=None),
        'GenSubjTerm': Term(childelem='GenSubjValue', attrname=None)
    }

    # Keep a count of the number of records transformed in this session.
    # Needs to be a class instance variable so it's available to all
    # instances. And in the instances, we need to say something like this:
    # self.__class__._transformedCount. Sometimes Python is so ugly, it hurts
    # my eyes...

    _transformedCount = 0

    # We only want one token per session (!)
    # The first time the class method is invoked, it creates the
    # token and stows it away for later reuse.
    @classmethod
    def sessionToken(cls):
        if not hasattr(cls, "_sessionToken"):
            # To be sure we get a unique session identifier, take the current
            # localtime (hour, minutes, seconds, year, month, date, day of the
            # year) and the current PID.
            rawstring = "%s-%s" % (
                time.strftime(
                    "%H:%M:%S:%Y:%B:%d:%j", time.localtime()), os.getpid(),)
            cls._sessionToken = hashlib.sha256(rawstring).hexdigest()
        return cls._sessionToken

    def _check_product_end_date(self):
        # If the current record belongs to a product that has
        # 'product_end_date' in its config stanza, check that
        # its date is less than or equal to the value in the config.
        if 'product_end_date' in self._cfg.keys():
            cut_off = int(self._cfg['product_end_date'])
            article_date = int(self._cfg['pruned_basename'].split('_')[1][:4])
            if article_date > cut_off:
                self.msq.append_to_message(
                    "Article date after product end date (%s). Not in output" %
                    cut_off, self._cfg['pruned_basename']
                )
                log.warning(
                    "%s: Article date after product end date (%s). Skipped.",
                    self._cfg['pruned_basename'], cut_off
                )
                return False
        # Either we don't have product_end_date set in the config,
        # or the record's date is valid.
        return True

    def __init__(self, record):
        self._defaultDelimiter = '|'
        self.rawrecord = record
        self._cfg = record._cfg

        if "pdf_representation" in self._cfg.keys():
            self.pdf_representation_required = to_bool(
                self._cfg['pdf_representation'])
        else:
            # Default to True
            self.pdf_representation_required = True

        # A simple message interface for logging messages for the operator.
        # Use to store messages about warnings etc that don't need to halt
        # execution, but which should nonetheless be remembered
        self.msq = self._cfg['msq']

        # Some products have cut-off point after which we should not
        # be building content. Check here to see if self._cfg contains
        # a key 'product_end_date', and check its value against the
        # record's date.
        if not self._check_product_end_date():
            raise SkipRecordException

        if "filename" in self._cfg.keys():
            self._srcFile = self._cfg['filename']
        self.record = LegacyRecord()
        self._fields = []
        self._check_seen()
        self.gs4 = GS4Record()
        # Grab the schema version details from the config file.
        self.gs4.minorVersion = self._cfg['schema_minor_ver']
        self.schema_major_version = self._cfg['schema_major_ver']

        # Most products will have a LegacyPlatform of 'CH'
        # However, EIMA should be mapped to 'HNP' (Historical NewsPapers)
        self.gs4.legacy_platform = u'CH'

        # This is a bit messy, but there is no easier way to get this in.
        self.gs4.relatedLegacyPlatform = u'PQ'
        # Component types callbacks. You can either add more here, or
        # add them in your subclass. Any that are used in more than one
        # product should be defined in this class. Only define the callback
        # in your subclass if it is not used elsewhere.
        self._componentTypes = {
            'Representation':    AbstractMapping._buildRepresentation,
            'CHImageIDs':        AbstractMapping._buildCHImagIDs,
            'InlineImageCount':  AbstractMapping._buildSimpleValue,
            'OrderCategory':     AbstractMapping._buildSimpleValue,
            'Order':             AbstractMapping._buildSimpleValue,
            'PageCount':         AbstractMapping._buildSimpleValue,
            'mstar_lm_media_id': AbstractMapping._buildSimpleValue,
            'MultipleComponents': AbstractMapping._buildMultipleComponents,
            }

        # A default, for cases where we haven't enabled the steady state checks
        self.gs4.action = "add"

        # If we haven't specifically asked for steady state not be used, make a
        # reference to the steady state handler object stored in the cfg dict.
        # The existence of this reference on self is tested to determine
        # whether or not to run the steady state checks.
        if self.doSteadyState is True:
            self.steadyStateHandler = self._cfg['steadyStateHandler']
            self.ssTableName = self._cfg['product']

        # if self.checkPubIDs() is True:
        #     self.pubIDHandler = PublicationIDs()
        #     self._cfg['pubIDHandler'] = self.pubIDHandler
        if self._cfg['product'] == 'art':
            self.productId = 'aaa'
        else:
            self.productId = self._cfg['product']
        self.gs4.productID = self.productId
        # Now we know what product we are handling, we can attach any end user
        # config file. These are all loaded when the app first starts, so we
        # don't have to reload for every record we inspect.
        try:
            self._cfg['usertunables'] = AbstractMapping.__configFiles[
                self.productId]
        except KeyError:
            self._cfg['usertunables'] = None

        # Check to see if there is a blocklist for this product, and read it in

        self.blocklist = self.__class__.__blocklist
        self.build_blocklist()

        # By default, we expect all records to have date information. Set that
        # expectation here. If a particular product needs to overrule that
        # default, its mapping simply needs to set this to True.
        self.gs4.undated = False

        # This tests the config file for a key 'unstructured' and if it is
        # present and true the ParentInfo information is omitted from the
        # output records
        if 'unstructured' in self._cfg.keys() and self._cfg[
                'unstructured'] == 'true':
            self.gs4.unstructured = True

    def build_blocklist(self):
        if self.blocklist.keys() == ['empty']:
            del(self.blocklist['empty'])
            blocklistpath = os.path.join(
                self._cfg['app_libdata'], 'blocklists', self._cfg['product'])
            if os.path.isdir(blocklistpath):
                for f in os.listdir(blocklistpath):
                    blocklist_for_f = [
                        line.strip() for line in
                        open(os.path.join(blocklistpath, f)).readlines()
                        if not line.startswith('#')]

                    if blocklist_for_f == [] or blocklist_for_f == ['*']:
                        blocklist_for_f = ['ALL']
                    self.blocklist[f] = blocklist_for_f

    def visual_feedback_printid(self):
        # We can also specify how much detail to print with visualFeedBack() -
        # some products have a single record per source file, so there is no
        # point in printing both the source file name and the record ID.
        # Others, such as IMPA and PIO, have multiple records per source file,
        # so it is useful to have the current record printed, to make tracking
        # down problems a bit easier.
        # if self.productId in ['eima', 'vogue', 'prisma']:
        if appconf.has_option(self.productId, 'recordperfile'):
            ret = self._cfg['basename']
        else:
            ret = "%s/%s" % (
                self.gs4.originalCHLegacyID, self._cfg['basename'])
        return ret

    def checkPubIDs(self):
        # Is checkpubids set to false in the config file? If so, return False.
        # If not, or if it's not set at all, return True (the default is to
        # checkpubids) '''
        try:
            if re.match(r'false', self._cfg['checkpubids'], re.IGNORECASE):
                return False
            else:
                return True
        except KeyError:
            return True
        except:  # noqa
            raise

    @property
    def ingest_schema(self):
        return os.path.join(
            os.path.abspath(
                os.path.join(
                    self._cfg['app_libdata'], 'mstar/ingestschemas')),
            self.schema_major_version.replace('.', '/'),
            'Ingest_v{major}.{point}.xsd'.format(
                major=self.schema_major_version,
                point=self.gs4.minorVersion))

    @property
    def global_schema_version(self):
        return 'Global_Schema_v{major_version}.xsd'.format(
                major_version=self.schema_major_version)

    @property
    def nossInConfig(self):
        ''' look in the self.cfg dict for a key 'noss' and value 'true'.
        This value comes from the cstore.config file.
        If the key is absent, or has any other value, return False '''
        try:
            if re.match(r'true', self._cfg['noss'], re.IGNORECASE):
                return True
            else:
                return False
        except KeyError:
            return False
        except:  # noqa
            # In case we get some other error, we need to know what it is.
            # It's probably important enough to halt execution.
            raise

    @property
    def doSteadyState(self):
        # Check to see if steady state is explicitly turned off, either on the
        # commandline (by using -m noss (in mappingOptions)), or in the
        # cstore.config file, by setting noss: true
        if 'noss' in self._cfg['mappingOptions'] or self.nossInConfig is True:
            return False
        else:
            return True

    def setSteadyStateToken(self, data):
        if self.doSteadyState is True:
            self._steadyStateToken = data

    def _checkSteadyState(self, recordid, checksum):
        if hasattr(self, 'steadyStateHandler'):
            self.recordid = str(recordid)
            checksum = str(checksum)

            if 'forcess' in self.cfg['mappingOptions']:
                log.info(
                    "Forcing steady state update %s",
                    self.gs4.originalCHLegacyID
                )
                self.steadyStateHandler.forceUpdate(
                    self.recordid, checksum, self.record.journalid
                )
            else:
                if 'ssnoupdate' in self.cfg['mappingOptions']:
                    log.debug(
                        "Steady state db not updated for %s",
                        self.gs4.originalCHLegacyID
                    )
                self.gs4.action = self.steadyStateHandler.checkForUpdate(
                    self.recordid, checksum, self.record.journalid
                )
                logger_info = (self.gs4.legacyID, self._cfg['basename'])
                if self.gs4.action == 'unchanged':
                    log.debug("Unchanged record %s, %s" % logger_info)
                    raise SteadyStateUnchanged
                elif self.gs4.action == 'add':
                    log.debug("New record %s, %s" % logger_info)
                elif self.gs4.action == 'change':
                    log.debug("Updated record %s, %s" % logger_info)

    def _mkChecksum(self, obj):
        return hashlib.sha512(str(obj)).hexdigest()

    def _increment_seen(self):
        self._cfg['seen'] += 1

    def _check_seen(self):
        self._seen()
        if 'recordCount' in self._cfg:
            if self._cfg['seen'] == self._cfg['recordCount']:
                raise RunCompleteException(
                    "Requested number of records processed")

    def _seen(self):
        if 'seen' not in self._cfg.keys():
            self._cfg['seen'] = 0

    def __getattr__(self, attrname):
        dictname = '_%s' % attrname
        if dictname in self.__dict__:
            return self.__dict__[dictname]
        else:
            raise AttributeError(
                'Instance (%s) has no attribute %s' % (
                    str(self.__class__), attrname))

    def before_hooks(self):
        self.deprecated_hook_call_syntax()
        self._run_hooks('_before_hooks')

    def after_hooks(self):
        self.deprecated_hook_call_syntax()
        try:
            self.is_blocked()
            self._run_hooks('_after_hooks')

            # These three callbacks should be run for EVERY SINGLE
            # DOCUMENT that goes through the system. Custom
            # after_hooks callbacks can be registered in your mapping
            # subclass in self._after_hooks and
            # self._after_hooks_always_run. The first group may cause
            # an exception to be raised, which can then result in a
            # record being omitted from the output. All callbacks
            # after the one raising the exception will not, unless
            # explicitly handled in your code, get executed, instead
            # causing the exception to be handled here. The second
            # group are executed in the finally: clause here, so are
            # guaranteed to be executed, even if an exception is
            # raised.
            self._set_object_id_in_config()
            self._do_steady_state_checks()
            # self._checkPubID()

        finally:
            self._run_hooks('_after_hooks_always_run')
            self.visualFeedBack()

    def _undefinedHook(self):
        raise UndefinedHookException

    def deprecated_hook_call_syntax(self):
        frstack = inspect.stack()
        caller = frstack[2][1]
        if not re.search('transform$', caller):
            if frstack[1][3] == "before_hooks":
                hookname = "before_hooks"
                define_instead = "self._before_hooks"
            else:
                hookname = "after_hooks"
                define_instead = "self._after_hooks and self._after_hooks_always_run"  # noqa
            log.warn("DEPRECATION WARNING! AbstractMapping.%s should not be overridden in derived classes. Instead, define your callbacks as methods on your derived class and list them, in the order you want them to run, in %s.", hookname, define_instead)  # noqa

    def _run_hooks(self, hook_list):
        if hasattr(self, hook_list):
            for method in getattr(self, hook_list):
                try:
                    method(self)
                except TypeError:
                    if re.search('<', str(method.__class__)):
                        print >> sys.stderr, "\n\nAn error occurred in %s\nwhile processing %s\n" % (method, hook_list)  # noqa
                        print >> sys.stderr, "self.record contains:\n"
                        print >> sys.stderr, self.record
                        print >> sys.stderr, "self.gs4 contains:\n"
                        print >> sys.stderr, self.gs4
                        print >> sys.stderr, "The error traceback was:\n"
                        raise
                    else:

                        log.warn("DEPRECATION WARNING! %s should be converted from a list of strings to a list of function references, in order to avoid the need to make calls to eval()", hook_list)  # noqa
                        try:
                            eval('self.%s()' % method)
                        except:  # noqa
                            print >> sys.stderr, "Failure in %s:" % method
                            print >> sys.stderr, inspect.stack()
                            raise
    # ++ HOOKS ++
    # These hook methods are to be called from the before_ or
    # after_hooks methods. As with the _computedValues, they should
    # not expect to take arguments except the implicit instance. There
    # are a few after_hooks that should be run for all instances of
    # any mapping, and these are called before any user-specified list
    # of methods.

    def _set_object_id_in_config(self):
        # Used by the validation code if it needs to write an error
        # report for a particular record.
        self._cfg['objectid'] = self.gs4.legacyID

    def _do_steady_state_checks(self):
        # Define _steadyStateToken in your mapping class to trigger
        # the steady state code. You can turn it off again by setting
        # noss: true in the config file, or by passing -m noss on the
        # commandline. (these cases are tested in the __init__()
        # method above, which attaches a steady state handler to self
        # if steady state processing is not explicitly turned off.)
        if hasattr(self, '_steadyStateToken'):
            log.debug("Checking steady state status for %s", self.gs4.legacyID)
            self._checkSteadyState(self.ssid, self._steadyStateToken)
        self._increment_transformedCount()

    def _increment_transformedCount(self):
        self.__class__._transformedCount += 1

    # def _checkPubID(self):
    #     # If we are dealing with a static data set, or one such as
    #     # vogue for which there is little point in checking the pub
    #     # id, make sure to set checkpubids: false in the config
    #     # file. This will disable the following code.
    #     if hasattr(self, 'pubIDHandler'):
    #         # This needs to be wrapped in a try: except: since it's
    #         # likely, during a full run, that the MySQL session will
    #         # drop.
    #         while True:
    #             try:
    #                 self.pubIDHandler.checkPubID(
    #                     self.gs4.journalID, self.productId)
    #             except MySQLdb.OperationalError:
    #                 self.pubIDHandler = PublicationIDs()
    #                 continue
    #             break

    # ++ HOOKS End ++

    def do_mapping(self):
        for field in self.record._fields():
            try:
                if self._dtable[field] is None:
                    self.notImplemented(field)
                    continue
            except KeyError:
                print "No key '%s' in dtable in %s" % (
                    field, self.__class__.__module__)
                sys.exit(1)
            if type(self._dtable[field]) is str:
                self.fixme(field, self._dtable[field])
                continue
            # The functions called from the dispatch table are
            # responsible for transforming the legacy formatted data
            # to something suitable to go into the GS format. They
            # should assign the transformed data to attributes on
            # self.gs4.
            data = getattr(self.record, field)
            self._dtable[field](self, data)

        # If this record is not in the list of desired records in
        # cfg['recordids'], raise SkipRecordException and continue.
        if 'recordids' in self._cfg.keys():
            if self.legacyDocumentID not in self._cfg['recordids']:
                self.visualFeedBack()
                log.info("skipping %s - not in list", self.legacyDocumentID)
                raise SkipRecordException

        # Since computedValues() can involve a lot of bit flipping,
        # defer it till we know we need it
        self.computedValues()

        self._increment_seen()

    def notImplemented(self, field):
        print >> sys.stderr, ("DEBUG notImplemented: %s" % field)

    def fixme(self, field, string=None):
        if 'verbose' in self._cfg:
            if self._cfg['verbose'] is True:
                print >> sys.stderr, ("DEBUG: %s - %s" % (field, string))

    # Fields that aren't required in GS4 should call noop.
    def noop(self, data): pass

    def computedValues(self):
        # We always want to run this, so that the correct global schema
        # version is inserted into self.gs4.global_schema_version. Because
        # of the way this is implemented, it can't be done elsewhere cleanly.
        self.gs4.global_schema_version = self.global_schema_version

        # Use this hook to calculate any computed values that are not
        # derived directly from the source data. Despite my preference
        # for explicit assignment at the point of method invocation,
        # it seems the better approach here is to use implicit
        # assignment - letting each of the called methods here handle
        # assigning values to attributes; this is simply because in
        # some instances, we need to set more than one attribute
        # within the body of a method. Therefore, any callbacks
        # registered in self._computedValues should handle assigning
        # values and attributes on self.gs4 and not return a value.

        for methodName in self._computedValues:
            if not isinstance(methodName, basestring):
                methodName(self)
            else:
                log.warn("DEPRECATION WARNING: _computedValues should be converted from a list of strings to a list of function references. Using strings requires a call to eval(), which should be avoided.")  # noqa
                eval('self.%s()' % methodName)

    # ## From here we are building the GS4 Record object contained in
    # ## the mapping instance.

    # Take the articleid from the source and attach it to self. Allows
    # us avoid running potentially expensive calls to computedValues()
    def setLegacyDocumentID(self, data):
        self.legacyDocumentID = data

    def title(self, data):
        if data == '':
            self.gs4.title = u'[untitled]'
        else:
            try:
                self.gs4.title = self.cleanAndEncode(data)
            except ValueError:
                log.error("Invalid character in title: %s (%s)",
                          data, self.documentID)
                raise SkipRecordException

    def language(self, data):
        languages = langUtils.languages(data, self._defaultDelimiter)
        self.gs4.languageData = langUtils.lang_iso_codes(languages)
        return languages

    def startpage(self, data):
        self.gs4.startpage = self.helper_startPage(data)
        return self.gs4.startpage

    def endpage(self, data):
        self.gs4.endpage = self.helper_endPage(data)
        return self.gs4.endpage

    def pagination(self, data):
        self.gs4.pagination = self.cleanAndEncode(data)
        return self.gs4.pagination

    def authors(self, data):
        self.gs4.contributors = self._contributors(data)

    def journalID(self, data):
        if data.startswith('ART'):
            data = data.replace('ART', 'AAA')
            print >> sys.stderr, "MANGLED AN ART title. Remove this code when possible"
        self.gs4.journalID = data

    def issn(self, data):
        self.gs4.issn = self.cleanAndEncode(data)

    def volume(self, data):
        self.gs4.volume = self.cleanAndEncode(data)

    def issue(self, data):
        self.gs4.issue = self.cleanAndEncode(data)

    def copyright(self, data):
        self.gs4.copyrightData = self.cleanAndEncode(data)

    def peerReviewed(self, data):
        self.gs4.peerReviewed = (u'true' if miscUtils.isTrue(data) else u'false')

    def rawPubDate(self, data):
        self.gs4.rawPubDate = self.cleanAndEncode(data)

    def pubTitle(self, data):
        self.gs4.pubTitle = self.cleanAndEncode(data)

    def publisher(self, data):
        pass  # This method should no longer be used.
        # self.gs4.publisher = textUtils.cleanAndEncode(data)
        # self.pubInfo()

    def publisherCountry(self, data):
        pass  # This method should no longer be used.
        # self.gs4.publisherCountry = textUtils.cleanAndEncode(data)
        # self.pubInfo()

    def documentFeatures(self, data):
        if data:
            if self._defaultDelimiter == '|':
                delimiter = '|'
            else:
                delimiter = ','
            self.gs4.docFeatures = [
                self.cleanAndEncode(feature.strip())
                for feature in data.strip().split(delimiter)
                if feature != '']

    def nonStandardCitation(self, data):
        self.gs4.nonStandardCitation = self.cleanAndEncode(data)

    # Anything that sets elements that live in /RECORD/PublicationInfo
    # should call this so the template renders it.
    def pubInfo(self):
        self.gs4.publicationInfo = True

    def prodInfo(self):
        self.gs4.productInfo = True

    def _setDates(self):
        try:
            self.gs4.normalisedAlphaNumericDate = dateUtils.normaliseDate(
                self.gs4.rawPubDate)
        except ValueError as e:
            log.error("Got a bad date value in %s. Value: %s Error: %s",
                      self._cfg['filename'], self.gs4.rawPubDate, e.message)
            self.msq.append_to_message(
                "Badly formatted date in file",
                "%s ('%s', Error: %s)" % (
                    self._cfg['basename'],
                    self.gs4.rawPubDate, e.message))
            raise SkipRecordException
        try:
            self.gs4.numericStartDate = dateUtils.pq_numeric_date(
                self.gs4.normalisedAlphaNumericDate)
        except UnhandledDateFormatException as e:
            log.error("Got unhandled date error in %s. Value: %s",
                      self._cfg['filename'], e.message)
            self.msq.append_to_message("Unhandled date string in file",
                                       "%s (%s)" % (self._cfg['basename'],
                                                    e.message))
            raise SkipRecordException
        if self.gs4.numericStartDate.startswith('FIXME'):
            log.error("Unhandled date format: %s, %s",
                      self.gs4.originalCHLegacyID, self.gs4.rawPubDate)
            raise SkipRecordException
        if self.gs4.numericStartDate == '00010101':
            self.gs4.undated = True

    def _lastUpdateTime(self):
        self.gs4.lastUpdateTime = unicode(dateUtils.fourteenDigitDate())

    # components

    def _components(self):
        self.gs4.components = []

        # These parts never change.
        values = {u'MimeType': u'text/xml', u'Resides': u'FAST'}

        # In PRISMA, we only ever see Representation inside Component.
        # Every record needs one of these:
        self.gs4.components.append(
            self._buildComponent(
                u'Citation', {
                    u'Representation': {
                        u'RepresentationType': u'Citation',
                        'values': values}}))

        if 'abstract' in self.gs4.fields():
            self.gs4.components.append(
                self._buildComponent(
                    u'Abstract',
                    {u'Representation': {u'RepresentationType': u'Abstract',
                                         'values': values}}))

    # Called from subclass's components() method.  compType is the
    # ComponentType attribute compData is a dictionary of all the
    # components that need to be included with each ComponentType. The
    # keys should be the names of the components that are
    # allowed. They are then used in yet another dispatch table to
    # construct the parts.
    def _buildComponent(self, compType, compData):
        component = {}
        component[u'ComponentType'] = unicode(compType)
        for comp, data in compData.items():
            component[comp] = self._componentTypes[comp](self, data)
        return component

    # Helper methods for attaching attributes to data elements. These
    # should be called from your subclasses, to ensure that the
    # correct attributes for the product are attached.  They return
    # values, rather than implicitly setting the values on the gs4
    # object. I think this makes it clearer what the code is doing
    # when looking at the subclass - explicit assignment is more
    # perspicuous than implicit assignment.  Note the signatures may
    # call for more than two arguments, depending on the type of data
    # we're dealing with.

    def _abstract(self, data, abstType, htmlcontent=None):
        abst = {'abstractText': self.cleanAndEncode(data),
                'abstractType': unicode(abstType)}
        if htmlcontent is not None:
            abst['HTMLContent'] = htmlcontent
        if htmlcontent == 'true':
            abst['abstractText'] = _sutils.unescape(abst['abstractText'])
        return abst

    # Takes either a string (and optional delimiter character) or a
    # list of author names.  If order is important, ensure the string
    # or list is ordered correctly before calling this method - items
    # will handled and emitted in the input order, but this method has
    # no internal ordering logic.
    def _contributors(self, data):
        if type(data) is str or type(data) is unicode:
            authors = [
                auth.strip() for auth
                in data.split(self._defaultDelimiter)
                if len(auth) > 0]
        else:
            authors = data
        contributors = []
        for index, contributor in enumerate(authors):
            if index == 0:
                contribrole = u'Author'
            else:
                contribrole = u'CoAuth'
            contributors.append(
                {u'ContributorRole': contribrole,
                 u'ContribOrder': unicode(index + 1),
                 'contribvalue': self.cleanAndEncode(contributor)})
        return contributors

    def _buildRepresentation(self, compData):
        # The object we pass in is in a reasonably good format for use
        # in the view template.
        return compData

    def _buildMultipleComponents(self, compData):
        return compData

    def _buildCHImagIDs(self, comp):
        return comp

    def _buildInlineImageCount(self, comp):
        return comp

    def _buildSimpleValue(self, comp):
        return comp

    # Add the product name as a prefix to the LegacyID. This is
    # required to ensure CH ids are unique within CStore, once we get
    # more products in.
    # BP3 prefix is "bp", not "bpc-", so we need a way to set the
    # prefix in the config file.

    def _prefix(self):
        if appconf.has_option(self.productId, 'legacyprefix'):
            return appconf.get(self.productId, 'legacyprefix')
        else:
            return "%s-" % self.productId

    def _prefixedLegacyId(self, idString):
        return "%s%s" % (self._prefix(), idString)

    def objectBundleData(self, val):
        self.gs4.objectBundleData = []
        self.gs4.objectBundleData.append(
                {u'ObjectBundleType': u'CHProductCode',
                 u'ObjectBundleValue': unicode(val)})

    # A nicer API for building the Term elements.  Each Term type
    # should specify what its child element should be called, and the
    # names of any attributes it is expected to support.  The caller
    # must pass in the type of Term it wants (Term, FlexTerm, etc),
    # the value to insert in the Term's child element, and the values
    # for any attributes it should have. If a single attribute is
    # supported, termattr should be a string, representing the
    # attribute's value. If multiple attributes are supported, pass a
    # list of strings. These need to be in the correct order so that
    # they are inserted into the XML correctly - the attribute names
    # are sorted alphabetically, and so their corresponging values
    # need to take that into account. If you want to include some but
    # not all attributes, set their values to None to prevent them
    # from being included in the final XML.
    def _build_term(self, termtype=None, termvalue=None, termattr=None):
        if termattr is None:
            attrs = {}
        elif type(termattr) is list:
            attrs = {}
            attr_names = sorted(self.__term_types[termtype].attrname.split())
            for attr_name, attr_value in zip(attr_names, termattr):
                if attr_value is None:
                    continue
                attrs[attr_name] = attr_value
        else:
            attrs = {self.__term_types[termtype].attrname.split()[0]: termattr}
        return {
            'TermType': termtype,
            'values': {self.__term_types[termtype].childelem: termvalue},
            'attrs': attrs
        }

    # ++ Helper methods that don't really need to be extracted out for
    # general use.

    def helper_startPage(self, paginationString):
        if paginationString == '':
            return u''
        if self.productId == 'vogue':
            return unicode(
                re.search(
                    '[A-Za-z0-9-]{1,}',
                    paginationString).group(0))
        else:
            try:
                return unicode(re.search(
                    '[A-Za-z0-9]{1,}', paginationString).group(0))
            except AttributeError:
                # If there is no match against the regexp, return the empty
                # string instead of choking...
                log.info(
                    "%s: Unexpected character in page display: %s",
                    self._cfg['basename'], paginationString)
                return u''

    def helper_endPage(self, paginationString):
        if paginationString == '':
            return u''
        return unicode(
            re.search(
                r'([A-Za-z0-9]{1,})[? .,+_-]*$',
                paginationString).group(1) if paginationString else u'')

    def stringToList(self, data, delimiter=None):
        # Useful for splitting strings of Terms etc into a list so
        # they can correctly be marked up. The default delimiter should
        # be set in each subclass of AbstractMapping that is going to
        # make use of this method. You can pass in an alternative
        # delimiter if the default is not appropriate. If you really
        # need a delimiter of None, pass in the string $$NONE$$, which
        # was chosen because of the sheer unlikelihood that it'll exist
        # in any data set!
        if delimiter is None:
            delimiter = self._defaultDelimiter
        if delimiter == '$$NONE$$':
            delimiter = None
        return [item.strip() for item in data.split(delimiter)
                if not item.strip() == '']

    # ## Set the object's product code, for use in the Resides elements
    # ## in Components. function is a string naming a function to apply
    # ## to the value retrieved from the self._cfg['product'] setting.
    # ## For Vogue, it is "capitalize" (to turn 'vogue' into 'Vogue')
    # ## and for EIMA it is "upper" (to turn 'eima' into 'EIMA'). This
    # ## method is not meant to be called directly, but instead is
    # ## called by the mapping's productCode property.
    def get_product_code(self, f):
        while True:
            try:
                return self._productCode
            except AttributeError:
                self._productCode = f(self._cfg['product'])

    # wrap calls to textUtils.cleanAndEncode() in order to correctly catch
    # EntRefError and other exceptions in a standard, unified manner.
    def cleanAndEncode(self, text, **kwargs):
        # text = strip_control_chars(text)
        # text = remove_unwanted_chars(text)
        try:
            return textUtils.cleanAndEncode(text, **kwargs)
        except EntRefError as e:
            log.error(
                "Entity encoding error: (%s), data: %s, in %s", e,
                text, self._srcFile)
            raise SkipRecordException

    @staticmethod
    def isStringy(data):
        return textUtils.isStringy(data)

    def visualFeedBack(self):
        if self._cfg['provideFeedBack'] is True:
            sys.stderr.write('\r\033[0K')  # pylint:disable=W1401
            sys.stderr.write(
                'Seen: \033[92m%s\033[0m  transformed: \033[91m%s\033[0m  (\033[96m%s\033[0m)' % (
                    self._cfg['index'],
                    self._transformedCount,
                    # pylint:disable=W1401,C0301
                    self.visual_feedback_printid()))

    # Check to see if the current article comes from a blocked title
    # Each product that needs to selectively block titles/issues
    # has a directory etc/blocklists/<product>, which contains one
    # file for each blocked title. If the file is empty or contains
    # ALL or * as its only non-comment line, all issues in that
    # journal will cause the app to raise SkipRecordException. If
    # the file contains individual issue IDs, one per line, only
    # those will be omitted from the output.
    def is_blocked(self):
        try:
            blocklist_for_journal = self.blocklist[self.gs4.journalID]
        except KeyError:
            # If there is no blocklist file for this journal, return None
            # to signify that the article is allowed.
            return
        if self.gs4.journalID in self.blocklist.keys():
            if self.blocklist[self.gs4.journalID] == ['ALL']:
                log.warn(
                    "all issues in %s are blocked. Omitting %s from output",
                    self.gs4.journalID, self.gs4.originalCHLegacyID)
                raise SkipRecordException
            elif self.gs4.legacyParentID in blocklist_for_journal:
                log.warn(
                    "%s in explicitly blocked issue %s. Skipping record",
                    self.gs4.originalCHLegacyID, self.gs4.legacyParentID)
                raise SkipRecordException
