#!/bin/bash

#Copy XML from handover directory to master archive at journal level. /handover/{project}/{release}/{title}/ to /dc/{project}-images/master
#Copy images from editorial directory to master archive at journal level. /dc/{project}-images/editorial/ to /dc/{project}-images/master
#Message to remind the user to keep a record of their image list.  

case $# in
        2)
            PRODUCT="$1"
            BATCHLIST="$2"                                                            
            ;;
        *)
            echo "usage: $0 <product code> <full path to batch list>"
            exit 1
            ;;
esac

echo "Copying images and XML from `cat $BATCHLIST` to /dc/$PRODUCT-images/master..."
cd /dc/$PRODUCT-images/editorial
for d in `more $BATCHLIST`
do
    if [ -e ${d} ]
    then
        cd ${d}
        find . -name '*.xml' -o -name '*.jpg' -o -name '*.pdf' | cpio -pd /dc/$PRODUCT-images/master
        cd ..
    else
        echo "${d} does not exist!!!"
    fi
done

echo "Finished copying. Remember to check the contents of the master directory before running 'remove-published.sh'."