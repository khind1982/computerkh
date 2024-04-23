#!/bin/bash

#case tests multiple conditions; here used to test three cases
#valid values for 3rd argument will be SAMPLE, BATCH1, PRELAUNCH, ONGOING.
case $# in
	3) 
		PRODUCT="$1"
		BATCH="$2"
		INDIR="$3"
		;;
	*) 
		echo "usage: $0 <product code> <batch id> <full path to directory where batch is located e.g. /dc/npp-images/incoming/innodata>"
		exit 1
		;;
esac
#change to incoming directory for relevant product and copy data to new batch folder in editorial
cd $INDIR
echo "Copying images and xml files to /dc/$PRODUCT-images/editorial..."
# find $BATCH -name "*.xml" -o -name "*.jpg" -o -name "*.pdf" | cpio -pd ~/dc/$PRODUCT-images/editorial
find $BATCH -name "*.xml" -o -name "*.jpg" -o -name "*.pdf" | cpio -pd /dc/$PRODUCT-images/editorial
echo "XML files and images now copied to /dc/$PRODUCT-images/editorial"

#remove zip files
echo "Removing zip files from $INDIR/$BATCH..."
find $INDIR/$BATCH -name "*.zip" -exec echo rm -rf {} \;
find $INDIR/$BATCH -name "*.zip" -exec rm -rf {} \;
echo "zip files in $INDIR/$BATCH removed."

#change user permissions on the files moved from incoming to editorial
# cd ~/dc/$PRODUCT-images/editorial
cd /dc/$PRODUCT-images/editorial
find $BATCH/ -name \*.xml -exec chmod 777 {} \;
find $BATCH/ -name xml -type d -exec chmod 777 {} \;
echo "file and directory permissions in /dc/$PRODUCT-images/editorial/$BATCH have been changed"
echo "Finished. Have a good day."