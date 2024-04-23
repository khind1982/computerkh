#!/bin/sh

usage () {
    echo "Usage: `basename $0` [product] [journalprefix] [instance servers]" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

product=${1}
prefix=${2}
instance=${3}

if [ -z "$product" ]
then
    die "Please specify a product (Choose from bpc, via, wma...)"
fi

if [ "$product" == "eim" ]
then
    product="eima"
fi


if [ -z "$prefix" ]
then
    die "Please specify journal prefix (BPD, VIA, WMA...)"
fi

if [ -z "$instance" ]
then
    die "Please specify an instance server - preprod or prod"
fi

do_rsync() {
    hostname=$1
    for d in ${prefix}*
    do
        rsync -av --progress --chmod=u=rwx,g=rwsx,o=rx --rsh=ssh --rsync-path=/usr/local/bin/rsync ${d}/ ${hostname}:/chadwyck/images/${product}/${d}
    done
    return $?
}


case ${instance} in
    preprod)
        do_rsync capella
        ;;
    prod)
        do_rsync pqsun106
        ;;
    *)
        die "Instance server ${instance} is not recognised. Please choose from preprod or prod."
        ;;
esac
