#!/bin/sh

usage () {
    echo "Usage: `basename $0` -p pagemap file -i issue date" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}

while getopts ":j:p:i:h" opt;
do
  case $opt in
    p) pagemap="$OPTARG" >&2  ;;

    i) issuedate="$OPTARG" >&2   ;;

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

echo "Generating the PCMI file"
xsltproc -o VOGUE_${issuedate}_PCMI.xml /dc/vogue/utils/PCMI.xsl ${pagemap}
echo "Checking the PCMI..."
xmllint --noout --schema /dc/vogue/utils/Media_index_schema.xsd VOGUE_${issuedate}_PCMI.xml
echo "Copying PCMI to handover..."
cp VOGUE_${issuedate}_PCMI.xml /handover/vogue/PCMI/
echo "Copying image list to handover..."
cp images.txt /handover/vogue/current/VOGUE_${issuedate}_images.txt

