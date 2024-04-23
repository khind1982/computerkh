#!/bin/sh

# Runs all of the intial scripts that should be run on WWD data.

usage () {
    echo "Usage: `basename $0` -b {batchname} -d {directory} -f {file type, e.g *.xml}" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}


while getopts ":b:d:f:h" opt;
do
  case $opt in
    b) batchname="$OPTARG" >&2	;;

    d) directory="$OPTARG" >&2	;;

    f) filetype="$OPTARG" >&2	;;


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

if [ -z "$batchname" ]
then
    die "Batch name specified with -b expected!"
fi

if [ -z "$directory" ]
then
    die "Directory specified with -d expected!"
fi

if [ -z "$filetype" ]
then
    die "File type specified with -f expected!"
fi

mkdir -p /dc/wwd-images/inc_validation/${batchname}_greps

# These are the commands that are passed to the shell

echo "Batch log running"
python2.6 /packages/dsol/platform/bin/log_incoming_batch.py -d ${directory} -p wwd
echo "Image check running"
python2.6 /packages/dsol/platform/bin/wwd-checkimageexists.py -o /dc/wwd-images/inc_validation/${batchname}_greps -d ${directory}
echo "Schema parse running"
find ${directory} -name '*.xml' -exec xmllint --noout --schema /packages/dsol/platform/lib/schemas/wwd_schema.xsd {} + 2>&1 | grep -v validates > /dc/wwd-images/incoming/${batchname}_validation.log
echo "Greps running"
/dc/wwd/utils/grep_final.sh -b ${batchname} -d ${directory} -f ${filetype}
echo "Matrix running"
python2.6 /packages/dsol/platform/bin/wwdmatrix.py -o /dc/wwd-images/inc_validation/${batchname}_greps/${batchname}_matrix.log -d ${directory} -p wwd
