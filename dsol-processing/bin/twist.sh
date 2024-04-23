#!/bin/sh

if [ `basename $0` = 'twist.sh' ]
then
    echo "This is a wrapper script used by various utilities to overcome a bug"
    echo "in the Python 2.7 build under Solaris that prevents it from correctly"
    echo "loading certain key modules used in the transformation application suite."
    echo 
    echo "It is not intended to be called directly; instead, a hardlink with the"
    echo "name of a wrapped script is created, with the wrapped script's real name"
    echo "being prefixed with _"

    exit 1
fi

# Hack to enable python2.7 to correctly load lxml.etree
# et al. on Solaris
if [ `uname -s` != 'FreeBSD' ]
then
        LD_LIBRARY_PATH=/usr/local/lib
        export LD_LIBRARY_PATH
fi

twist() {
    wrapped=_`echo $0 | awk -F/ '{print $NF}'`
    wrapped=`dirname $0`/$wrapped
    echo $wrapped
}

exec `twist` "$@"
