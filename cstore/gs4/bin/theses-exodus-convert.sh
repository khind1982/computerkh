#!/bin/bash

#Structure of incoming data: /dc/theses/incoming/[batch]/[schoolcode]/[schoolid_number]/[number]/[media/xml]
#New structure desired: /dc/theses/output/[batch]/[schoolcode]/[schoolid_number]/[files for main issue]/
#[Supplements in 02, 03 etc.]

case $# in
    3)
        INDIR="$1"
        OUTDIR="$2"
        BATCH="$3"
        ;;
    *)
        echo "usage: $0 requires three arguments - <input directory e.g. /dc/theses/editorial/[vendor]> <output directory e.g. /dc/theses/output> <batch number>"
        exit 1
        ;;
esac

#Potential errors:
#No INDIR
#Input directories not properly formed - incorrect structure
#No 'main' directories just supplements

if [ ! -e $INDIR ]
then
echo "$INDIR is not a valid input directory. Check the path you entered and try again."
exit 1
fi

if [ ! -e $OUTDIR ]
then
echo "$OUTDIR is not a valid output directory. Check the path you entered and try again."
exit 1
fi

if [ ! -e $INDIR$BATCH ]
then
echo "$BATCH does not exist at $INDIR.  Check the batch name and try again."
exit 1
fi

for dir in `gfind $INDIR$BATCH -mindepth 2 -maxdepth 2`
do
if [ ! -e $dir/01 ]
then
echo "This script expects each thesis sub-directory to have a '01' directory. $dir does not have an '01' sub-directory."
exit 1
fi
done

#Create the batch, institution and supplement directories.
echo "Creating batch, institution and supplement directories at $OUTDIR..."
cd $INDIR > /dev/null
BATCH_SCHOOLID=`gfind $BATCH -mindepth 1 -maxdepth 3`
for d in $BATCH_SCHOOLID
do
mkdir -p $OUTDIR/${d}
done

#Copy all files in the main folder to the individual theses directory in the output.
echo "Copying main files to the main institution directories at $OUTDIR..."
cd $INDIR > /dev/null
for DISSINDIR in `gfind $BATCH -mindepth 2 -maxdepth 2`
do
cd $DISSINDIR > /dev/null
for d in `find . -type d`
do
if [ ${d} == ./01 ]
then
find ${d} -type f -exec cp -r {} $OUTDIR/$DISSINDIR/ ";"
fi
done
cd $INDIR > /dev/null
done

#Copy all supplement folders to the individual theses directories
echo "Copying supplement files to supplement directories at $OUTDIR..."
for DISSINDIR in `gfind $BATCH -mindepth 2 -maxdepth 2`
do
cd $DISSINDIR > /dev/null
for d in `gfind . -mindepth 1 -maxdepth 1`
do
if [ ${d} != ./01 ]
then
cd ${d} > /dev/null
find . -type f -exec cp -r {} $OUTDIR/$DISSINDIR/${d}/ ";"
cd .. > /dev/null
fi
done
cd $INDIR > /dev/null
done

#Rename the thesis subdirectories so they are prefixed by the name of the school subdirectories.  
cd $OUTDIR/$BATCH > /dev/null
for d in `ls`
do
SCHOOLDIR=`echo ${d} | sed 's!\(.*\)\(/\)!\1!g'`
cd $SCHOOLDIR > /dev/null
for d in `ls`
do
DISSDIR=`echo ${d} | sed 's!\(.*\)\(/\)!\1!g'`
mv "$DISSDIR" "$SCHOOLDIR"_"$DISSDIR"
done
cd .. > /dev/null
done

#Remove all of the empty '01' directories
echo "Removing empty sub-directories..."
cd $OUTDIR > /dev/null
for d in `gfind $BATCH -mindepth 3 -maxdepth 3 | grep "/01"`
do
rm -r ${d}
done

echo "Finished."