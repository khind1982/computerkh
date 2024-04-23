#!/bin/bash

usage () {
    echo "Usage: `basename $0` {batch directory}" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

trgdir=${1}

if [ -z "$trgdir" ]
then
    die "Please specify a target directory at batch level, e.g., /dc/paris-coll6/Incoming/20171221"
fi

cd ${trgdir}

shopt -s nullglob dotglob     # To include hidden files
files=(${trgdir}/*.tar.gz)
if [ ! ${#files[@]} -gt 0 ]
then 
    die "No packages detected in target directory. Please specify a batch level directory, e.g., /dc/paris-coll6/Incoming/20171221"
fi

batch=${PWD##*/}
mkdir -p ../../Tarchive/${batch}
mkdir /dc/eurobo/incoming/${batch}

for tarfile in `find . -name '*.tar.gz'`
do
echo $tarfile
outdir=${tarfile//\.tar\.gz/\/}
mkdir $outdir
gtar -zxvf ${tarfile} -C $outdir
chmod 775 ${outdir}*
chmod 775 ${outdir}*/ocr
find ${outdir} -type f -exec chmod 775 {} +
mv ${tarfile} ../../Tarchive/${batch}/
for f in `find ${outdir} -name '*-[0-9][0-9][0-9].xml'`
do
cp $f /dc/eurobo/incoming/${batch}
done
done
