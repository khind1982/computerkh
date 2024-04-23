#!/bin/sh

usage () {
    echo "Usage: `basename $0` -d directory -x stylesheet -e extension" >&2
}

die () {
    echo "$1" >&2
    usage
    exit 1
}


while getopts ":d:x:e:r:h" opt; 
do
  case $opt in
    d) TGTDIR="$OPTARG" >&2	;;
    
    x) xsl="$OPTARG" >&2	;;
    
    e) extension="$OPTARG" >&2	;;
    
    r) remove="$OPTARG" >&2	;;
    
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

if [ -z "$TGTDIR" ]
then
    die "Directory specified with -d expected!"
fi

if [ -z "$xsl" ]
then
    die "Stylesheet specified with -x expected!"
fi

if [ -z "$extension" ]
then
    die "Extension specified with -e expected!"
fi

if [ -z "$remove" ]
then
   echo "Continuing without removing previous versions of files"
else

for rmf in `find ${TGTDIR} -name "*${suffix}"`
do
    rm $rmf
done

fi

suffix=".press"


runfile=`mktemp -t runner.XXXX`
#rmfile=`mktemp -t remover.XXXX`

# if runfile already exists, truncate it

if [ -f ${runfile} ]
then 
    echo "" > $runfile
fi

for f in `find ${TGTDIR} -name "*\.${extension}"`
do
    
    outf=`echo ${f} | sed "s!\.\(${extension}\)!${suffix}!"`
    if [ ! -f ${outf} ]
    then
        cp ${f} ${outf}
    fi
    echo "xsltproc -o ${f} ${xsl} ${outf}" >> ${runfile}
done


sh $runfile && rm $runfile

