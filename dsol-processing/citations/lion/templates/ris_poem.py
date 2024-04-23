#!/usr/bin/env python




##################################################
## DEPENDENCIES
import sys
import os
import os.path
from os.path import getmtime, exists
import time
import types
import __builtin__
from Cheetah.Version import MinCompatibleVersion as RequiredCheetahVersion
from Cheetah.Version import MinCompatibleVersionTuple as RequiredCheetahVersionTuple
from Cheetah.Template import Template
from Cheetah.DummyTransaction import DummyTransaction
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList, valueFromFrameOrSearchList
from Cheetah.CacheRegion import CacheRegion
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers

##################################################
## MODULE CONSTANTS
try:
    True, False
except NameError:
    True, False = (1==1), (1==0)
VFFSL=valueFromFrameOrSearchList
VFSL=valueFromSearchList
VFN=valueForName
currentTime=time.time
__CHEETAH_version__ = '2.0rc8'
__CHEETAH_versionTuple__ = (2, 0, 0, 'candidate', 8)
__CHEETAH_genTime__ = 1226314423.785284
__CHEETAH_genTimestamp__ = 'Mon Nov 10 10:53:43 2008'
__CHEETAH_src__ = 'ris_poem.tmpl'
__CHEETAH_srcLastModified__ = 'Mon Sep 24 16:38:49 2007'
__CHEETAH_docstring__ = 'Autogenerated by CHEETAH: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class ris_poem(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        Template.__init__(self, *args, **KWs)
        if not self._CHEETAH__instanceInitialized:
            cheetahKWArgs = {}
            allowedKWs = 'searchList namespaces filter filtersLib errorCatcher'.split()
            for k,v in KWs.items():
                if k in allowedKWs: cheetahKWArgs[k] = v
            self._initCheetahInstance(**cheetahKWArgs)
        

    def respond(self, trans=None):



        ## CHEETAH: main method generated for this template
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        write('''TY  - CHAP\r
AU  - ''')
        _v = VFN(VFFSL(SL,"author_attribution_set",True)[0],"namefromdata",True) # '$author_attribution_set[0].namefromdata' on line 2, col 7
        if _v is not None: write(_filter(_v, rawExpr='$author_attribution_set[0].namefromdata')) # from line 2, col 7.
        write('''\r
TI  - ''')
        _v = VFFSL(SL,"title",True) # '$title' on line 3, col 7
        if _v is not None: write(_filter(_v, rawExpr='$title')) # from line 3, col 7.
        write('''\r
''')
        if len(VFFSL(SL,"author_attribution_set",True)) > 1: # generated from line 4, col 1
            for author in VFFSL(SL,"author_attribution_set",True)[1:]: # generated from line 5, col 1
                write('''A2  - ''')
                _v = VFFSL(SL,"author",True) # '$author' on line 6, col 7
                if _v is not None: write(_filter(_v, rawExpr='$author')) # from line 6, col 7.
                write('''.''')
                _v = VFFSL(SL,"namefromdata",True) # '$namefromdata' on line 6, col 15
                if _v is not None: write(_filter(_v, rawExpr='$namefromdata')) # from line 6, col 15.
                write(''' (''')
                _v = VFFSL(SL,"author.role",True) # '$author.role' on line 6, col 30
                if _v is not None: write(_filter(_v, rawExpr='$author.role')) # from line 6, col 30.
                write(''')\r
''')
        write('''T2  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"title",True) # '$volume_set[0].title' on line 9, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].title')) # from line 9, col 7.
        write('''\r
CY  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"city",True) # '$volume_set[0].city' on line 10, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].city')) # from line 10, col 7.
        write('''\r
PB  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"publisher",True) # '$volume_set[0].publisher' on line 11, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].publisher')) # from line 11, col 7.
        write('''\r
Y2  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"filepubdate",True) # '$volume_set[0].filepubdate' on line 12, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].filepubdate')) # from line 12, col 7.
        write('''\r
Y1  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"pubdate",True) # '$volume_set[0].pubdate' on line 13, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].pubdate')) # from line 13, col 7.
        write('''\r
SP  - ''')
        _v = VFFSL(SL,"startpage",True) # '$startpage' on line 14, col 7
        if _v is not None: write(_filter(_v, rawExpr='$startpage')) # from line 14, col 7.
        write('''\r
SN  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"ISBN",True) # '$volume_set[0].ISBN' on line 15, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].ISBN')) # from line 15, col 7.
        write('''\r
T3  - Literature Online\r
UR  - http://gateway.proquest.com/openurl?ctx_ver=Z39.88-2003&xri:pqil:res_ver=0.2&res_id=xri:lion&rft_id=xri:lion:po:''')
        _v = VFFSL(SL,"idref",True) # '$idref' on line 17, col 119
        if _v is not None: write(_filter(_v, rawExpr='$idref')) # from line 17, col 119.
        write('''\r
N1  - ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"notes",True) # '$volume_set[0].notes' on line 18, col 7
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].notes')) # from line 18, col 7.
        write('''\r
N1  - 2000, Chadwyck-Healey (a Bell & Howell Information and Learning company)\r
N1  - Copyright (c) 2007 ProQuest-CSA LLC. All Rights Reserved. Do not export or print from this database without checking the Copyright Conditions to see what is permitted.\r
ER  - ''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        
    ##################################################
    ## CHEETAH GENERATED ATTRIBUTES


    _CHEETAH__instanceInitialized = False

    _CHEETAH_version = __CHEETAH_version__

    _CHEETAH_versionTuple = __CHEETAH_versionTuple__

    _CHEETAH_genTime = __CHEETAH_genTime__

    _CHEETAH_genTimestamp = __CHEETAH_genTimestamp__

    _CHEETAH_src = __CHEETAH_src__

    _CHEETAH_srcLastModified = __CHEETAH_srcLastModified__

    _mainCheetahMethod_for_ris_poem= 'respond'

## END CLASS DEFINITION

if not hasattr(ris_poem, '_initCheetahAttributes'):
    templateAPIClass = getattr(ris_poem, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(ris_poem)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=ris_poem()).run()

