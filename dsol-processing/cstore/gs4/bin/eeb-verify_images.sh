#!/bin/bash

# Script to verify that images are present on image servers

usage () {
    echo "Usage: `basename $0` [pqid list] [collection]" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

pqidlist=$1
coll=$2

if [ -z "$pqidlist" ]
then
    die "Please specify a file containing a list of pqids"
fi

if [ -z "$coll" ]
then
    die "Please specify collection in the form Collection1"
fi

while IFS='' read -r pqid || [[ -n "$pqid" ]]; do
    pqidpath=${pqid//-/\/}
    if [ -d "/images/eeb-jpeg-${coll}/${pqidpath}" ]
    then
        jnum=`find /images/eeb-jpeg-${coll}/${pqidpath} -name '*.jpg' | wc -l` 
        znum=`find /images/eeb-zoomify-${coll}/${pqidpath} -name '*.jpg' | wc -l`
        if [ $jnum = '0' ] || [ $znum = '0' ]
        then
            echo ${pqid}: ${jnum} jpegs, ${znum} tiles
        fi
    else
        echo ${pqid}: Directory not found: /images/eeb-jpeg-${coll}/${pqidpath} 
    fi
done < "$pqidlist"

