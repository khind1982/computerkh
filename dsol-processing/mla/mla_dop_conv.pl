#!/usr/local/bin/perl -w

use strict;
use diagnostics;

print "
##########################################
# mla_dop_conv.pl
# BY RICHARD BARRETT-SMALL SEPT/OCT 04
# CONVERT THE MLA DIRECTORY OF PERIODICALS
##########################################
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

# DEFINE THE FILE TO CONVERT
my $file = $ARGV[0]
  or die "$!\n\nSyntax is...\n\tmla_dop_conv.pl filename(s)\n";
my $text;

#MOVE ALONG THE FILE LIST
while ( $file = shift ) {

    # OPEN THE FILE TO CONVERT
    print "--\nOpening\t\t\t$file\n";
    open( FILE, "<$file" )
      or die "Could not open input file $file: $!\n!\nSyntax is...\n\nmla_dop_conv.pl filename(s)\n\n";

    # DEFINE OUTPUT FILENAME
    my $out = $file;
    if ( $out =~ /\.[a-zA-Z]{3}/ ) { $out =~ s/\..*/\.dop/ }
    else { $out =~ s/$/\.dop/ }

    #OPEN OUTPUT FILE
    open( FILE_OUT, '>', $out )
      or die "Could not open output file $out: $!\n";

    #SLURP IN THE INPUT TEXT
    $text = <FILE>;

    #TIDY INPUT TEXT
#    $text =~ s/\r/\n/g;
#    $text =~ s/\n\n/\n/g;
    #Get rid of speech marks around every record.
    $text =~ s/\"(REC_.*\|)\"/$1/g;
    $text =~ s/</&lt;/g;
    $text =~ s/>/&gt;/g;
    $text =~ s/&/&amp;/g;
    $text =~ s/\x00$//m;

    # BREAK INPUT TEXT INTO RECORDS ACCORDING TO HEX VALUES
    my @filerecs = split( /\x0a/, $text );

    # YOU GOTTA LOVE COUNTERS
    my $reccounter = 0;
    my $record;
    foreach $record (@filerecs) {
        $reccounter++;
        $totalcount++;
        my $fivehundred = $reccounter / 1000;
        if ( $fivehundred =~ "[0-9]+\.[0-9]+" ) { }
        else {
            print "Processing rec...\t$reccounter\n";
        }
        $record =~ s/$/<\/record>/m;
        $record =~ s/^REC_([^|]*)/<record>\n<num>$1<\/num>/m;
        $record =~ s/\|/\n/g;
        $record =~ s/^ACR_(.*?)$/<jnlabbrv>$1<\/jnlabbrv>/gm;
        $record =~ s/^ART_(.*?)$/<article>$1<\/article>/gm;
        $record =~ s/^NAM_(.*?)$/<jnlname>$1<\/jnlname>/gm;
        $record =~ s/^PLA_(.*?)$/<jpubloc>$1<\/jpubloc>/gm;
        $record =~ s/^ACT_(.*?)$/<mlaindex>$1<\/mlaindex>/gm;
        $record =~ s/^PYB_(.*?)$/<firstpub>$1<\/firstpub>/gm;
        $record =~ s/^PUT_(.*?)$/<type>$1<\/type>/gm;
        $record =~ s/--/\n/g;
        $record =~ s/^EDI_|^ELE_|^SUB_|^PER_|^SED_|//gm;
        $record =~ s/^PUB (.*?)$/<edpubl>$1<\/edpubl>/gm;
        $record =~ s/^PED (.*?)$/<ednames><edname>$1<\/edname><\/ednames>/gm;
        while ( $record =~ s/^<ednames>((?:(?!<\/ednames>).)*[^>]); ?/<ednames>$1<\/edname>; <edname>/gm ) { }
        $record =~ s/^PEA (.*?)$/<edadd1>$1<\/edadd1>/gm;
        $record =~ s/^PEZ (.*?)$/<edzip>$1<\/edzip>/gm;
        $record =~ s/^PCO (.*?)$/<edcntry>$1<\/edcntry>/gm;
        $record =~ s/^PEE (.*?)$/<edadd2>$1<\/edadd2>/gm;
        $record =~ s/^PEP (.*?)$/<edtelno>$1<\/edtelno>/gm;
        $record =~ s/^PEF (.*?)$/<edfaxno>$1<\/edfaxno>/gm;
        $record =~ s/^PEM (.*?)$/<edemail>$1<\/edemail>/gm;
        $record =~ s/^PTE (.*?)$/<elcprint>$1<\/elcprint>/gm;
        $record =~ s/^ECL (.*?)$/<elconly>$1<\/elconly>/gm;
        $record =~ s/^INT (.*?)$/<elcurl>$1<\/elcurl>/gm;
        $record =~ s/^<elcurl>(.*?)(http.*?)<\/elcurl>/<elcurl>$1<url>$2<\/url><\/elcurl>/gm;
        $record =~ s/^EFR (.*?)$/<elcfreq>$1<\/elcfreq>/gm;
        $record =~ s/^ECO (.*?)$/<elcinfo>$1<\/elcinfo>/gm;
        $record =~ s/^SUA (.*?)$/<subadd1>$1<\/subadd1>/gm;
        $record =~ s/^SUZ (.*?)$/<subzip>$1<\/subzip>/gm;
        $record =~ s/^SUC (.*?)$/<subcntry>$1<\/subcntry>/gm;
        $record =~ s/^SUS (.*?)$/<subadd2>$1<\/subadd2>/gm;
        $record =~ s/^SUP (.*?)$/<subtelno>$1<\/subtelno>/gm;
        $record =~ s/^SUX (.*?)$/<subfaxno>$1<\/subfaxno>/gm;
        $record =~ s/^SUR (.*?)$/<subrate>$1<\/subrate>/gm;
        $record =~ s/^SUY (.*?)$/<subyear>$1 Subscription Rate:<\/subyear>/gm;
        $record =~ s/<subrate>(.*?<\/subrate>.*?)(<subyear>.*?<\/subyear>)/<subrate>$2 $1/s;
        $record =~ s/^SCO (.*?)$/<perscope>$1<\/perscope>/gm;
        $record =~ s/^SIT (.*?)$/<persubjs><persubj>$1<\/persubj><\/persubjs>/gm;
        while ( $record =~ s/^<persubjs>((?:(?!<\/persubjs>).)*[^>]); ?/<persubjs>$1<\/persubj>; <persubj>/gm ) { }
        $record =~ s/^EPR (.*?)$/<perprrev>$1<\/perprrev>/gm;
        $record =~ s/^PBR (.*?)$/<perbkrev>$1<\/perbkrev>/gm;
        $record =~ s/^PSN (.*?)$/<pershnot>$1<\/pershnot>/gm;
        $record =~ s/^PAB (.*?)$/<perabst>$1<\/perabst>/gm;
        $record =~ s/^PLP (.*?)$/<perlangs><perlang>$1<\/perlang><\/perlangs>/gm;
        while ( $record =~ s/<perlangs>((?:(?!<\/perlangs>).)*[^>]); ?/<perlangs>$1<\/perlang>; <perlang>/g ) { }
        $record =~ s/^CIR (.*?)$/<percirc>$1<\/percirc>/gm;
        $record =~ s/^FRE (.*?)$/<perfreq>$1<\/perfreq>/gm;
        $record =~ s/^AAD (.*?)$/<perads>$1<\/perads>/gm;
        $record =~ s/^ARA (.*?)$/<peradrat>$1<\/peradrat>/gm;
        $record =~ s/^MIC (.*?)$/<permicro>$1<\/permicro>/gm;
        $record =~ s/^MID (.*?)$/<permdist>$1<\/permdist>/gm;
        $record =~ s/^PPG (.*?)$/<perpages>$1<\/perpages>/gm;
        $record =~ s/^ISN (.*?)$/<perissn>$1<\/perissn>/gm;
        $record =~ s/^ESN (.*?)$/<pereissn>$1<\/pereissn>/gm;
        $record =~ s/^SPO (.*?)$/<perspons>$1<\/perspons>/gm;
        $record =~ s/^ROC (.*?)$/<sedlimit>$1<\/sedlimit>/gm;
        $record =~ s/^CHS (.*?)$/<sedcost>$1<\/sedcost>/gm;
        $record =~ s/^CSF (.*?)$/<sedrate>$1<\/sedrate>/gm;
        $record =~ s/^CHP (.*?)$/<sedpcost>$1<\/sedpcost>/gm;
        $record =~ s/^CPC (.*?)$/<sedprate>$1<\/sedprate>/gm;
        $record =~ s/^SLA (.*?)$/<sedartl>$1<\/sedartl>/gm;
        $record =~ s/^SLB (.*?)$/<sedbookl>$1<\/sedbookl>/gm;
        $record =~ s/^SLR (.*?)$/<sedrevl>$1<\/sedrevl>/gm;
        $record =~ s/^SLO (.*?)$/<sednotel>$1<\/sednotel>/gm;
        $record =~ s/^ESP (.*?)$/<sedstyle>$1<\/sedstyle>/gm;
        $record =~ s/^NCM (.*?)$/<sedmsnum>$1<\/sedmsnum>/gm;
        $record =~ s/^BLI (.*?)$/<sedblind>$1<\/sedblind>/gm;
        $record =~ s/^SSR (.*?)$/<sedreqs>$1<\/sedreqs>/gm;
        $record =~ s/^COP (.*?)$/<sedcpyrt>$1<\/sedcpyrt>/gm;
        $record =~ s/^REJ (.*?)$/<sedrejct>$1<\/sedrejct>/gm;
        $record =~ s/^TSP (.*?)$/<seddecis>$1<\/seddecis>/gm;
        $record =~ s/^TDP (.*?)$/<sedpubl>$1<\/sedpubl>/gm;
        $record =~ s/^NOR (.*?)$/<sedreads>$1<\/sedreads>/gm;
        $record =~ s/^ASY (.*?)$/<sedarts>$1<\/sedarts>/gm;
        $record =~ s/^APY (.*?)$/<sedartp>$1<\/sedartp>/gm;
        $record =~ s/^BSY (.*?)$/<sedbooks>$1<\/sedbooks>/gm;
        $record =~ s/^BPY (.*?)$/<sedbookp>$1<\/sedbookp>/gm;
        $record =~ s/^BRY (.*?)$/<sedrevs>$1<\/sedrevs>/gm;
        $record =~ s/^BRP (.*?)$/<sedrevp>$1<\/sedrevp>/gm;
        $record =~ s/^NSY (.*?)$/<sednotes>$1<\/sednotes>/gm;
        $record =~ s/^NPY (.*?)$/<sednotep>$1<\/sednotep>/gm;
        $record =~ s/^DCF (.*?)$/<sedupdat>$1<\/sedupdat>/gm;
        $record =~ s/\n+/\n/g;
        $record =~ s/(<type>.*?<\/type>.*?)(<mlaindex>.*?<\/mlaindex>\n(:?<firstpub>.*?<\/firstpub>\n)?)/$2$1/s;
        print FILE_OUT "$record\n\n";

        if ( $record =~ /^([A-Z]{3})/m or $record =~ /([A-Z]{3}_)/ ) {
            print "Error: $file: $1\n";
        }

    }
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
print "Total recs:\t$totalcount\n";
print "All done!\n\n";
