#!/bin/sh

usage () {
    echo "Usage: `basename $0` {input directory} {output file} {schema to use}" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

trgdir=${1}
outfile=${2}
schema=${3}

if [ -z "$trgdir" ]
then
    die "Please specify a target directory!"
fi

if [ -z "$outfile" ]
then
    die "Please specify output file!"
fi

if [ -z "$schema" ]
then
    die "Please specify schema to use!"
fi

if [ -f ${outfile} ]
then
    echo "" > $outfile
fi


for foo in `find ${trgdir} -name "*.xml"`
do
    xmllint --noout --schema ${schema} ${foo} 2>&1 | grep -v validates >> ${outfile}
done

echo "Schemaparse completed" >> ${outfile}
