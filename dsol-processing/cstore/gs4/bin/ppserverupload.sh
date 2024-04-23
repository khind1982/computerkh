#!/bin/sh

usage () {
    echo "Usage: `basename $0` [product] [journalprefix]" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

product=${1}
prefix=${2}

if [ -z "$product" ]
then
    die "Please specify a product (Choose from bpc, via, wma...)"
fi


if [ -z "$prefix" ]
then
    die "Please specify journal prefix (BPD, VIA, WMA...)"
fi

for h in canopus capella
do
for d in ${prefix}*
do
rsync --PQI ${d}/ ${h}:/images/${product}/${d}
done
done
