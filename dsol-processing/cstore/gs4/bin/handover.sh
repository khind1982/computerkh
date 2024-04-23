#!/bin/bash

#Move XML files to handover directory; take the full path names for each image in the directory and append it to a list; perform the same process for multiple batches.

case $# in
        4)
                PRODUCT="$1"
                HANDOVER="$2"
                HANDDIR="$3"
                BATCHLIST="$4"
                ;;
        *)
                echo "usage: $0 <product code> <handover e.g. prod_yyyymmdd> <handover directory e.g. /handover/wma, handover/via> <full path to batch list>"
                exit 1
                ;;
esac

if [ -e $BATCHLIST ]
then
    cd /dc/$PRODUCT-images/editorial
else
    echo "usage: $0 This script requires a list of batches from which the image list will be created and the XML files copied to $HANDDIR/$HANDOVER.  Please supply the name and full path of the batch list as the third argument in this script.  If you have already created this list, please check the name of the list matches what you have entered in the command line."
    exit 1
fi

if [ -e $HANDDIR ]
then
    echo "$HANDDIR exists."
else
    echo "$HANDDIR is not the correct name of the handover directory for your product.  Please enter the correct path to the handover directory for your product and try again."
    exit 1
fi

if [ -e $HANDDIR/$HANDOVER ]
then
    echo "$HANDDIR/$HANDOVER exists"
else
    mkdir $HANDDIR/$HANDOVER
fi

for d in `more $BATCHLIST`
do
    if [ -e ${d} ]
    then
        cd ${d}
        echo "Copying xml files for $BATCHLIST to $HANDDIR/$HANDOVER..."
        find . -name "*.xml" | cpio -pd $HANDDIR/$HANDOVER
        echo "Creating image list for batches in $BATCHLIST at $HANDDIR/$HANDOVER..."
        find `pwd` -name \*.jpg >> $HANDDIR/$HANDOVER/$HANDOVER-imagelist.txt
        cd ..        
    else
        echo "${d} does not exist at /dc/$PRODUCT-images/editorial"
    fi
echo "XML files copied"
echo "Image list $HANDOVER-imagelist.txt created"
done