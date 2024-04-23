#!/usr/local/bin/perl -w
use strict;
use diagnostics;
print "
#######################################
# mla_bib_conv.pl
# BY RICHARD BARRETT-SMALL SEPT/OCT 04
# CONVERT THE MLA BIBLIOGRAPHY
# THIS IS STEP 1 OF THE CONVERSION
# subconn fix 09/03/2005
# add doi 15/04/2005
# new format subject indexing 17/01/2005
########################################
";
###########################
# 1 SETUP PREMLIMINARY INFO
###########################
###################
# SET UP THE TIMINGS
###################
my $sec;
my $min;
my $hour;
my $starttime = time;
( $sec, $min, $hour ) = (localtime)[ 0, 1, 2 ];
if ( $sec =~ /^[0-9]$/m ) { $sec =~ s/([0-9])/0$1/ }
if ( $min =~ /^[0-9]$/m ) { $min =~ s/([0-9])/0$1/ }
if ( $min =~ /^[0-9]$/m ) { $min =~ s/([0-9])/0$1/ }
#########################
# LETS HOPE IT STAYS AT 0
#########################
my $errorcount = 0;
################################################
# HOW MANY RECORDS ARE THERE IN THIS SCRIPT RUN?
################################################
my $totalcount = 0;
##################
# ENTER SLURP MODE
##################
undef $/;
#################
# WITTER ON A BIT
#################
printf "\nYou are using perl version %vd\n\n", $^V;
print "Start time:\t$hour:$min:$sec\n--\n";
###################
# CLEAN UP OLD LOGS
###################
unlink "allyears.log";
unlink "pubdates.log";
unlink "mlaerrors.log";
unlink "missingjstor.log";
unlink "mlawarnings.log";
#######################
# 2 SETUP JSTOR LOOK UP
#######################
####################################
# SLURP IN THE JSTOR LOOK UP FOR NOW
####################################
my $jstorlutfile    = "/dc/elp/lionref/mla/lookups/jstorcol.lut";
my $foundjstorcount = 0;
open( JSTLOOK, "<$jstorlutfile" )
  or die "!\nCannot open JSTOR lut: $jstorlutfile\n\t!\n";
my $jstlut = <JSTLOOK>;
$jstlut =~ s/\r//g;
my @jstorjnls = split( /\n/, $jstlut );
my $jnl;
my %jnlhash;

#BREAK UP THE LOOK UP BY LINE
foreach $jnl (@jstorjnls) {

    #TIDY EACH LINE OF LUT
    $jnl =~ s/\s+/ /g;
    $jnl =~ s/^ //m;
    $jnl =~ s/ $//m;

    #GET LOOK UPS INTO A SEARCHABLE HASH
    if ( $jnl =~ /^([^|]+)\|([^|]+)$/m ) {
        $jnlhash{$1} = $2;
    }
    else {
        $errorcount++;
        open( LOG, ">>mlaerrors.log" );
        print LOG "--JSTOR LUT Error--|File:$jstorlutfile|Line:$jnl\n";
    }
}

# DEFINE THE FILE TO CONVERT
my $file = $ARGV[0]
  or die "$!\n\nSyntax is...\n\tmla_convert.pl filename(s)\n";
my $text;

#MOVE ALONG THE FILE LIST
while ( $file = shift ) {

    # OPEN THE FILE TO CONVERT
    print "--\nOpening\t\t\t$file\n";
    open( FILE, "<$file" )
      or die "Could not open input file $file: $!\n!\nSyntax is...\n\nmla_convert.pl filename(s)\n\n";

    # DEFINE OUTPUT FILENAME
    my $out = $file;
    if ( $out =~ /\.[a-zA-Z]{3}/ ) { $out =~ s/\..*/\.xml/ }
    else { $out =~ s/$/\.xml/ }

    #OPEN OUTPUT FILE
    open( FILE_OUT, '>', $out )
      or die "Could not open output file $out: $!\n";
    print FILE_OUT '<?xml version="1.0" encoding="iso-8859-1"?>',                         "\n";
    print FILE_OUT '<!DOCTYPE mla SYSTEM "/dc/elp/lionref/mla/utils_suite/mla_xml.dtd">', "\n";
#    print FILE_OUT '<!DOCTYPE mla SYSTEM "mla_xml_old.dtd">', "\n";
    print FILE_OUT '<mla>',                                                               "\n";

    #SLURP IN THE INPUT TEXT
    $text = <FILE>;

    #TIDY INPUT TEXT
    #$text =~ s/\r//g;
    #$text =~ s/\n//g;
    #Get rid of speech marks around every record.
    $text =~ s/\"(UDC_.*\|)\"/$1/g;
    $text =~ s/\x00$//m;
    $text =~ s/&/&amp;/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;

    # BREAK INPUT TEXT INTO RECORDS ACCORDING TO HEX VALUES
    my @filerecs = split( /\x0a/, $text );

    # YOU GOTTA LOVE COUNTERS
    my $reccounter = 0;
    my $record;
    foreach $record (@filerecs) {
        my $recseqnum = "None";
        $reccounter++;
        $totalcount++;
        if ( $reccounter % 1000 == 0 ) {
            print "Processing rec...\t$reccounter\n";
        }
        $record =~ s/^(.*)$/<record>\n$1\n<\/record>\n/m;
#############################
        # GLOBAL WORK WITH MLA FIELDS
#############################
        $record =~ s/UDC_([^|]+)\|/<attdbase>MLA<\/attdbase>\n<update>$1<\/update>\n/g;
        $record =~ s/KEY_([^|]+)\|/<num>$1<\/num>\n/g;
        if ( $record =~ /<num>(.+?)<\/num>/ ) {
            $recseqnum = $1;
        }
        else {
            print "$record\n";
            next;
        }

        # old book article fudge
        if ( $record =~ /CPP_|CTI_|CAU_/ && $record =~ /TYP_book\|/ ) {
        	$record =~ s/TYP_book\|/TYP_book article\|/;
        	#print $record, "\n";
        	 open( WARN, ">>mlawarnings.log" );
                print WARN "--book article classified as book--|File:$file|Record:$recseqnum|Error: No subjects\n";
        }
	#if ( $record !~ /CPP_|CTI_|CAU_/ && $record =~ /TYP_book article\|/ ) {
	if ( $record !~ /CPP_|CTI_|CAU_/ && $record =~ /TYP_book article\|/ ) {
	        	$record =~ s/TYP_book article\|/TYP_book\|/;
	        	print $record, "\n";
        }
        $record =~ s/SEQ_([^|]+)\|/<seqnum>$1<\/seqnum>\n/g;
        if ( $record =~ /SIC_([^|]+)\|/ ) {
            my $sici = $1;
            $record =~ s/SIC_([^|]+)\|/<sici>$sici<\/sici>\n/g;
        }
        $record =~ s/JSS_([^|]+)\|/<jstorlnk>$1<\/jstorlnk>\n/g;
        while ( $record =~ s/<seqnum>((?:(?!<\/seqnum>|--).)*)--/<seqnum>$1<\/seqnum><seqnum>/g ) { }
        $record =~ s/TYP_([^|]+)\|/<type>$1<\/type>\n/g;
        $record =~ s/DOI_([^|]+)\|/<doi>$1<\/doi>\n/g;
        $record =~ s/ABS_([^|]+)\|/<abstract>$1<\/abstract>\n/g;

        # MOVE THE <TYPE> FIELD TO A LINE OF ITS OWN IMMEDIATELY FOLLOWING THE <ATTDBASE> TAG.
        $record =~ s/<\/attdbase>\n(.*?)(<type>.*?<\/type>\n)/<\/attdbase>\n$2$1/gs;
        $record =~ s/LAN_([^|]+)\|/<langs><language>$1<\/language><\/langs>\n/g;
        while ( $record =~ s/<langs>((?:(?!<\/langs>|--).)*)--/<langs>$1<\/language>; <language>/g ) { }
        $record =~ s/\|/\n/g;
        $record =~ s/TIT_(.+)$/<title>$1<\/title>/gm;
        $record =~ s/TPA_(.+)$/<titlepag>$1<\/titlepag>/gm;
        $record =~ s/ECO_(.+)$/<digcont>$1<\/digcont>/gm;
       
        #########The ECO tag may now contain multiple URLs, separated by double-hyphen...convert  the URLs in different instances of <digcont></digcont>, on separate lines
        ##ADDED 25/3/2010 A.M
        while ( $record =~ s/<digcont>((?:(?!<\/digcont>|--).)*-?)--/<digcont>$1<\/digcont>\n<digcont>/g ) { };

	# RM: REMOVE ANY LEFT-OVER EMPTY ECO_ fields
        $record =~ s/GLO_(.+)$/<notes>$1<\/notes>/gm;
        $record =~ s/AUT_(.+)$/<authdtl><author>$1<\/author><\/authdtl>/gm;
        while ( $record =~ s/<author>((?:(?!<\/author>|--).)*-?)--/<author>$1<\/author>; <author>/g ) { }
        $record =~ s/JNA_(.+)$/<jnlabbrv>$1<\/jnlabbrv>/gm;
        $record =~ s/JNL_(.+)$/<journal>$1<\/journal>/gm;
        $record =~ s/JNP_(.+)$/<jpubloc>$1<\/jpubloc>/gm;
        $record =~ s/JNI_(.+)$/<ISSN>$1<\/ISSN>/gm;
        # RM: ONLY ONE ISSN PLEASE!
        my $issn;
        $issn = $1;
        $record =~ s/<ISSN>.+<\/ISSN>/<ISSN>$issn<\/ISSN>/gs;
        $record =~ s/JNE_(.+)$/<EISSN>$1<\/EISSN>/gm;
        $record =~ s/DAT_(.+)$/<date>$1<\/date>/gm;
        $record =~ s/VOL_(.+)$/<volume>$1<\/volume>/gm;
        $record =~ s/ISS_(.+)$/<issue>$1<\/issue>/gm;
        $record =~ s/<\/volume>\n<issue>/<\/volume>:<issue>/gm;
        $record =~ s/^(<volume>.+)$/<volissue>$1<\/volissue>/gm;
        $record =~ s/^(<issue>.+)$/<volissue>$1<\/volissue>/gm;
        $record =~ s/^EXT_(.+)$/<pages>$1<\/pages>/gm;
        $record =~ s/PRV_(.+)$/<peerrev>$1<\/peerrev>/gm;
        $record =~ s/DES_--/DES_/g;

	# RM: For website records
        $record =~ s/SLU_(.+)$/<lastupdated>$1<\/lastupdated>/gm;
        $record =~ s/SLV_((....).+)$/<lastvisited>$1<\/lastvisited>\n<lastvisitedyear>$2<\/lastvisitedyear>/gm;


        #$record =~ s/&lt;&lt;(.*?)&gt;&gt;/ ($1)/g;
        unless ( $record =~ /DES_[A-Z]{3} / || $record =~ /DES_--NEW--/ ) {
            $record =~ s/DES_/DES_RBS /;
        }
        my ($allsubjs) = $record =~ /DES_(.*)<\/record>\s+$/s;
        if ($allsubjs) {
            $allsubjs = subjecty($allsubjs);
            
            #*$allsubjs=~
            $record =~ s/DES_(.*)<\/record>/$allsubjs\n<\/record>/s;
            #print $record
            
            ##ADDED 25/3/2010 to incorporate  NPN fields A.M
            $record =~ s/(<subjauth>.*?<\/subtext>)<\/subjauth>\n\s*(<npn>.*?<\/npn>)/$1$2<\/subjauth>/gm;
            $record=~s/(<subjfeat>.*?<\/subtext>)<\/subjfeat>\n\s*(<npn>.*?<\/npn>)/$1$2<\/subjfeat>/gm;
            $record =~ s/(<subjsour>.*?<\/subtext>)<\/subjsour>\n\s*(<npn>.*?<\/npn>)/$1$2<\/subjsour>/gm;
            $record =~ s/(<subjgrup>.*?<\/subtext>)<\/subjgrup>\n\s*(<npn>.*?<\/npn>)/$1$2<\/subjgrup>/gm;
            $record =~ s/(<subjinfl>.*?<\/subtext>)<\/subjinfl>\n\s*(<npn>.*?<\/npn>)/$1$2<\/subjinfl>/gm;
            $record =~ s/(<subjwork>.*?<\/subtext>)<\/subjwork>\n\s*(<npn>.*?<\/npn>)/$1$2<\/subjwork>/gm;
            #when there are several values in <npn></npn> separate them.Use ";") to identify each section
	    #but before separating make sure to avoid entities references within (because they end with ";") to be conSidered as <npn></npn> values
	    #another solution; store entities in a list and chec if in
	    #split values separated by ; each become new npn
            #split the record and join later
            my @npnline=();
	    my @recpart = split( /;/, $record );
	    foreach my $recp(@recpart){
            #if the slice is an entity or end with an entity place ### where ; used to be
		if ($recp=~/.+&\S+/ or $recp=~/^\s*?&/){
			push @npnline, $recp."###";}	

		else
		      {push @npnline, $recp.";"}
		#rebuild the line					}
		$record = join( "", @npnline);
		}

            while ( $record =~/<npn>(.*?);\s*(.*?)<\/npn>/){$record =~ s/<npn>(.*?);\s*(.*?)<\/npn>/<npn>$1<\/npn><npn>$2<\/npn>/gm;}
            #re-insert the entities reference endings
            $record=~ s/###/;/gm;
            
        }
        else {
            $errorcount++;
            open( WARN, ">>mlawarnings.log" );
            print WARN "--No Subjects!--|File:$file|Record:$recseqnum|Error: No subjects\n";

        }

        $record =~ s/DAN_(.+)$/<dissabno>$1<\/dissabno>/gm;
        $record =~ s/DGI_(.+)$/<deggrant>$1<\/deggrant>/gm;
        $record =~ s/DGY_(.+)$/<degyear>$1<\/degyear>/gm;
        $record =~ s/CTI_(.+)$/<coltitle>$1<\/coltitle>/gm;
        $record =~ s/CAU_(.+)$/<cauthdtl><cauthor>$1<\/cauthor><\/cauthdtl>/gm;

        # SORT MULTIPLE CAUTHORS SEPARATED BY COLONS
        #while ( $record =~ s/<cauthor>((?:(?!<\/cauthor>|;).)*); /<cauthor>$1<\/cauthor><cauthor>/g ) { }

        # SORT MULTIPLE CAUTHORS SEPARATED BY --
        while ( $record =~ s/<cauthor>((?:(?!<\/cauthor>|--).)*)--/<cauthor>$1<\/cauthor><cauthor>/g ) { }

        #TIDY THAT DODGY ED FIELD
        $record =~ s/<\/cauthor><cauthor>ed.<\/cauthor>/, ed.<\/cauthor>/g;

        #ADD IN THOSE SEMI-COLONS
        $record =~ s/<\/cauthor><cauthor>/<\/cauthor>; <cauthor>/g;
        $record =~ s/CPP_(.+)$/<cpage>$1<\/cpage>/gm;
        $record =~ s/SEA_(.+)$/<serabrv>$1<\/serabrv>/gm;
        $record =~ s/SER_(.+)$/<series>$1<\/series>/gm;
        $record =~ s/SEI_(.+)$/<serissn>$1<\/serissn>/gm;
        $record =~ s/SEP_(.+)$/<spubloc>$1<\/spubloc>/gm;
        $record =~ s/SNO_(.+)$/<sernum>$1<\/sernum>/gm;
        $record =~ s/PUB_(.+)$/<publishr>$1<\/publishr>/gm;
        while ( $record =~ s/<publishr>((?:(?!<\/publishr>|--).)*)--/<publishr>$1; /g ) { }
        $record =~ s/IBN_(.+)$/<ISBNs><ISBN>$1<\/ISBN><\/ISBNs>/gm;
        $record =~ s/IBZ_(.+)$/<ISBNs>$1<\/ISBNs>/gm;
        my $isbn13;
        ($isbn13) = $record =~ m/<ISBNs>(.+?)<\/ISBNs>/m;

        if ($isbn13) {
            my @allisbns = ();
            my @i13s     = split( /--/, $isbn13 );

            foreach my $i13 (@i13s) {
                if ( $i13 !~ /invalid/ ) {

                    #print $i13,"\n";
                    my ($inisbn) = $i13 =~ /([0-9]{13})/;
                    if ($inisbn) {
                        my $outisbn = toisbn10($inisbn);
                        my $i10     = $i13;
                        $i10 =~ s/$inisbn/$outisbn/;
                        push @allisbns, "<ISBN>" . $i10 . "</ISBN>";
                        push @allisbns, "<ISBN13>" . $i13 . "</ISBN13>";
                    }
                    else {

                        push @allisbns, "<ISBN>" . $i13 . "</ISBN>";
                        $errorcount++;
                        open( WARN, ">>mlawarnings.log" );
                        print WARN "--Invalid ISBN13--|File:$file|Record:$recseqnum|Error:$i13\n";
                    }
                }
                else {

                    push @allisbns, "<ISBN>" . $i13 . "</ISBN>";
                }

            }
            my $allisbnsjoin = join( "; ", @allisbns );
            $record =~ s/<ISBNs>.+?<\/ISBNs>/<ISBNs>$allisbnsjoin<\/ISBNs>/;

        }
        while ( $record =~ s/<ISBN>((?:(?!<\/ISBN>|--).)*)--/<ISBN>$1<\/ISBN>; <ISBN>/g )           { }
        while ( $record =~ s/<ISBN13>((?:(?!<\/ISBN13>|--).)*)--/<ISBN13>$1<\/ISBN13>; <ISBN13>/g ) { }
        $record =~ s/PLA_(.+)$/<bpubloc>$1<\/bpubloc>/gm;
        while ( $record =~ s/<bpubloc>((?:(?!<\/bpubloc>|--).)*)--/<bpubloc>$1; /g ) { }
        $record =~ s/<\/bpubloc><bpubloc>/; /g;
        $record =~ s/PYR_(.+)$/<pubdate>$1<\/pubdate>/gm;
        $record =~ s/PAG_(.+)$/<pages>$1<\/pages>/gm;

        # TOC > FESTCONT
        $record =~ s/TOC_(.+)$/<festcont><zall><zt>$1<\/zt><\/zall><\/festcont>/gm;
        while ( $record =~ s/<zt>((?:(?!<\/zt>|\/).)*) \/ /<zt>$1<\/zt><\/zall><zall><zt>/g ) { }

        # CLEAN UP <<DATES>>

#################################################################
        # ENSURE RECORD HAS UNIQUE IDENTIFIER BEFORE BEGINNING PROCESSING
#################################################################
        if ( $record =~ /<num>(.*?)<\/num>/ ) {
            my $recseqnum = $1;
#######################################
            # CHECK EARLIER CONVERSIONS HAVE WORKED
#######################################
            # LEFTOVER <<?
            if ( $record =~ /(&lt;&lt;.*)/ or $record =~ /(.*&gt;&gt;>)/ ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--Remaining << --|File:$file|Record:$recseqnum|Error:$1\n";
            }

            # TITLE FIELDS?- IF NOT ADD A FAKE
            unless ( $record =~ /<title>/ ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--No <title> field--|File:$file|Record:$recseqnum\n";
                if ( $record =~ /<\/authdtl>/ ) {
                    $record =~ s/<\/authdtl>/<\/authdtl>\n<title>[Unknown Title]<\/title>/;
                }
                elsif ( $record =~ /<\/langs>/ ) {
                    $record =~ s/<\/langs>/<\/langs>\n<title>[Unknown Title]<\/title>/;
                }
            }

            # LANGUAGE FIELD? - IF NOT ADD AN EMPTY
            unless ( $record =~ /<language>/ ) {
                $record =~ s/(<title>.+?<\/title>(?:.*?<titlepag>.*?<\/titlepag>)?)\n(.*?)(<authdtl>.*?<\/authdtl>)/$3\n$1\n$2/s;
                $errorcount++;
                open( WARN, ">>mlawarnings.log" );
                print WARN "--No <language> field--|File:$file|Record:$recseqnum\n";
                if ( $record =~ /<authdtl/ ) {
                    $record =~ s/<authdtl/<langs><language>[Unknown]<\/language><\/langs>\n<authdtl/;
                }
                elsif ( $record =~ /<title>/m ) {
                    $record =~ s/<title/<langs><language>[Unknown]<\/language><\/langs>\n<title/;
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No <title> field--|File:$file|Record:$recseqnum\n";
                }
            }

            # ANY LEFTOVER SUBJECT CONNECTORS?
            if ( $record =~ /(&lt;[a-z]{3}[^A-z0-9>=])/ ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--Remaining subject connector--|File:$file|Record:$recseqnum|Error:$1\n";
            }
            if ( $record =~ /^(.*&lt;.*)$/m || $record =~ /^(.*&gt;.*)$/m ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--&gt; or &lt; remains--|File:$file|Record:$recseqnum|Error:$1\n";
            }

            # ANY LEFTOVER MLA FIELDS?
            if ( $record =~ /^([A-Z]{3}_)/m ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--Remaining MLA field--|File:$file|Record:$recseqnum|Error:$1\n";
            }

            # ANY CONSPICUOS FIELDS?
            if ( $record =~ /^([A-Z]{3} .*)$/m ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--Remaining subject field--|File:$file|Record:$recseqnum|Error:$1\n";
            }

            # WARN IF DES_ HAS NO FIRST SUBJECT
            if ( $record =~ /<subjrbs>/m ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--First DES_ field error--|File:$file|Record:$recseqnum|\n";
            }

            # WARN IF DODGY NEW USE
            if ( $record =~ /<subjnew>/m ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--NEW_ treated as subj--|File:$file|Record:$recseqnum|\n";
            }
################################
            # BEGIN TYPE-SPECIFIC PROCESSING
################################
###########################
            #JOURNAL ARTICLE PROCESSING
###########################
            if ( $record =~ /<type>journal article<\/type>/ ) {
                while ( $record =~ s/<ISSN>(.*?)-/<ISSN>$1/g ) { }
                $record =~ s/<\/langs>\n(.+?)(<authdtl>.+?<\/authdtl>)/<\/langs>\n$2\n$1/gs;
                if ( $record =~ /<journal>/ ) {
                    $record =~ s/(<journal>.*<\/journal>)/<pubdtl>$1<\/pubdtl>/g;
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No <journal> error--|File:$file|Record:$recseqnum\n";
                    if ( $record =~ /<\/titlepag>/ ) {
                        $record =~ s/<\/titlepag>/<\/titlepag>\n<pubdtl><journal>[Unknown Journal]<\/journal><\/pubdtl>/;
                    }
                    elsif ( $record =~ /<\/jnlabbrv>/ ) {
                        $record =~ s/<\/jnlabbrv>/<\/jnlabbrv>\n<pubdtl><journal>[Unknown Journal]<\/journal><\/pubdtl>/;
                    }
                    elsif ( $record =~ /<\/title>/ ) {
                        $record =~ s/<\/title>/<\/title>\n<pubdtl><journal>[Unknown Journal]<\/journal><\/pubdtl>/;
                    }
                    else {
                        open( LOG, ">>mlaerrors.log" );
                        print LOG "--Catastrophic <journal> error--|File:$file|Record:$recseqnum\n";
                    }
                }
                $record =~ s/<jpubloc>([^(].*?[^)])<\/jpubloc>/<jpubloc>\($1\)<\/jpubloc>/g;
                $record =~ s/<\/pubdtl>(.*?)(<jpubloc>.*?<\/jpubloc>)/ $2<\/pubdtl>$1/s;
                $record =~ s/<volissue>(.*?)<\/volissue>/<volissue>\($1\)<\/volissue>/g;
                $record =~ s/<\/pubdtl>(.*?)(<volissue>.*?<\/volissue>)/, $2<\/pubdtl>$1/s;
                $record =~ s/<\/pubdtl>(.*?)(<date>.*?<\/date>)/, $2<\/pubdtl>$1/s;
                $record =~ s/<\/pubdtl>(.*?)(<pages>.*?<\/pages>)/, $2<\/pubdtl>$1/s;
                $record =~ s/<notes>([^\(].*?[^\)])<\/notes>/<notes>\($1\)<\/notes>/g;
                $record =~ s/(<notes>.+?<\/notes>)(.+?)<\/pubdtl>/$2 $1<\/pubdtl>/gs;
		$record = serieso($record);
                unless ( $record =~ /<subj/ ) {
                    $record =~ s/^(.*?)(<\/record>\n)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }
                else {
                    $record =~ s/^(.*?)(<subj.*)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }

                # CHECK FOR DATE FIELD AND COLLECT PUBDATE
                if ( $record =~ /<date>(.+?)<\/date>/ ) {
                    my $datey = $1;
                    if ( $datey =~ /no date/ or $datey =~ /n\.d\./ ) {
                        $errorcount++;
                        open( WARN, ">>mlawarnings.log" );
                        print WARN "--No <date> field--|File:$file|Record:$recseqnum|Error:No date\n";
                    }
                    else {

                        #CAPTURE PUBDATE FROM DATE FIELD
                        my $pubdate = $datey;
                        $record =~ s/<pubdate><\/pubdate>/<pubdate>$pubdate<\/pubdate>/;
                        my $allyears = $pubdate;
                        $record =~ s/<allyears><\/allyears>/<allyears>$allyears<\/allyears>/;
                    }
                }
                
                else {
                    $errorcount++;
                    open( WARN, ">>mlawarnings.log" );
                    print WARN "--No <date> field--|File:$file|Record:$recseqnum|Error:No date\n";
                    if ( $record =~ /<num>([0-9]{4})/ ) {
                        my $pubdate = $1;
                        $record =~ s/<pubdate><\/pubdate>/<pubdate>$pubdate<\/pubdate>/;
                        my $allyears = $pubdate;
                        $record =~ s/<allyears><\/allyears>/<allyears>$allyears<\/allyears>/;
                    }
                }
##################
                # JSTOR BUSINESS
##################
                $record =~ s/<jstorlnk>http:\/\/links.jstor.org\/sici\?sici=?/<jstorlnk>/g;
                if ( $record =~ /<jstorlnk>/ ) {

                    # MAKE SURE JOURNAL ARTICLE HAS JOURNAL FIELD FOR GOODNESS SAKES
                    if ( $record =~ /<journal>(.+?)<\/journal>/ ) {
                        my $jnltotry = $1;
                        $jnltotry =~ s/\s+/ /g;
                        $jnltotry =~ s/^ //m;
                        $jnltotry =~ s/ $//m;
                        if ( exists( $jnlhash{$jnltotry} ) ) {
                            $foundjstorcount++;
                            my $jstas = $jnlhash{$jnltotry};
                            if ( $jstas =~ /^<(js[A-z0-9]+)><\/\1>$/m ) {
                                my $jstag = $1;
                                $record =~ s/<jstorlnk>(.+?)<\/jstorlnk>/<jstorlnk><$jstag>$1<\/$jstag><\/jstorlnk>/;
                            }
                            else {
                                $errorcount++;
                                open( LOG, ">>mlaerrors.log" );
                                print LOG "--<jstas> error--|File:$jstorlutfile|Lut line:$jnltotry|$jstas\n";
                            }
                        }
                        else {
                            open( MISSING, ">>missingjstor.log" );
                            print MISSING "$jnltotry\n";
                        }
                    }
                }
            }
###########################
            # BOOK PROCESSING
###########################
            elsif ( $record =~ /<type>book<\/type>/ ) {
                if ( $record =~ /<publishr>/ ) {
                    $record =~ s/(<publishr>.+<\/publishr>)/<pubdtl>$1<\/pubdtl>/;
                    $record =~ s/(<publishr>.+<\/publishr><\/pubdtl>.*?)(<bpubloc>.+<\/bpubloc>)/$2: $1/gs;
                    $record =~ s/(<bpubloc>.+<\/bpubloc>)(.*?)<pubdtl>/$2<pubdtl>$1: /gs;
                }
                elsif ( $record =~ /<bpubloc>/ ) {

                    #PRINT "CABOOSE\N";
                    $record =~ s/(<bpubloc>.+<\/bpubloc>)/<pubdtl>$1<\/pubdtl>/;
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No <pubdtl> in this record--|File:$file|Record:$recseqnum\n";
                    #print $record;
                    if ($record =~ /<titlepag>/ ) {
                    $record =~ s/(<\/titlepag>)(.+?)$/$1\n<pubdtl>[No Publisher Information]<\/pubdtl>$2/s;
                    }
                    else {
			$record =~ s/(<\/title>)(.+?)$/$1\n<pubdtl>[No Publisher Information]<\/pubdtl>$2/s;
                    }
                }
                if ( $record =~ /<pubdate>(.+?)<\/pubdate>/ ) {
                    my $bkpdate = $1;
                    $record =~ s/<\/pubdtl>/, <date>$bkpdate<\/date>.<\/pubdtl>/;
                    my $bkallyears = $bkpdate;
                    $record =~ s/<\/pubdate>/<\/pubdate>\n<allyears>$bkallyears<\/allyears>/;
                }
                else {
                    $errorcount++;
                    open( WARN, ">>mlawarnings.log" );
                    print WARN "--No <pubdate> in this record--|File:$file|Record:$recseqnum\n";
                }
                $record =~ s/(<\/pubdtl>.*?)(<pages>.*?<\/pages>)/ $2.$1/s;
                $record =~ s/<notes>([^(].+?[^)])<\/notes>/<notes>($1)<\/notes>/g;
                $record =~ s/(<notes>.+?<\/notes>)(.*?)<\/pubdtl>/$2 $1<\/pubdtl>/s;
                $record =~ s/<\/pubdtl>(.*?)(<notes>.+?<\/notes>)/ $2<\/pubdtl>$1/s;
                $record =~ s/<\/langs>(.*?)(<authdtl>.+?<\/authdtl>)/<\/langs>\n$2\n$1/s;
		$record = serieso($record);

                #PUT FEST CONT AT END OF RECORD
                $record =~ s/(<festcont>.*?<\/festcont>)(.*?)\n<\/record>/$2\n$1\n<\/record>/gs;
            }
############################
            # BOOK COLLECTION PROCESSING
############################
            elsif ( $record =~ /<type>book collection<\/type>/ ) {
                $record =~ s/<\/langs>(.*?)(<authdtl>.+?<\/authdtl>)/<\/langs>\n$2\n$1/s;
                if ( $record =~ /<publishr>/ ) {
                    $record =~ s/(<publishr>.+<\/publishr>)/<pubdtl>$1<\/pubdtl>/;
                    $record =~ s/(<publishr>.+<\/publishr><\/pubdtl>.*?)(<bpubloc>.+<\/bpubloc>)/$2: $1/gs;
                }
                elsif ( $record =~ /<bpubloc>/ ) {

                    #PRINT "CABOOSE\N";
                    $record =~ s/(<bpubloc>.+<\/bpubloc>)/<pubdtl>$1<\/pubdtl>/;
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No <pubdtl> in this record--|File:$file|Record:$recseqnum\n";
                }



                if ( $record =~ /<pubdate>(.+?)<\/pubdate>/ ) {
                    my $bkcpdate = $1;
                    $record =~ s/<\/pubdtl>/, <date>$bkcpdate<\/date>.<\/pubdtl>/;
                    my $bkcallyears = $bkcpdate;
                    $record =~ s/<\/pubdate>/<\/pubdate>\n<allyears>$bkcallyears<\/allyears>/;
                }
                else {
                    $errorcount++;
                    open( WARN, ">>mlawarnings.log" );
                    print WARN "--No <pubdate> in this record--|File:$file|Record:$recseqnum\n";
                }
                $record =~ s/(<\/pubdtl>.*?)(<pages>.*?<\/pages>)/ $2.$1/s;
                $record =~ s/<notes>([^(].+?[^)])<\/notes>/<notes>($1)<\/notes>/g;
                $record =~ s/(<notes>.+?<\/notes>)(.*?)<\/pubdtl>/$2 $1<\/pubdtl>/s;

                #PUT SERINFO INTO PUBDTL
                $record = serieso($record);
            }
#########################
            # BOOK ARTICLE PROCESSING
#########################
            elsif ( $record =~ /<type>book article<\/type>/ ) {
                $record =~ s/<\/langs>(.*?)(<authdtl>.+?<\/authdtl>)/<\/langs>\n$2\n$1/s;
                if ( $record =~ /<cpage>/ ) {
                    $record =~ s/(<cpage>.+<\/cpage>)/<pubdtl><it>In<\/it> (pp. $1)<\/pubdtl>/;
                }
                elsif ( $record =~ /<cauthdtl>/ ) {
                    $record =~ s/(<cauthdtl>.+<\/cauthdtl>)/<pubdtl><it>In<\/it> $1<\/pubdtl>/;
                }
                elsif ( $record =~ /<coltitle>/ ) {
                    $record =~ s/(<coltitle>.+<\/coltitle>)/<pubdtl><it>In<\/it> $1<\/pubdtl>/;
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No <pubdtl> in this record--|File:$file|Record:$recseqnum\n";
                }
                $record =~ s/(<cauthdtl>.+<\/cauthdtl>)(.*?)<\/pubdtl>/$2 $1<\/pubdtl>/gs;
                $record =~ s/<\/pubdtl>(.*?)(<cauthdtl>.+<\/cauthdtl>)/ $2<\/pubdtl>$1/gs;
                $record =~ s/<coltitle>(.+?)<\/coltitle>/<coltitle><it>$1<\/it>.<\/coltitle>/g;
                $record =~ s/(<coltitle>.+<\/coltitle>)(.+?)<\/pubdtl>/$2, $1<\/pubdtl>/gs;

                $record =~ s/(<\/pubdtl>.*?)(<bpubloc>.+<\/bpubloc>)/ $2:$1/gs;
                $record =~ s/(<\/pubdtl>.*?)(<publishr>.+<\/publishr>)/ $2$1/gs;

                if ( $record =~ /<pubdate>(.+?)<\/pubdate>/ ) {
                    my $bkatpdate = $1;
                    $record =~ s/<\/pubdtl>/, <date>$bkatpdate<\/date>.<\/pubdtl>/;
                    my $bkatallyears = $bkatpdate;
                    $record =~ s/<\/pubdate>/<\/pubdate>\n<allyears>$bkatallyears<\/allyears>/;
                }
                else {
                    $errorcount++;
                    open( WARN, ">>mlawarnings.log" );
                    print WARN "--No <pubdate> in this record--|File:$file|Record:$recseqnum\n";
                }
                $record =~ s/(<\/pubdtl>.*?)(<pages>.*?<\/pages>)/ $2.$1/s;
                $record =~ s/<notes>([^(].+?[^)])<\/notes>/<notes>($1)<\/notes>/g;
                $record =~ s/(<notes>.+?<\/notes>)(.*?)<\/pubdtl>/$2 $1<\/pubdtl>/s;


                $record = serieso($record);
                #$record =~ s/<\/title>\n(.*?)(<digcont>.*?<\/digcont>\n)/<\/title>\n$2$1/gs;
        	##ADDED25/3/2010 there can be now more than 1 <digcont></digcont>(they will be on succesive lines) keep then together
                $record =~ s/<\/title>\n(.*?)(<digcont>.*<\/digcont>\n)/<\/title>\n$2$1/gs;
                
            }
##################################
            # DISSERTATION ABSTRACT PROCESSING
##################################
            elsif ( $record =~ /<type>dissertation abstract<\/type>/ ) {
                $record =~ s/<\/langs>(.*?)(<authdtl>.+?<\/authdtl>)/<\/langs>\n$2\n$1/s;
                $record =~ s/(<journal>.*<\/journal>)/<pubdtl>$1<\/pubdtl>/g;

                # JPUBLOC FUNCTIONALITY
                $record =~ s/<jpubloc>([^(].*?[^)])<\/jpubloc>/<jpubloc>\($1\)<\/jpubloc>/g;
                $record =~ s/<\/pubdtl>(.*?)(<jpubloc>.*?<\/jpubloc>)/ $2<\/pubdtl>$1/s;
                $record =~ s/<volissue>([^(].+?[^)])<\/volissue>/<volissue>($1)<\/volissue>/g;
                $record =~ s/(<\/pubdtl>.*?)(<volissue>.*?<\/volissue>)/, $2$1/s;
                $record =~ s/(<\/pubdtl>.*?)(<date>.*?<\/date>)/ $2,$1/s;
                $record =~ s/(<\/pubdtl>.*?)(<pages>.*?<\/pages>)/ $2.$1/s;
                $record =~ s/<notes>([^(].+?[^)])<\/notes>/<notes>($1)<\/notes>/g;
                $record =~ s/(<notes>.+?<\/notes>)(.*?)<\/pubdtl>/$2 $1<\/pubdtl>/s;
                if ( $record =~ /<deggrant>/ ) {
                    $record =~ s/(<deggrant>.+<\/deggrant>)/<deginfo>$1,<\/deginfo>/;
                }
                elsif ( $record =~ /<degyear>/ ) {
                    $record =~ s/(<degyear>.+<\/degyear>)/<deginfo>$1,<\/deginfo>/;
                }
                elsif ( $record =~ /<dissabno>/ ) {
                    $record =~ s/(<dissabno>.+<\/dissabno>)/<deginfo>$1<\/deginfo>/;
                }
                else {

                    #$ERRORCOUNT++;
                    #OPEN( LOG, ">>MLAERRORS.LOG" );
                    #PRINT LOG "--NO <DEGINFO> IN THIS RECORD--|FILE:$FILE|RECORD:$RECSEQNUM\N";
                }
                $record =~ s/(<\/deginfo>.*?)(<degyear>.*?<\/degyear>)/ $2$1/s;
                $record =~ s/(<dissabno>.+?<\/dissabno>)(.*?)<\/deginfo>/$2 $1<\/deginfo>/s;
                $record =~ s/(<\/pubdtl>.*?)(<deginfo>.*?<\/deginfo>)/ $2.$1/s;
                $record =~ s/<\/degyear> <dissabno>/<\/degyear>. <dissabno>/g;
                unless ( $record =~ /<subj/ ) {
                    $record =~ s/^(.*?)(<\/record>\n)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }
                else {
                    $record =~ s/^(.*?)(<subj.*)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }

                # CHECK FOR DATE FIELD AND COLLECT PUBDATE
                if ( $record =~ /<date>(.+?)<\/date>/ ) {
                    my $datey = $1;
                    if ( $datey =~ /no date/ or $datey =~ /n\.d\./ ) {
                        $errorcount++;
                        open( WARN, ">>mlawarnings.log" );
                        print WARN "--No <date> field--|File:$file|Record:$recseqnum|Error:No date\n";
                    }
                    else {
                        my $pubdate = $datey;
                        $record =~ s/<pubdate><\/pubdate>/<pubdate>$pubdate<\/pubdate>/;

                        # open( PUBDATE, ">>pubdates.log" );
                        # print PUBDATE "<pubdate>$pubdate</pubdate>\n";
                        my $allyears = $pubdate;
                        $record =~ s/<allyears><\/allyears>/<allyears>$allyears<\/allyears>/;

                        # open( ALLYEARS, ">>allyears.log" );
                        # print ALLYEARS "<allyears>$allyears<\/allyears>\n";
                    }
                }
                else {
                    $errorcount++;
                    open( WARN, ">>mlawarnings.log" );
                    print WARN "--No <date> field--|File:$file|Record:$recseqnum|Error:No date\n";
                    if ( $record =~ /<num>([0-9]{4})/ ) {
                        my $pubdate = $1;
                        $record =~ s/<pubdate><\/pubdate>/<pubdate>$pubdate<\/pubdate>/;

                        #CREATE LOG OF PUBDATES
                        # open( PUBDATE, ">>pubdates.log" );
                        # print PUBDATE "<pubdate>$pubdate</pubdate>\n";
                        my $allyears = $pubdate;
                        $record =~ s/<allyears><\/allyears>/<allyears>$allyears<\/allyears>/;

                        # open( ALLYEARS, ">>allyears.log" );
                        # print ALLYEARS "<allyears>$allyears<\/allyears>\n";
                    }
                }
		                $record = serieso($record);
                #IF ( $RECORD =~ /<DEGYEAR/ ) { PRINT "$RECSEQNUM\N" }
            }
##################################
            # DISSERTATION ABSTRACT PROCESSING
##################################
            elsif ( $record =~ /<type>website<\/type>/ ) {

                unless ( $record =~ /<subj/ ) {
                    $record =~ s/^(.*?)(<\/record>\n)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }
                else {
                    $record =~ s/^(.*?)(<subj.*)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }

                if ( $record =~ /<lastvisitedyear>(.+?)<\/lastvisitedyear>/ ) {
                    my $pubdate = $1;
                    $record =~ s/<pubdate><\/pubdate>/<pubdate>$pubdate<\/pubdate>/;
                    my $allyears = $pubdate;
                    $record =~ s/<allyears><\/allyears>/<allyears>$allyears<\/allyears>/;
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--Website record without a lastvisitedyear--|File:$file|Record:$recseqnum\n";
                }
            }

##################################
            # IF NONE OF THE ABOVE TYPES
##################################
                
            # NOT A RECOGNISED TYPE!
            else {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--Not a recognised record type!--|File:$file|Record:$recseqnum\n";
            }

#################################
            # END OF TYPE SPECIFIC PROCESSING
#################################
#####################
            # PUBDATES!
#####################
            if ( $record =~ /<pubdate>(.*?)<\/pubdate>/ ) {

                # TIDY UP THOSE DATES
                my $pubdate = $1;
                $pubdate =~ s/[^0-9-; ]//g;
                $pubdate =~ s/\s+/ /g;
                $pubdate =~ s/^ //m;
                $pubdate =~ s/ $//m;
                $pubdate =~ s/ ?- ?/-/g;
                $pubdate =~ s/-;/;/g;
                $pubdate =~ s/ ;/;/g;
                $pubdate =~ s/([0-9]) ;/$1; /g;
                $pubdate =~ s/([0-9])-;/$1;/g;
                $pubdate =~ s/-+/-/gm;
                $pubdate =~ s/-$//gm;
                $pubdate =~ s/ [0-9]{1,3}-[0-9]{1,3}$//gm;
                $pubdate =~ s/ [0-9]{1,3}$//gm;
                $pubdate =~ s/ [0-9]{1,2}([ ;-])/ $1/gm;
                $pubdate =~ s/ ?- ?/-/g;
                $pubdate =~ s/ ;/;/g;

                # IF THERE'S A 1993-94 TYPE DATE, SORT IT OUT.
                while ( $pubdate =~ s/(([0-9]{2})[0-9]{2})-([0-9]{2})$/$1-$2$3/ ) {
                }
                while ( $pubdate =~ s/(([0-9]{2})[0-9]{2})-([0-9]{2})([ ;-])/$1-$2$3$4/ ) {
                }

                # pubdate for arsing
                my $pubdate2 = $pubdate;
                my @pubdarray;
                while ( $pubdate2 =~ /[^ ;-]{4}/ ) {
                    if ( $pubdate2 =~ /([^ ;-]{4})/ ) {
                        my $yum = $1;
                        push( @pubdarray, $yum );
                        $pubdate2 =~ s/([^ ;-]{4})//;
                    }
                }
                @pubdarray = sort { $a <=> $b } @pubdarray;
                my $item;
                my @uniqpubdates = ();
                my %seen         = ();
                foreach $item (@pubdarray) {
                    unless ( $seen{$item} ) {

                        # if we get here, we have not seen it before
                        $seen{$item} = 1;
                        push( @uniqpubdates, $item );
                    }
                }
                unless ( $pubdate =~ /-/ || $pubdate =~ /;/ ) {
                    $pubdate = join " ", @uniqpubdates;
                }
                elsif ( $pubdate =~ /-/ && $pubdate =~ /;/ ) {
                    $pubdate = join "; ", @uniqpubdates;
                }
                elsif ( $pubdate =~ /;/ ) {
                    $pubdate = join "; ", @uniqpubdates;
                }
                else { $pubdate = join " ", @uniqpubdates; }
                $pubdate =~ s/^([0-9]{4});? ([0-9]{4})$/$1-$2/m;
                $record  =~ s/<pubdate>.*?<\/pubdate>/<pubdate>$pubdate<\/pubdate>/;
                if (   $record =~ /<pubdate>\(no date\)<\/pubdate>/
                    || $record =~ /<pubdate><\/pubdate>/
                    || $record =~ /<pubdate>\(?n\.d\.?\)?<\/pubdate>/i )
                {
                    if ( $record =~ /<num>([0-9]{4})/ ) {
                        $pubdate = $1;
                        $record =~ s/<pubdate>.*?<\/pubdate>/<pubdate>$pubdate<\/pubdate>/;
                    }
                    else {
                        $errorcount++;
                        open( LOG, ">>mlaerrors.log" );
                        print LOG "--No <pdate> no <num> year--|File:$file|Record:$recseqnum|Error:$1\n";
                    }
                }
                open( PUBDATE, ">>pubdates.log" );
                print PUBDATE "<pubdate>$pubdate</pubdate>\n";
                if ( $record =~ /<allyears>(.*?)<\/allyears>/ ) {
                    my $allyears = $pubdate;
                    $allyears =~ s/[^0-9 ]/ /g;
                    $allyears =~ s/\s+/ /g;
                    $allyears =~ s/^ //m;
                    $allyears =~ s/ $//m;

                    # CREATE AN ALLYEARS ARRAY
                    my @allyearsarray = split( " ", $allyears );

                    # FILL IN GAPS IN ALLYEARS
                    while ( $allyears =~ /([0-9]{4}) ([0-9]{4})/ ) {
                        my $lowroller  = $1;
                        my $highroller = $2;
                        if ( $lowroller eq $highroller - 1 ) {

                            #print "OK: $lowroller $highroller\n";
                            push( @allyearsarray, $lowroller );
                            $allyears =~ s/([0-9]{4}) ([0-9]{4})/$2/;
                        }
                        else {

                            #print "No: $lowroller $highroller\n";
                            my $outcome = $highroller - $lowroller;

                            #print "$outcome\n";
                            $allyears =~ s/([0-9]{4}) ([0-9]{4})/$2/;
                            while ( $outcome > 1 ) {
                                $outcome = $outcome - 1;
                                my $inbetween = $highroller - $outcome;
                                push( @allyearsarray, $inbetween );

                                #print $inbetween, "\n";
                            }
                        }
                    }
                    @allyearsarray = sort { $a <=> $b } @allyearsarray;
                    my $item1;
                    my @uniqallyears = ();
                    my %seen1        = ();
                    foreach $item1 (@allyearsarray) {
                        unless ( $seen1{$item1} ) {

                            # if we get here, we have not seen it before
                            $seen1{$item1} = 1;
                            push( @uniqallyears, $item1 );
                        }
                    }
                    $allyears = join " ", @uniqallyears;
                    $record =~ s/<allyears>.*?<\/allyears>/<allyears>$allyears<\/allyears>/;
                    open( ALLYEARS, ">>allyears.log" );
                    print ALLYEARS "<allyears>$allyears<\/allyears>\n";
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No final <allyears> in this record--|File:$file|Record:$recseqnum\n";
                }
            }
            else {
                unless ( $record =~ /<subj/ ) {
                    $record =~ s/^(.*?)(<\/record>\n)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }
                else {
                    $record =~ s/^(.*?)(<subj.*)$/$1<pubdate><\/pubdate>\n<allyears><\/allyears>\n$2/ms;
                }
                if ( $record =~ /<num>([0-9]{4})/ ) {
                    my $pubdate = $1;
                    $pubdate =~ s/[A-z]//g;
                    $pubdate =~ s/\s+/ /g;
                    $pubdate =~ s/^ //m;
                    $pubdate =~ s/ $//m;
                    $pubdate =~ s/ ?- ?/-/g;
                    $record  =~ s/<pubdate><\/pubdate>/<pubdate>$pubdate<\/pubdate>/;
                    open( PUBDATE, ">>pubdates.log" );
                    print PUBDATE "<pubdate>$pubdate</pubdate>\n";
                    my $allyears = $pubdate;
                    $allyears =~ s/[^0-9 ]/ /g;
                    $allyears =~ s/\s+/ /g;
                    $allyears =~ s/^ //m;
                    $allyears =~ s/ $//m;
                    $record   =~ s/<allyears><\/allyears>/<allyears>$allyears<\/allyears>/;
                    open( ALLYEARS, ">>allyears.log" );
                    print ALLYEARS "<allyears>$allyears<\/allyears>\n";
                }
                else {
                    $errorcount++;
                    open( LOG, ">>mlaerrors.log" );
                    print LOG "--No <pdate> no <num> year--|File:$file|Record:$recseqnum|Error:$1\n";
                }
            }
##############
            # PUBDTLS TIDY
##############
            $record =~ s/><\/pubdtl/>.<\/pubdtl/;

            # tidy digcont
            #$record =~ s/<\/title>\n(.*?)(<digcont>.*?<\/digcont>\n)/<\/title>\n$2$1/gs;
	    ##ADDED 25/3/2010 there can be now more than 1 <digcont></digcont>(they will be on succesive lines) keep then together
            $record =~ s/<\/title>\n(.*?)(<digcont>.*<\/digcont>\n)/<\/title>\n$2$1/gs;
            $record =~ s/<\/title>\n(.*?)(<titlepag>.*?<\/titlepag>\n)/<\/title>\n$2$1/gs;

#################
            # PERCENTAGE TIDY
#################
            while ( $record =~ s/^((?:(?!<jstor[^>]+>).)+)%[ST]/$1/m ) { }
            if ( $record =~ /^(.*%[ST].*)$/m ) {
                $errorcount++;
                open( LOG, ">>mlaerrors.log" );
                print LOG "--Remaining %--|File:$file|Record:$recseqnum|Error:$1\n";
            }
        }
############
        # NO SEQNUM?
############
        else {
            $errorcount++;
            open( LOG, ">>mlaerrors.log" );
            while ( $record =~ s/\s+/ /g ) { }
            print LOG "--No <seqnum> in this record--|File:$file|Record:$record\n";
        }

        $record =~ s/<subjmisc><\/subjmisc>//g;
        while ( $record =~ s/\n\n/\n/g ) { }
        $record =~ s/[\t ]+/ /g;
        $record =~ s/=pipe=/\|/g;
        if ($record =~ /(<ISSN>.*?)\n(<pubdtl>.*?)\n/ ) {
        	$record =~ s/(<ISSN>.*?)\n(<pubdtl>.*?)\n/$2\n$1\n/;
  open( LOG, ">>mlaerrors.log" );
                    print LOG "--ISSN in book!--|File:$file|Record:$recseqnum|Error:ISSN in book\n";
        }

###################
        # PRINT OUT THE REC
###################
        print FILE_OUT "$record\n\n";
    }
    print FILE_OUT '</mla>', "\n";
###############################
    # GIVE US THE STATS ON THE FILE
###############################
    print "Total:\t\t\t$reccounter\n";
    close FILE;
    close FILE_OUT;
    print "Output:\t\t\t$out\n";
}
#########################################
# GIVE US THE STATS ON THE SCRIPT SESSION
#########################################
print "--\nStart time:\t$hour:$min:$sec\n";
( $sec, $min, $hour ) = (localtime)[ 0, 1, 2 ];
if ( $sec =~ /^[0-9]$/m ) { $sec =~ s/([0-9])/0$1/ }
if ( $min =~ /^[0-9]$/m ) { $min =~ s/([0-9])/0$1/ }
if ( $min =~ /^[0-9]$/m ) { $min =~ s/([0-9])/0$1/ }
print "End time:\t$hour:$min:$sec\n";
my $endtime = time;
my $secs    = $endtime - $starttime;
print "Duration:\t${secs}s\n";
print "Errors:\t\t$errorcount\n";
print "JSTOR:\t\t$foundjstorcount\n";
print "Total recs:\t$totalcount\n";
print "All done!\n\n";


sub serieso {
	my $record = $_[0];

		my $seriescount = 1;
                while ( $record =~ s/<series>(.*?)<\/series>/<series$seriescount>$1<\/series$seriescount>/ ) {
                    $seriescount++;
                }
                my $serabrvcount = 1;
                while ( $record =~ s/<serabrv>(.*?)<\/serabrv>/<serabrv$serabrvcount>$1<\/serabrv$serabrvcount>/ ) {
                    $serabrvcount++;
                }
                my $spubloccount = 1;
                while ( $record =~ s/<spubloc>(.*?)<\/spubloc>/<spubloc$spubloccount>$1<\/spubloc$spubloccount>/ ) {
                    $spubloccount++;
                }
                my $sernumcount = 1;
                while ( $record =~ s/<sernum>(.*?)<\/sernum>/<sernum$sernumcount>$1<\/sernum$sernumcount>/ ) {
                    $sernumcount++;
                }
                my $serissncount = 1;
                while ( $record =~ s/<serissn>(.*?)<\/serissn>/<serissn$serissncount>$1<\/serissn$serissncount>/ ) {
                    $serissncount++;
                }
                my @multitags = ( "serabrv", "spubloc", "series", "sernum", "serissn" );
                my $multitag;
                foreach $multitag (@multitags) {
                    if ( $record =~ /<$multitag[0-9]+>/ ) {
                        unless ( $record =~ /<serinfo/ ) {
                            $record =~ s/<pubdtl>/<serinfo>\n<\/serinfo>\n<pubdtl>/;
                        }
                        while ( $record =~ /^<$multitag/m ) {
                            if ( $record =~ /^(<$multitag([0-9]+)>.*?<\/$multitag\2>)/m ) {
                                my $thismultitag = $1;

                                #PRINT "$THISMULTITAG\N";
                                #PRINT $THISMULTITAG;
                                my $serinfonum = $2;
                                unless ( $record =~ /<serinfo$serinfonum>/ ) {
                                    $record =~ s/<\/serinfo>/<serinfo$serinfonum>$thismultitag<\/serinfo$serinfonum>\n<\/serinfo>/;
                                    $record =~ s/^\Q$thismultitag\E//m;
                                }
                                else {
                                    $record =~ s/<\/serinfo$serinfonum>/ $thismultitag<\/serinfo$serinfonum>/;
                                    $record =~ s/^\Q$thismultitag\E//m;
                                }
                            }
                        }
                    }
                }

                # TIDY UP SERINFO
                $record =~ s/(<\/serabrv[0-9]+>) /$1/g;
                $record =~ s/<\/spubloc([0-9]+)> /<\/spubloc$1>: /g;
                $record =~ s/ ?(<\/serinfo[0-9]+>)\n?/$1; /g;
                $record =~ s/\n<\/serinfo/<\/serinfo/gs;
                $record =~ s/<serinfo>\n/<serinfo>/gs;
                $record =~ s/; ?<\/serinfo>/<\/serinfo>/gs;
                $record =~ s/<serinfo>(.*?)<\/serinfo>/<serinfo>($1)<\/serinfo>/g;

                #PUT SERINFO INTO PUBDTL
                $record =~ s/(<serinfo>.*?<\/serinfo>)(.*?)<\/pubdtl>/$2 $1<\/pubdtl>/gs;
		return $record;
}

sub toisbn10 {

    my $inny = $_[0];

    #    print "in: ", $inny, "\n";
    my $nine = substr( $inny, 3, 9 );

    my $weight  = 10;
    my $running = 0;
    while ( $weight > 1 ) {
        my $product = $weight * substr( $nine, 10 - $weight, 1 );
        $running += $product;
        $weight--;
    }
    my $modulus = $running % 11;
    my $checkdigit;

    if ( $modulus > 0 ) {
        $checkdigit = 11 - $modulus;
    }
    else {
        $checkdigit = $modulus;

    }

    my $moddo = $running + $checkdigit;

    #print $moddo, "\n";
    #print $moddo % 11, "\n";
    #$shouldmod11 = ( $running + $checkdigit ) % 11;
    if ( $checkdigit == 10 ) {
        $checkdigit = 'X';
    }
    elsif ( $checkdigit > 10 ) {
        die $inny, "\n";
    }

    my $outy = "$nine" . "$checkdigit";

    #print "out: ",  $outy, "\n";
    return $outy;
}

sub subjecty {
    my $sujette;

    foreach $sujette (@_) {

        #print $sujette;
        $sujette =~ s/--([A-Z]{3})/\n$1/g;
        $sujette =~ s/^NEW\n([A-Z]{3} )/$1/gm;
        $sujette =~ s/^RBS (.+)$/<subjmisc>$1<\/subjmisc>/gm;
        $sujette =~ s/^NEW--(.*)$/<subjmisc>$1<\/subjmisc>/gm;
        $sujette =~ s/^NEW-?-?\n//gm;
        $sujette =~ s/^SLN (.*)$/<subjlang>$1<\/subjlang>/gm;
        $sujette =~ s/^SLT (.*)$/<subjlit>$1<\/subjlit>/gm;
        $sujette =~ s/^FLK (.*)$/<subjfolk>$1<\/subjfolk>/gm;
        $sujette =~ s/^LIN (.*)$/<subjling>$1<\/subjling>/gm;
        $sujette =~ s/^GLT (.*)$/<subjgen>$1<\/subjgen>/gm;
        $sujette =~ s/^SJC (.*)$/<subjclas>$1<\/subjclas>/gm;
        $sujette =~ s/^MED (.*)$/<subjmed>$1<\/subjmed>/gm;
        $sujette =~ s/^LWK (.*)$/<subjaltl>$1<\/subjaltl>/gm;
        $sujette =~ s/^LOC (.*)$/<subjloc>$1<\/subjloc>/gm;
        $sujette =~ s/^TIM (.*)$/<subjperi>$1<\/subjperi>/gm;
        $sujette =~ s/^SAU (.*)$/<subjauth>$1<\/subjauth>/gm;
	#########
        ##ADDED 25/3/2010 to include new <npn></npn> field
        $sujette =~ s/^NPN (.*)$/<npn>$1<\/npn>/gm;
        
        $sujette =~ s/^SWK (.*)$/<subjwork>$1<\/subjwork>/gm;
        $sujette =~ s/^WTR (.*)$/<subjtwrk>$1<\/subjtwrk>/gm;
        $sujette =~ s/^GRP (.*)$/<subjgrup>$1<\/subjgrup>/gm;
        $sujette =~ s/^GEN (.*)$/<subjgenr>$1<\/subjgenr>/gm;

        # THESE LFES ARE BOTHERSOME
        $sujette =~ s/^LFE ?(.*)$/<subjfeat>$1<\/subjfeat>/gm;
        $sujette =~ s/^LTC (.*)$/<subjtech>$1<\/subjtech>/gm;
        $sujette =~ s/^LTH (.*)$/<subjthem>$1<\/subjthem>/gm;
        $sujette =~ s/^LIF (.*)$/<subjinfl>$1<\/subjinfl>/gm;
        $sujette =~ s/^LSO (.*)$/<subjsour>$1<\/subjsour>/gm;
        $sujette =~ s/^LPR (.*)$/<subjproc>$1<\/subjproc>/gm;
        $sujette =~ s/^SCP (.*)$/<subjtheo>$1<\/subjtheo>/gm;
        $sujette =~ s/^SAP (.*)$/<subjappr>$1<\/subjappr>/gm;
        $sujette =~ s/^SDV (.*)$/<subjdev>$1<\/subjdev>/gm;
        $sujette =~ s/^SCH (.*)$/<subjsch>$1<\/subjsch>/gm;
        $sujette =~ s/^NDS (.*)$/<subjmisc>$1<\/subjmisc>/gm;
        #print $sujette, "\n" if $sujette =~ /^[A-Z]{3}/m;

        while ( $sujette =~ s/ ?&lt;agn ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(against)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )         { }
        while ( $sujette =~ s/ ?&lt;and ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(and)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )             { }
        while ( $sujette =~ s/ ?&lt;api ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(application in)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )  { }
        while ( $sujette =~ s/ ?&lt;apo ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(application of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )  { }
        while ( $sujette =~ s/ ?&lt;apt ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(applied to)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )      { }
        while ( $sujette =~ s/ ?&lt;asx ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(as)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;atx ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(at)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;bet ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(between)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )         { }
        while ( $sujette =~ s/ ?&lt;byx ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(by)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;cot ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(compared to)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )     { }
        while ( $sujette =~ s/ ?&lt;dat ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(date)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )            { }
        while ( $sujette =~ s/ ?&lt;dsc ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(discusses)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )       { }
        while ( $sujette =~ s/ ?&lt;dur ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(during)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )          { }
        while ( $sujette =~ s/ ?&lt;esp ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(especially)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )      { }
        while ( $sujette =~ s/ ?&lt;fau ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(for audience)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )    { }
        while ( $sujette =~ s/ ?&lt;for ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(for)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )             { }
        while ( $sujette =~ s/ ?&lt;frm ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(from)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )            { }
        while ( $sujette =~ s/ ?&lt;inc ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(includes)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )        { }
        while ( $sujette =~ s/ ?&lt;int ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(into)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )            { }
        while ( $sujette =~ s/ ?&lt;inx ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(in)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;iof ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(influence of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )    { }
        while ( $sujette =~ s/ ?&lt;ion ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(influence on)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )    { }
        while ( $sujette =~ s/ ?&lt;ofx ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;onx ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(on)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;ret ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(relationship to)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge ) { }
        while ( $sujette =~ s/ ?&lt;rin ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(role in)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )         { }
        while ( $sujette =~ s/ ?&lt;rof ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(role of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )         { }
        while ( $sujette =~ s/ ?&lt;soi ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(sources in)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )      { }
        while ( $sujette =~ s/ ?&lt;stu ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(study example)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )   { }
        while ( $sujette =~ s/ ?&lt;taf ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(to and from)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )     { }
        while ( $sujette =~ s/ ?&lt;thr ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(theories of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )     { }
        while ( $sujette =~ s/ ?&lt;tin ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(treatment in)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )    { }
        while ( $sujette =~ s/ ?&lt;tof ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(treatment of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )    { }
        while ( $sujette =~ s/ ?&lt;tox ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(to)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;twd ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(toward)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )              { }
        while ( $sujette =~ s/ ?&lt;usi ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(use in)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )          { }
        while ( $sujette =~ s/ ?&lt;uso ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(use of)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )          { }
        while ( $sujette =~ s/ ?&lt;wit ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(with)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge )            { }
        while ( $sujette =~ s/ ?&lt;agn<subconn>\(/<subconn>\(against /g )                                                                                          { }
        while ( $sujette =~ s/ ?&lt;and<subconn>\(/<subconn>\(and /g )                                                                                              { }
        while ( $sujette =~ s/ ?&lt;api<subconn>\(/<subconn>\(application in /g )                                                                                   { }
        while ( $sujette =~ s/ ?&lt;apo<subconn>\(/<subconn>\(application of /g )                                                                                   { }
        while ( $sujette =~ s/ ?&lt;apt<subconn>\(/<subconn>\(applied to /g )                                                                                       { }
        while ( $sujette =~ s/ ?&lt;asx<subconn>\(/<subconn>\(as /g )                                                                                               { }
        while ( $sujette =~ s/ ?&lt;atx<subconn>\(/<subconn>\(at /g )                                                                                               { }
        while ( $sujette =~ s/ ?&lt;bet<subconn>\(/<subconn>\(between /g )                                                                                          { }
        while ( $sujette =~ s/ ?&lt;byx<subconn>\(/<subconn>\(by /g )                                                                                               { }
        while ( $sujette =~ s/ ?&lt;cot<subconn>\(/<subconn>\(compared to /g )                                                                                      { }
        while ( $sujette =~ s/ ?&lt;dat<subconn>\(/<subconn>\(date /g )                                                                                             { }
        while ( $sujette =~ s/ ?&lt;dsc<subconn>\(/<subconn>\(discusses /g )                                                                                        { }
        while ( $sujette =~ s/ ?&lt;dur<subconn>\(/<subconn>\(during /g )                                                                                           { }
        while ( $sujette =~ s/ ?&lt;esp<subconn>\(/<subconn>\(especially /g )                                                                                       { }
        while ( $sujette =~ s/ ?&lt;fau<subconn>\(/<subconn>\(for audience /g )                                                                                     { }
        while ( $sujette =~ s/ ?&lt;for<subconn>\(/<subconn>\(for /g )                                                                                              { }
        while ( $sujette =~ s/ ?&lt;frm<subconn>\(/<subconn>\(from /g )                                                                                             { }
        while ( $sujette =~ s/ ?&lt;inc<subconn>\(/<subconn>\(includes /g )                                                                                         { }
        while ( $sujette =~ s/ ?&lt;int<subconn>\(/<subconn>\(into /g )                                                                                             { }
        while ( $sujette =~ s/ ?&lt;inx<subconn>\(/<subconn>\(in /g )                                                                                               { }
        while ( $sujette =~ s/ ?&lt;iof<subconn>\(/<subconn>\(influence of /g )                                                                                     { }
        while ( $sujette =~ s/ ?&lt;ion<subconn>\(/<subconn>\(influence on /g )                                                                                     { }
        while ( $sujette =~ s/ ?&lt;ofx<subconn>\(/<subconn>\(of /g )                                                                                               { }
        while ( $sujette =~ s/ ?&lt;onx<subconn>\(/<subconn>\(on /g )                                                                                               { }
        while ( $sujette =~ s/ ?&lt;ret<subconn>\(/<subconn>\(relationship to /g )                                                                                  { }
        while ( $sujette =~ s/ ?&lt;rin<subconn>\(/<subconn>\(role in /g )                                                                               { }
        while ( $sujette =~ s/ ?&lt;rof<subconn>\(/<subconn>\(role of /g )                                                                               { }
        while ( $sujette =~ s/ ?&lt;soi<subconn>\(/<subconn>\(sources in /g )                                                                            { }
        while ( $sujette =~ s/ ?&lt;stu<subconn>\(/<subconn>\(study example /g )                                                                         { }
        while ( $sujette =~ s/ ?&lt;taf<subconn>\(/<subconn>\(to and from /g )                                                                           { }
        while ( $sujette =~ s/ ?&lt;thr<subconn>\(/<subconn>\(theories of /g )                                                                           { }
        while ( $sujette =~ s/ ?&lt;tin<subconn>\(/<subconn>\(treatment in /g )                                                                          { }
        while ( $sujette =~ s/ ?&lt;tof<subconn>\(/<subconn>\(treatment of /g )                                                                          { }
        while ( $sujette =~ s/ ?&lt;tox<subconn>\(/<subconn>\(to /g )                                                                                    { }
        while ( $sujette =~ s/ ?&lt;twd<subconn>\(/<subconn>\(toward /g )                                                                                    { }
        while ( $sujette =~ s/ ?&lt;usi<subconn>\(/<subconn>\(use in /g )                                                                                { }
        while ( $sujette =~ s/ ?&lt;uso<subconn>\(/<subconn>\(use of /g )                                                                                { }
        while ( $sujette =~ s/ ?&lt;wit<subconn>\(/<subconn>\(with /g )                                                                                { }
        while ( $sujette =~ s/ ?&lt;wit ((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>(with)<\/subconn><subtext>".displayName($1)."<\/subtext>"/ge ) { }

        $sujette =~ s/ ?&lt;zot ([^:]+):((?:(?!<\/?sub[^>]+>|&lt;[a-z]{3} ).)*)/"<subconn>($1)<\/subconn><subtext>".displayName($2)."<\/subtext>"/ge;

        $sujette =~ s/(<subj[^>]+>)([^<]+)</"$1<subtext>".displayName($2)."<\/subtext><"/ge;
        $sujette =~ s/ <\//<\//g;
        $sujette =~ s/\s+$//;

        #$sujette =~ s/<subtext><\/subtext>//g;
        print $sujette, "\n" if $sujette =~ /&lt;[a-z]{3} /;    # or $sujette =~ /[A-Z]{3} /;
        return $sujette;
        
    }

}

sub displayName {
    my $with_date = $_[0];

    #$record =~ s/&lt;&lt;(.*?)&gt;&gt;/ ($1)/g;
    unless ( $with_date =~ /&lt;&lt;.*?&gt;&gt/ ) {

        #print 'No date: ', $with_date, "\n";
        return '<ss>' . $with_date . '</ss>';
    }
    else {

        #print 'date: ', $with_date, "\n";
        my $without = $with_date;

        # if (  $without =~ s/^(.*?) ?(\(fl. ?[0-9]{3,4}(?:-[0-9]{3,4})?\))$/<ss>$1<\/ss><sd>$2<\/sd>/ ) {}
        # elsif ( $without =~ s/^(.*?) ?(\([0-9]{3,4}-[0-9]{3,4}\))$/<ss>$1<\/ss><sd>$2<\/sd>/ ) {}
        # elsif ( $without =~ s/^(.*?) ?(\([0-9]{3,4}- +\))$/<ss>$1<\/ss><sd>$2<\/sd>/ ) {}
        # else {
        # print $without,"\n";
        # $without = '<ss>' . $without . '</ss>';
        # }
        $without =~ s/^(.*?) ?&lt;&lt;(.*?)&gt;&gt;.*$/<ss>$1<\/ss><sd>($2)<\/sd>/;

        # <subsrch>Sisinnius, Saint (d. 397)</subsrch>
        #          <subdisp>Strabo (64/63 B.C.-23 A.D.)</subdisp>
        #          <subsrch>Strabo (64/63 B.C.-23 A.D.)</subsrch>
        #print 'done: ', $without, "\n";
        return $without;
    }
}


