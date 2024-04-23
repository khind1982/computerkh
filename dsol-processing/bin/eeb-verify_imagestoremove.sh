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

containsElement () {
  local e
  for e in "${@:2}"; do [[ "$e" == "$1" ]] && return 1; done
  return 0
}


rootpathls=()

while IFS='' read -r pqid || [[ -n "$pqid" ]]; do
    pqidpath=${pqid//-/\/}
    pqidrootpath=${pqidpath%\/[0-9][0-9][0-9]}
    rootpathls+=("/images/eeb-jpeg-${coll}/$pqidrootpath" "/images/eeb-zoomify-${coll}/$pqidrootpath")
done < "$pqidlist"

# echo list: ${rootpathls[*]}

echo To remove from $coll:

for path in `gfind /images/eeb-*-${coll} -type d -maxdepth 4 -mindepth 4`
do  
# echo list: ${rootpathls[*]}
# echo path: $path
if [[ ! " ${rootpathls[*]} " =~ "$path" ]]
then
    echo $path
fi
done
