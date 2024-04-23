#!/usr/local/bin/bash

function do_the_renaming {
    if [[ $1 =~ hin-wel-all-[0-9]{8}-[0-9]{3} ]]
    then
      INPUTIMAGEDIR=`grep "$1" eeb_wellcome_delivery_"${TODAYDATE}".temp`
      INPUTIMAGEBOOKDIR=`dirname "${INPUTIMAGEDIR}"`
      /home/twilson/temp/eeb_wellcome_image_rename.py "${INPUTIMAGEBOOKDIR}" "${OUTPUTDIR}" "$1"
    fi
}

case $# in
    2)
        PQIDSOURCE=$1
        IMAGELOCATION=$2
        ;;
    *)
        echo "Usage: $0 <pqid or path to file containing list of pqids> <absolute path to location of input image files>"
        exit 1
        ;;
esac

TODAYDATE=`date +%Y%m%d`

# take input directory, use find to generate temporary list of all pqids to be found there
find "${IMAGELOCATION}" -name 'hin-*' | grep -v 'jp2' > eeb_wellcome_delivery_"${TODAYDATE}".temp

# create batch output directory
OUTPUTDIR="/dc/dsol/eurobo/conv/${TODAYDATE}"
mkdir -p "${OUTPUTDIR}"

# test whether input is file
# if so run rename script on each pqid in file
if [[ -f ${PQIDSOURCE} ]]
then
  while read -r line || [[ -n "$line" ]]; do
    do_the_renaming ${line}
  done < ${PQIDSOURCE}
else
  do_the_renaming ${PQIDSOURCE}
fi


#for each dir in output area jpylyze dir contents
for dir in "${OUTPUTDIR}"/*; do
      python2.7 /home/twilson/bin/jpylyzer.py -w "${dir}"/*.jp2 > "${dir}"/jpylyzer.log
done

#read all the jpylyzer files and produce summary
/home/twilson/temp/eeb_wellcome_image_validator.py "${OUTPUTDIR}"








#delete the temporary pqid list

#if all okay do automated ftp? or do this separately?
#at any rate, ftp should
#find correct collection folder
#create bnumber folder
#create images folder
#upload images
#go up one level and add empty text file
#exit ftp and cleanup - deleting jpylyzer logs? but not images?
#check all images delivered correctly


#    # check line is a pqid
#    if [[ "$line" =~ hin-wel-all-[0-9]{8}-[0-9]{3} ]]
#    then
#      INPUTIMAGEDIR="(grep "${line}" eeb_wellcome_delivery_"${TODAYDATE}".temp)"
#      INPUTIMAGEBOOKDIR="(dirname "${INPUTIMAGEDIR}")"
#      /home/twilson/temp/eeb_wellcome_image_rename.py "${INPUTIMAGEBOOKDIR}" "${OUTPUTDIR}" "${line}"
#    fi
