#!/bin/sh

usage () {
    echo "Usage: `basename $0` -i issue date -t lookup file" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

while getopts ":i:t:h" opt;
do
  case $opt in
    i) issuedate="$OPTARG" >&2  ;;

    t) lupfile="$OPTARG" >&2   ;;

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
    die "Issue date in the form YYYYMMDD expected!"
fi

if [ -z "$lupfile" ]
then
    die "Look up file specified with -t expected!"
fi

year=`echo "${issuedate}" | sed "s!\(....\)....!\1!"`
month=`echo "${issuedate}" | sed "s!....\(..\)..!\1!"`


srcdir="/dc/vogue/data/processing/prod_processing/vogue_${year}${month}"

if [ -d ${srcdir} ]
  then
    echo "Source directory detected..."
    cd ${srcdir}
    echo "Running the specified look up file over the data..."
    find ${srcdir} -name '*.out' -exec translit ${lupfile} {} \+
    echo "Running the XSLT prep scripts..."
    /dc/vogue/utils/pre-xslt-perlfnr.sh ${srcdir} .out
    /dc/vogue/utils/fix-xslt-perlfnr.sh ${srcdir} .out
    echo "Running the stylesheet transformation..."
    /home/cmoore/bin/auto_xsltproc.sh -d ${srcdir} -x /dc/vogue/utils/vogue.xsl -e out -s _final.xml -r remove
    /dc/vogue/utils/post-xslt-perlfnr.sh ${srcdir} _final.xml
    /dc/vogue/utils/post-xslt-perlfnr.sh ${srcdir} .out
    echo "Running greps for the final version - you'll want to check these..."
    /dc/vogue/utils/grepUI.sh ${srcdir} *_final.xml _final
    echo "Running the data against the output schema - you'll want to check the validation log afterwards before handover..."
    find . -name "*_final.xml" -exec xmllint --noout --schema /dc/vogue/utils/post_xslt_vogueschema.xsd {} + 2>&1 | grep -v validates > validation.log
    echo "Generating the PCMI file..."
    find /dc/vogue-images/new_master_data/master_set/${year}/${month} -name "*.txt" -exec xsltproc -o VOGUE_${issuedate}_PCMI.xml /dc/vogue/utils/PCMI.xsl {} +
    echo "Checking the PCMI..."
    xmllint --noout --schema /dc/vogue/utils/Media_index_schema.xsd VOGUE_${issuedate}_PCMI.xml  > pcmival.log 2>&1
    if grep validates pcmival.log
      then
        echo "PCMI file validates. Copying PCMI to handover..."
        cp VOGUE_${issuedate}_PCMI.xml /handover/vogue/PCMI/
      else
        die "PCMI does not validate. Investigate and fix source pagemap, then run script again."
    fi
    echo "All done - you can now check the XMLs and copy them to the handover area."
   else
    die "Source directory /dc/vogue/data/processing/prod_processing/vogue_${year}${month} not found - try running vogueproc-1.sh first"
fi

