# -*- mode: python -*-
# pylint: disable = invalid-name

'''Functions for communicating with the HMS/EOS storage system.

'''

import datetime
import json
import logging
import logging.handlers
import os
import mimetypes
import time
import sys

try:
    import requests
except ImportError:
    sys.path.append('/packages/dsol/opt/lib/python2.7/site-packages')
    import requests


import commonUtils.fileUtils

SESSION = requests   #.Session()

# Let's have some logging, shall we?

rootLogger = logging.getLogger('')
rootLogger.setLevel(logging.INFO)
socketHandler = logging.handlers.SocketHandler(
    'localhost',
    logging.handlers.DEFAULT_TCP_LOGGING_PORT)

rootLogger.addHandler(socketHandler)

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)

# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# console.setFormatter(formatter)

# logging.getLogger('').addHandler(console)

logger = logging.getLogger('hmslib')


# These are the three canonical hostnames to use for communicating with HMS.
HMSInstances = {
    'dev': 'http://hms-store.dev.proquest.com',
    'pre': 'https://hms-store.pre.proquest.com',
    'prod': 'https://hms-store.prod.proquest.com'
}


class StorageRecipe(object):
    '''Base class for storage recipes.'''
    def __init__(self, uniqueId, clientId, instance='dev'):
        self.uniqueId = uniqueId
        self.clientId = clientId
        self.instance = instance
        self._hmsclient = HMSClient

    def set_client(self, client):
        setattr(self, '_hmsclient', client)

    @property
    def body(self):
        'The body of the request to be sent to the service.'
        return None

    def __raise__(self, prop_name):
        raise NotImplementedError('Derived classes must implement the "%s" property' % prop_name)

    @property
    def recipe_name(self):
        'The recipe name. This is used as the first part of the request URI, after the hostname.'
        self.__raise__('recipe_name')

    @property
    def params(self):
        '''A dict of parameters to be sent with the request. The requests module handles
        assembling them correctly.'''
        # pylint: disable = no-member
        return {'uniqueId': self.uniqueId, 'clientId': self.clientId}

    @property
    def http_method(self):
        '''The name of the HTTP method for the recipe. This base implementation just
        raises a NotImplementedError'''
        self.__raise__('http_method')

    def run(self):
        '''Runs the recipe. It simply hooks into the run_recipe method on HMSClient,
        passing the current recipe instance in as its sole argument.'''
        return self._hmsclient(env=self.instance).run_recipe(self)
        #return HMSClient(env='dev').run_recipe(self)

class Lookup(StorageRecipe):
    'Lookup recipe to look up a key in HMS.'
    def __init__(self, uniqueId, clientId=None, instance='dev'):
        super(self.__class__, self).__init__(uniqueId, clientId, instance)

    @property
    def http_method(self):
        return 'get'

    @property
    def recipe_name(self):
        return 'Lookup'

class Status(StorageRecipe):
    'Represents the Status workflow.'
    def __init__(self, uniqueId, clientId=None, instance='dev'):
        super(self.__class__, self).__init__(uniqueId, clientId, instance)

    @property
    def http_method(self):
        return 'get'

    @property
    def recipe_name(self):
        return 'Status'

## '/SimplePDF?clientId=CH&uniqueId=%(docid)s
## &size=%(pdfsize)s
## &md5=%(pdfmd5)s
## &objectLoc=%(pdf_uri)s
## &action=%(action)s
## &validateObject=No
## &storeObject=Yes
## &textExtract=No
## &linearizeObject=No
## &retrieveRecipe=SimplePDF
## &async=Yes'

class StoreSimpleObject(StorageRecipe):
    def __init__(self, uniqueId, clientId=None, instance='dev', file_name=None, **kwargs):
        '''
        '''
        self.args = {}
        super(self.__class__, self).__init__(uniqueId, clientId, instance)
        self.file_name = file_name
        self.file_basename = os.path.basename(self.file_name)
        self._params = {
            'uniqueId': self.uniqueId,
            'clientId': self.clientId,
            'action' : 'Upsert',
        }
        for key, value in kwargs.items():
            self.args[key] = value
        if self.async:
            self._params['async'] = 'Yes'

    @property
    def recipe_name(self):
        return 'SimpleObject'

    @property
    def async(self):
        # FIXME Once we implement synchronous posts, this will need to be changed.
        return True

    @property
    def params(self):
        return self._params

    @property
    def action(self):
        return self.params['action']

    @property
    def headers(self):
        return {}

    @property
    def http_method(self):
        return 'post'

    @property
    def objectLoc(self):
        return self.args['objectLoc']

    @property
    def body(self):
        '''The body of the request, converted to JSON.
        '''
        _body = {
            'clientId': 'CH',
            'action': 'Upsert',
            'retrieveRecipe': 'SimpleObject',
            'timeout': '300',
            'objects': [
                {
                    'type': 'object',
                    'size': self.size,
                    'md5': self.md5,
                    'location': self.objectLoc,
                    'options': [
                        {'key': 'specifiedFileName',
                         'value': self.file_basename},
                        {'key': 'mimeType', 'value': self.mimetype}
                    ]}]}

        # Only certain types of objects should be stored with the storeCF flag.
        if self.mimetype in ['audio/mpeg']:
            _body['objects'][0]['options'].append({'key': 'storeCF', 'value': 'Yes'})

        return json.dumps(_body)

    @property
    def size(self):
        return commonUtils.fileUtils.get_file_size(self.file_name)

    @property
    def md5(self):
        return commonUtils.fileUtils.get_file_checksum(self.file_name)

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.file_basename)[0]

class StoreSimplePDF(StorageRecipe):
    '''Class representing objects to be stored using the SimplePDF recipe.
    It expects to receive a uniqueId, clientId, and file_name at a minimum.
    Default parameters are overridden by passing appropriate kwargs.'''

    def __init__(self, uniqueId, clientId=None, instance='dev', file_name=None, **kwargs):
        super(self.__class__, self).__init__(uniqueId, clientId, instance)
        self._params = {
            'uniqueId': self.uniqueId,
            'clientId': self.clientId,
            'action': 'Upsert',
            'linearizeObject': 'No',
            'retrieveRecipe': 'SimplePDF',
            'storeObject': 'Yes',
            'textExtract': 'No',
            'validateObject': 'No',
        }
        self.file_name = file_name
        self._params['size'] = commonUtils.fileUtils.get_file_size(self.file_name)
        self._params['md5'] = commonUtils.fileUtils.get_file_checksum(self.file_name)
        for key, value in kwargs.items():
            self._params[key] = value

        if self.async:
            self._params['async'] = 'Yes'

        #print "PARAMS: %s" % self._params

    @property
    def headers(self):
        '''If this is a synchronous request, set Content-Type header to `application/pdf'.
        Otherwise, return an empty dict.'''
        if self.async:
            return {}
        return {'Content-Type': 'application/pdf'}

    @property
    def async(self):
        '''Checks for the existence of `objectLoc' in self.params. If it is
        found, the current instance is intended for submission of an asynchronous
        load request.'''
        return 'objectLoc' in self.params.keys()

    @property
    def http_method(self):
        return 'post'

    @property
    def recipe_name(self):
        return 'SimplePDF'

    @property
    def params(self):
        return self._params

    @property
    def action(self):
        '''Action is a flag that indicates to the HMS service whether we want to
        Insert or Update an object. By default, we use Upsert which updates an object if
        it already exists, or creates it otherwise. The user may specify it in their
        parameters when creating a new instance.'''
        return self.params['action']

    @property
    def body(self):
        '''A synchronous request must include the file data when the request is made.
        In this recipe, the body is the file to be uploaded. We defer opening it so
        that the HMSClient instance that receives it can decide whether to stream
        it to the service or load it from memory.

        '''
        if self.async:
            return None
        return self.file_name

def get_client():
    return HMSClient

# Map handled mimetypes to the storage recipe class that implements the recipe.
mimetype_mapping = {
    'text/xml': StoreSimpleObject,
    'application/pdf': StoreSimplePDF,
    'audio/mpeg': StoreSimpleObject,
    'image/jpeg': StoreSimpleObject,
}

def get_class(filepath):
    m_type = mimetypes.guess_type(filepath)[0]
    try:
        return mimetype_mapping[m_type]
    except KeyError:
        raise NotImplementedError(
            "No handler exists for files of type '%s'" % m_type)

def lookup(uniqueId):
    lookup_data = Lookup(uniqueId, clientId='CH').run()
    # Check the status code of the returned value. If it's 500 on a Lookup,
    # it *might* mean that an asynchronous load of an object is in process. If
    # that's the case, issuing a Status request will get the metadata we want,
    # and allow HMS to clear the Status document...
    if lookup_data.status_code == 500:
        lookup_data = Status(uniqueId, clientId='CH').run()
    # Just return the JSON representation of the response body. If the Lookup
    # didn't find any matches, it sends back an empty result document. No 404
    # for you!
    return lookup_data.json()

def load(filepath, productCode=None, location=None, action='Insert', check=False):
    '''Load the object at `filepath'. If `location' is given, it must either be
    a string representing the URL that HMS can use to retrieve the object, or a
    callable that takes the `filepath' and returns a suitable URL. For example,
    calling str.replace() on a portion of `filepath'
    '''
    if any(o is None for o in [productCode, location]):
        raise RuntimeError("Must provide a productCode and location")

    # Try treating the value passed in as `location' as a callable. If that
    # raises a TypeError, just take it as a string.
    try:
        url = location(filepath)
    except TypeError:
        url = location
    cls = get_class(filepath)
    uniqueId = "%s-%s" % (productCode, os.path.basename(filepath))

    # If the client set `check' to True, we can short-circuit the loading if we
    # get back a match for the uniqueId.
    if check:
        resp = lookup(uniqueId)
        if resp:
            return resp

    # We can't simply return the value we get back from this request, because in
    # the case of an asynchronous request, we will only get back an empty 204.
    resp = cls(uniqueId, clientId='CH', file_name=filepath, objectLoc=url).run()
    if resp.status_code == 204:
        while True:
            time.sleep(2)
            status_resp = status(uniqueId)
            if status_resp.status_code == 404:
                # We get here if the object we wanted to load asynchronously has
                # already finished loading before we get as far as sending the
                # Status request. In such cases, HMS helpfully clears the Status
                # data, but doesn't do anything helpful like redirecting us to
                # the Lookup instead. Oh no. You have to do that yourself.
                status_resp = lookup(uniqueId)
                if status_resp.json():
                    return status_resp.json()

            try:
                if status_resp.json():
                    return status_resp.json()
            except:
                continue

class HMSClient(object):
    '''A class implementing an abstraction around the HMS API. HMS for humans, if
    you will.

    '''
    def __init__(self, env):
        self.environment = env
        self.host = HMSInstances[env]

    def _run_recipe(self, recipe):
        '''Runs the passed in recipe, which must must contain the necessary parts
        for it to succeed. This is a delegate method that inspects the recipe for its
        method parameter, and uses that to locate the correct method here.'''

        return self._run_recipe([recipe])

    def run_recipe(self, recipe):
        start = time.time()
        logger.debug("%s: Starting API call (%s, %s)", os.getpid(),
                     recipe.recipe_name, recipe.http_method)
        result = getattr(self, recipe.http_method)(recipe)
        end = time.time()
        dur = str(datetime.timedelta(seconds=int(end - start)))
        logger.debug("%s: API call finished (%s)", os.getpid(), dur)
        return result

    def get(self, recipe):
        '''Send a GET to self.host, with body, headers and params taken from the
        passed in recipe object.'''
        return SESSION.get('%s/%s' % (self.host, recipe.recipe_name),
                           params=recipe.params)

    def post(self, recipe):
        '''If recipe's async param is True, we need to check that the string in
        recipe.body is the name of a valid file. If it is, we then need to check
        the file's size, to determine if we want to stream it or send inline.

        '''

        if recipe.async:
            return self.async_post(recipe)
        else:
            return self.sync_post(recipe)

    def async_post(self, recipe):
        '''Make an asynchronous requet to store an object.
        '''

        return SESSION.post('%s/%s' % (self.host, recipe.recipe_name),
                            headers=recipe.headers, params=recipe.params,
                            data=recipe.body)

    def sync_post(self, recipe):
        '''Need to get clarification from the HMS devs on how to encode objects
        for inline loading as the request body. No guidance in the API docs.
        '''

        raise NotImplementedError
