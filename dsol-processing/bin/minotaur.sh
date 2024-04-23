#!/bin/bash

#Navigate to /dc/wma-images/incoming/WMA0100 and run the batch logging command.
#$/packages/dsol/platform/bin/leviathan-batchlog-issues.py {batch directory}/dc/wma-images/incoming/WMA0100/ -n{batch note}test -r{batch delivery date} 01/01/2001 -s
#$/packages/dsol/platform/bin/schemaparse.sh {input directory}/dc/wma-images/incoming/WMA0100/ {output file}WMA0100-parsing.txt {schema to use}/dc/wma-images/utils/wma_schema.xsd
#$/packages/dsol/platform/bin/leviathan-data_audit.py {batch directory}/dc/wma-images/incoming/WMA0100/ {output file}WMA0100-audit.txt
#$Go
#...
#trap "exit 1" SIGINT

while getopts n:d:sp opt
do
	case $opt in
		n)note=$OPTARG;;
		d)deldate=$OPTARG;;
		s)resupp=1;;
		p)checkspelling=1;;
		*)echo "Invalid option - $opt"
		exit 1;;
	esac
done
shift $(($OPTIND -1))
case $# in
	3)
		PRODUCT="$1"
		BATCH="$2"
		#Make the following two arguments optional
		#Make the deldate argument conform to a specific date format, e.g. mmddyyyy
		#NOTE="$3"
		#DELDATE="$4"
		#Include a sixth argument that, if used, suppresses resupply searching
		INPATH="$3"
		;;
	*)
		echo "usage: $0 [-n <batchnote>] [-d <deldate>] [-s] [-p] <product code> <batch id> <full path to batch in 'incoming' folder e.g. /dc/hba-images/incoming/HBA0001>"
		exit 1
		;;
esac

#Navigate to the batch level directory
cd $INPATH

#Unzip the zip files
echo "Unzipping zip files for $INPATH..."
for f in `find . -name '*.zip'`; do unzip -d `dirname ${f}` ${f}; done

#Change permissions
echo "Opening file and directory permissions for $INPATH..."
find . -name \*.xml -exec chmod 777 {} \;
find . -name xml -type d -exec chmod 777 {} \;

#Run the batch logging script
echo "Running leviathan-batchlog-issues.py..."
if [[ ! -z $note ]]
then
	NOTE="-n $note"
fi

if [[ ! -z $deldate ]]
then
	DELDATE="-r $deldate"
fi

if [[ ! -z $resupp ]]
then
	RESUPP="-s"
fi

if [[ $PRODUCT == 'ger' ]]
then
	find . -name '*[0-9].txt' -exec cat {} + > ${BATCH}_doclinks.txt
fi

python2 /packages/dsol/platform/bin/leviathan-batchlog-issues.py $INPATH $NOTE $DELDATE $RESUPP
#The -s switch as this suppresses resupply searching

#Run the parsing script
echo "Parsing the data in $BATCH..."
/packages/dsol/platform/bin/schemaparse.sh $INPATH $BATCH-parsing.txt /dc/content_ops_management/project_toolkit/vendor_toolkit/data_spec_and_schema/leviathan.xsd

#Run the audit script
echo "Running the data audit script..."

if [[ ! -z $checkspelling ]]
then
	CHECK='--spellcheck'
	echo "Spelling check will run on XMLs in $BATCH"
	echo "Currently supported languages: English, Spanish, French, Portugese, German, Russian"
fi

leviathan_audit $INPATH $BATCH-audit.txt $CHECK

echo "Finished!"
