#!/bin/bash

usage () {
    echo "Usage: `basename $0` [product] [batch]" >&2
}

#Defines a function that echoes a usage message and displays it to STDERR by redirecting STDIN to STDERR.

die () {
    echo "$1" >&2
    usage
    exit 1
}

#Function name is 'Die'. If only one argument is entered a message appears and the usage function is called then exits with status 1.

product=${1}
batch=${2}

#Two command line arguments.  First is product and second is batch.  

if [ -z "$product" ]
then
    die "Please specify a product (Choose from bpc, bpd, vogueitalia, wmb...)"
fi

#If the 'product' argument hasn't been filled in, ten the 'die' function is activated and the error message is printed.

if [ -z "$batch" ]
then
    die "Please specify batch to return to editorial"
fi

#If the 'batch' argument hasn't been filled in, then the 'die' function is activated and the error message is printed.

valdir=/dc/$product-images/samplings
cd $valdir

parsefile=/dc/$product-images/samplings/parsing-$batch.txt

if [ -e "$parsefile" ]
then
    rm $parsefile
    echo "Parsing file deleted."
fi

for f in `find $batch -name "*.xml"`
do
xmllint --noout --schema /dc/$product-images/utils/$product.xsd ${f} 2>&1 | grep -v "validates" >> ./parsing-$batch.txt
done

if [ -s parsing-$batch.txt ]
then
echo "The data has parsing errors.  Please check /dc/$product-images/samplings/parsing-$batch.txt and correct errors before running unsampler.sh again"
exit 1
else 
echo "No parsing errors detected."
fi

#Run script to remove empty elements
LD_LIBRARY_PATH=/usr/local/lib /dc/content_ops_management/Utils/empty-element-remove-refactored.py $valdir $batch

rec=0

#Defines an argument called 'rec' which has the value '0'

for f in `find $batch -name "*.xml"`
do
    rec=`expr ${rec} + 1`
    #Take the argument 'rec' and add the number '1' at each pass.  This ends up totalling the number of records produced by the 'find' command.  
    mv ${f} /dc/${product}-images/editorial/${f}
    #Each file is moved to the relevant batch in the editorial directory.  
done

echo ${rec} 'records moved to /dc/'$product'-images/editorial/'$batch
#This should equal the total number of records moved to 'editorial'

while true
do
    echo -n "Are you sure you want to remove ${batch} from /dc/${product}-images/samplings? (y/n): "
    read yn
    case $yn in
        [Yy]* ) rm -r /dc/${product}-images/samplings/${batch}; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer y or n.";;
    esac
done
