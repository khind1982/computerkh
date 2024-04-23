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
__CHEETAH_genTime__ = 1226314423.9681759
__CHEETAH_genTimestamp__ = 'Mon Nov 10 10:53:43 2008'
__CHEETAH_src__ = 'ris_poem_comcitn.tmpl'
__CHEETAH_srcLastModified__ = 'Mon Nov 10 10:52:40 2008'
__CHEETAH_docstring__ = 'Autogenerated by CHEETAH: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class ris_poem_comcitn(Template):

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
        
        write('''<comcitn>''')
        write('''<TY>CHAP</TY>''')
        write('''<AU>''')
        _v = VFN(VFFSL(SL,"author_attribution_set",True)[0],"namefromdata",True) # '$author_attribution_set[0].namefromdata' on line 3, col 5
        if _v is not None: write(_filter(_v, rawExpr='$author_attribution_set[0].namefromdata')) # from line 3, col 5.
        write('''</AU>''')
        write('''<TI>''')
        _v = VFFSL(SL,"title",True) # '$title' on line 4, col 5
        if _v is not None: write(_filter(_v, rawExpr='$title')) # from line 4, col 5.
        write('''</TI>''')
        if len(VFFSL(SL,"author_attribution_set",True)) > 1: # generated from line 5, col 1
            for author in VFFSL(SL,"author_attribution_set",True)[1:]: # generated from line 6, col 1
                write('''<A2>''')
                _v = VFFSL(SL,"author.namefromdata",True) # '$author.namefromdata' on line 7, col 5
                if _v is not None: write(_filter(_v, rawExpr='$author.namefromdata')) # from line 7, col 5.
                write('''</A2>''')
        write('''<T2>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"title",True) # '$volume_set[0].title' on line 10, col 5
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].title')) # from line 10, col 5.
        write('''</T2>''')
        write('''<CY>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"city",True) # '$volume_set[0].city' on line 11, col 5
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].city')) # from line 11, col 5.
        write('''</CY>''')
        write('''<PBL>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"publisher",True) # '$volume_set[0].publisher' on line 12, col 6
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].publisher')) # from line 12, col 6.
        write('''</PBL>''')
        write('''<Y2>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"filepubdate",True) # '$volume_set[0].filepubdate' on line 13, col 5
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].filepubdate')) # from line 13, col 5.
        write('''</Y2>''')
        write('''<Y1>''')
        _v = VFN(VFN(VFN(VFFSL(SL,"volume_set",True)[0],"pubdate",True),"replace",False)('[', ''),"replace",False)(']', '') # "$volume_set[0].pubdate.replace('[', '').replace(']', '')" on line 14, col 5
        if _v is not None: write(_filter(_v, rawExpr="$volume_set[0].pubdate.replace('[', '').replace(']', '')")) # from line 14, col 5.
        write('''</Y1>''')
        write('''<SP>''')
        _v = VFFSL(SL,"startpage",True) # '$startpage' on line 15, col 5
        if _v is not None: write(_filter(_v, rawExpr='$startpage')) # from line 15, col 5.
        write('''</SP>''')
        write('''<SN>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"ISBN",True) # '$volume_set[0].ISBN' on line 16, col 5
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].ISBN')) # from line 16, col 5.
        write('''</SN>''')
        write('''<T3>Literature Online</T3>''')
        write('''<UR>''')
        _v = VFFSL(SL,"idref",True) # '$idref' on line 18, col 5
        if _v is not None: write(_filter(_v, rawExpr='$idref')) # from line 18, col 5.
        write('''</UR>''')
        write('''<N1a>''')
        _v = VFN(VFN(VFFSL(SL,"volume_set",True)[0],"excludere",True),"sub",False)('', VFN(VFFSL(SL,"volume_set",True)[0],"notes",True)) # "$volume_set[0].excludere.sub('', $volume_set[0].notes)" on line 19, col 6
        if _v is not None: write(_filter(_v, rawExpr="$volume_set[0].excludere.sub('', $volume_set[0].notes)")) # from line 19, col 6.
        write('''</N1a>''')
        write('''<N1b>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"filecity",True) # '$volume_set[0].filecity' on line 20, col 6
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].filecity')) # from line 20, col 6.
        write(''', ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"filepublisher",True) # '$volume_set[0].filepublisher' on line 20, col 31
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].filepublisher')) # from line 20, col 31.
        write(''', ''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"filepubdate",True) # '$volume_set[0].filepubdate' on line 20, col 61
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].filepubdate')) # from line 20, col 61.
        write('''</N1b>''')
        write('''<N1c>''')
        _v = VFN(VFFSL(SL,"volume_set",True)[0],"copyright",True) # '$volume_set[0].copyright' on line 21, col 6
        if _v is not None: write(_filter(_v, rawExpr='$volume_set[0].copyright')) # from line 21, col 6.
        write('''</N1c>''')
        write('''</comcitn>''')
        
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

    _mainCheetahMethod_for_ris_poem_comcitn= 'respond'

## END CLASS DEFINITION

if not hasattr(ris_poem_comcitn, '_initCheetahAttributes'):
    templateAPIClass = getattr(ris_poem_comcitn, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(ris_poem_comcitn)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=ris_poem_comcitn()).run()

