#!/usr/local/bin/python2.7

import sys
import os
sys.path.append('/packages/dsol/lib/python2.7/site-packages')
sys.path.append(os.path.join(os.path.dirname(__file__), '../lib/python'))

from innodata_cache_reader import innodata_cache_reader
from bs4 import BeautifulSoup

    
def testcache(cachepath, errorlog):

    tester = InnodataCacheTester(cachepath)
    tester.seterrorfile(errorlog)
    tester.applytests()

class InnodataCacheTester:

    def __init__(self, cachepath):
        self._cachepath = cachepath
        self._reader = innodata_cache_reader(self._cachepath)
        self._alltests = [
                        'test_missing_objects',
                        'test_missing_components',
                        'test_inline_image_count',
                        'test_image_order',
                        'test_duplicate_components'
                        ]
        self._teststorun = self._alltests
        self._errors = []
        self._errorfile = 'innodatacachetest.log'

    def seterrorfile(self, errorlogpath):
        self._errorfile = errorlogpath
    
    def applytests(self):
        with open(self._errorfile, 'w') as log:
            for recpath, recdata in self._reader:
                print recpath
                self.currentrecpath = recpath
                self.fulltextdict = recdata[1]
                self.components = recdata[0]
                self._get_ft_media_ids()
                self._get_image_components()
                self.testonerecord()
                self.writeerrors(log)
                
    def writeerrors(self, filehandle):
        filehandle.write(''.join(['%s\n' % e for e in self._errors]))
        self._errors = []
            
    def testonerecord(self):
        for test in self._teststorun:
            getattr(self, test)()
    
    
    def _get_ft_media_ids(self):
        """Given the full text object for an Innodata record, create a
        list of the mediaids for the images it contains, in sequence.
        
        """
        
        ftstring = self.fulltextdict['fullText']['value']
        ftparsed = BeautifulSoup(ftstring)
        #print ftparsed
        images = ftparsed.find_all('object')
        self.ftmediaids = []
        for image in images:
            #print image
            mediaidparam = image.find(attrs={'name': 'mstar_lm_media_id'})
            mediaid = mediaidparam['value']
            self.ftmediaids.append(mediaid)
            
    def _get_image_components(self):
        self._imagecomponents = [c for c in self.components
                                    if c[u'ComponentType'] == u'InlineImage'
                                    ]
     
    def _register_error(self, msg):
        self._errors.append(u'%s: %s' % (self.currentrecpath, msg))

    def test_missing_objects(self):
    
        for component in self._imagecomponents:
            if component[u'mstar_lm_media_id'] not in self.ftmediaids:
                self._register_error(u'Component with mstar_lm_media_id %s' \
                                    u' has no matching object.'
                                            % component[u'mstar_lm_media_id'])
                
    
    def test_missing_components(self):

        for mediaid in self.ftmediaids:
            mediaidmatched = False
            for component in self._imagecomponents:
                if component[u'mstar_lm_media_id'] == mediaid:
                    mediaidmatched = True
            if not mediaidmatched:
                self._register_error(u'Object with mstar_lm_media_id %s' \
                                    u' has no matching component.'
                                                            % mediaid)
            
    def test_inline_image_count(self):
    
        correctcount = unicode(len(self._imagecomponents))
        for component in self._imagecomponents:
            if component[u'InlineImageCount'] != correctcount:
                self._register_error(u'Incorrect InlineImageCount (%s) - ' \
                            u'there are %s InlineImage components.'
                            % (component[u'InlineImageCount'], correctcount))
                            
    def test_image_order(self):
        
        ordermap = {}
        for order, mediaid in enumerate(self.ftmediaids):
            if mediaid not in ordermap:
                ordermap[mediaid] = unicode(order+1)
        for component in self._imagecomponents:
            #print ordermap
            try:
                if component[u'Order'] != \
                                ordermap[component[u'mstar_lm_media_id']]:
                    self._register_error(u'Incorrect Order value (%s) on ' \
                            'component with mstar_lm_media_id %s; ' \
                            'Order should be %s.'
                                % ( component[u'Order'],
                                    component[u'mstar_lm_media_id'],
                                    ordermap[component[u'mstar_lm_media_id']]
                                    ))
            except KeyError:
                self._register_error(u'Cannot test Order - mismatch ' \
                                        'between components and objects.')
                                            
    def test_duplicate_components(self):
     
        componentimagepaths = {}
        for component in self._imagecomponents:
            imagepath = component[u'InnoImgReprs'][u'values'][u'MediaKey']
            if imagepath not in componentimagepaths:
                componentimagepaths[imagepath] = ''
            else:
                self._register_error(u'Image %s occurs more than once in ' \
                                        'components.' % imagepath)
    


if __name__ == '__main__':

    testcache(sys.argv[1], sys.argv[2])