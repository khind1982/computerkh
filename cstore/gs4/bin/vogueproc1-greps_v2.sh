#!/bin/sh

usage () {
    echo "Usage: `basename $0` -i issue date" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

while getopts ":i:h" opt;
do
  case $opt in
    i) issuedate="$OPTARG" >&2  ;;

    \?|h)
      usage;
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      usage;
      exit 1
      ;;
  esac
done

if [ -z "$issuedate" ]
then
    die "Issue date in the form YYYYMMDD expected"
fi

year=`echo "${issuedate}" | sed "s!\(....\)....!\1!"`
month=`echo "${issuedate}" | sed "s!....\(..\)..!\1!"`


srcdir="/dc/vogue-images/new_master_data/master_set/${year}/${month}"

if [ -d ${srcdir} ]
  then
    echo "Source directory detected..."
    outdir="/dc/vogue/data/processing/prod_processing/vogue_${year}${month}"
    echo "Creating ${outdir}..."
    mkdir -p ${outdir}
    echo "Creating image list file in /handover/vogue/current..."
    find ${srcdir} -name '*.jpg' -print > /handover/vogue/current/VOGUE_${issuedate}images.txt
    cp /handover/vogue/current/VOGUE_${issuedate}images.txt ${outdir}/VOGUE_${issuedate}images.txt
    echo "Copying XML and pagemap to ${outdir}..."
    rsync -azm --exclude="*.jpg" ${srcdir} ${outdir}/${year}
    echo "Dos to unix file conversion running on XML files..."
    /dc/vogue/utils/auto_dos2unix.sh -d ${outdir} -e xml
    echo "Fixing prism:objects and advertisment titles..."
    python /dc/vogue/utils/Vogue_takingobjectfromtitle.py -d ${outdir}
    echo "Running greps..."
    cd ${outdir}
    /dc/vogue/utils/grepUI.sh . *.out
    echo "Archiving old company and brand clean up file as /dc/vogue/utils/archive/`today`archive_master_obsandins.xlsx"
    cp /dc/vogue/utils/master_obsandins.xlsx /dc/vogue/utils/archive/`today`archive_master_obsandins.xlsx
  else
    die "Source directory /dc/vogue-images/new_master_data/master_set/${year}/${month} not found - copy incoming data to master_set and try again"
fi
