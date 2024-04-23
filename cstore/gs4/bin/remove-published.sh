#!/bin/bash
# Check that the batch list exists
# Ask the user for confirmation to proceed to delete the files from remove

case $# in
        3)
            PRODUCT="$1"
            BATCHLIST="$2"
            INDIR="$3"
            ;;
        *)
            echo "usage: $0 <product code> <full path to batch list> <path to incoming directory containing batches e.g. /dc/npp-images/incoming/ninestars>"
            exit 1
            ;;
esac

if [ -e $BATCHLIST ]
then
    cd /dc/$PRODUCT-images/editorial
else
    echo "usage: $0 make sure that $BATCHLIST exists and contains the names of the batches you wish to delete from /dc/$PRODUCT-images/editorial and $INDIR."
    exit 1
fi

while true
do
    read -p "Are you sure you want to delete all of the batches listed in $BATCHLIST from /dc/$PRODUCT-images/editorial and $INDIR?" yn
    case $yn in
        [Yy]*)
            for d in `cat $BATCHLIST`
            do
                rm -rf ${d}
                find $INDIR -name ${d} -type d -exec rm -rf {} \;
            done
            break
            ;;
        [Nn]*)
            exit 1
            ;;
        *)
            echo "Please answer 'y''Y' or 'n''N'."
            ;;
    esac
done
echo "Finished."