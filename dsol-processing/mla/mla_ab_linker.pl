#!/opt/perl/bin/perl -w
use strict;
use diagnostics;
use locale;
use String::Approx 'amatch';

print "
#####################################
# mla_ab_linker.pl
# BY RICHARD BARRETT-SMALL NOV 04
# Shoves LION full text details into
# MLA record - Ace!!
#####################################
";

unless ( $ARGV[0] ) {
    die "
\t--
\tSyntax is...\n
\t\tmla_ab_linker.pl mla_file_to_link\n
\tYou must specify the ISSN lut and
\tABELL FT file inside the script.
\t---
";
}
my $mla_file;
undef $/;    # SLURP MODE
#################
# GET IN THE LUT
#################
open( LOG, ">add_ft_info.log" ) || die "Couldn't open add_ft_info.log\n";


#my $mla_ab_matches = "/dc/lion3/data/mla/bib_recs/ftnumnums.txt";    # DEFINE WHERE LUT IS - FOR INSERTING PREVIOUS MLA LINKS
#my $mla_ab_matches = "/dc/elp/lionref/mla/data/20090305/matches.out";    # DEFINE WHERE LUT IS - FOR INSERTING ABELL LINKS
#my $mla_ab_matches = "/dc/misc/python/abell/matches.out";    # DEFINE WHERE LUT IS
#my $mla_ab_matches = "/dc/elp/lionref/data/master/rw_test/matches.out";    # DEFINE WHERE LUT IS - FOR INSERTING ABELL LINKS INTO ABELL BACKFILE
my $mla_ab_matches = "/dc/lion3/data/mla/bib_recs/matches.out";    # DEFINE WHERE LUT IS - FOR INSERTING ABELL LINKS INTO MLA BACKFILE

open( FTLUT, "<$mla_ab_matches" ) || die "LUT error: $!\n";          # SLURP CONTENTS INTO FILE HANDLE
my $lut_text = <FTLUT>;                                              # GET LUT INTO A SCALAR
$lut_text =~ s/\r//g;                                                # GET DOS OUT OF THERE
my @lut_lines = split( "\n", $lut_text );                            # GET LUT LINES INTO LIST
###############
# GET IN ABELL
###############
#my $abell_ft_recs = "/dc/lion3/data/mla/bib_recs/mla_bib.got"; # WHERE ARE ABELL RECS - FOR INSERTING PREVIOUS MLA LINKS
my $abell_ft_recs = "/dc/elp/lionref/data/master/ab_target.txt";     # WHERE ARE ABELL RECS - FOR INSERTING ABELL LINKS
#my $abell_ft_recs = "/dc/lion3/data/mla/bib_recs/mla_bib.20081016"; # WHERE ARE ABELL RECS


################
# LUT INTEGRITY
################
print "Checking look up...\n";
my %lut_hash;
for (@lut_lines) {
    if ( $_ =~ /^<num>([^<]+)<\/num>\|<num>([^<]+)<\/num>$/ ) {
        my $noft = $1;
        my $ft   = $2;
        $lut_hash{$noft} = $ft;
    }
    elsif ( $_ =~ /^([^<]+)\|([^<]+)$/ ) {
            my $noft = $1;
            my $ft   = $2;
        $lut_hash{$noft} = $ft;
    }
    else { die "This line is unacceptable\n $_\n"; }
}
print "...LUT works!\n";
print "Looking for ", $#lut_lines + 1, " matches\n";
my $ftnums = 0;
my %abell_hash;
print "Opening full text source records...\n";
open( ABELL_REX, "<$abell_ft_recs" ) || die "Couldn't open full text source recs: $abell_ft_recs\n$!\n";

print "Building full text source records hash...\n";
$/ = "</record>";
my $counter = 0;
while (<ABELL_REX>) {
    $counter++;
    print $counter, "\n" if $counter % 10000 == 0;
    if (/<num>([^<]+)<\/num>/ )  {

        $abell_hash{$1} = $_;
    }
}

while ( $mla_file = shift ) {

    #my $out = '/home/richards/'. $mla_file . '.lin';
    my $out = $mla_file . '.lin';
    print "Opening $mla_file...\n";
    open( MLA_RECS, "<$mla_file" ) || die "Couldn't open MLA file: $mla_file\n$!\n";
    open( OUT,      ">$out" )      || die "Couldn't open MLA file: $mla_file\n$!\n";
    while (<MLA_RECS>) {
        my $mla_rec = $_;
        my $abell_rec;
        if ( $mla_rec =~ /<num>([^<]+)<\/num>/  ) {
            my $mla_num = $1;
            my $abell_num;
            if ( exists( $lut_hash{$mla_num} ) && $mla_rec !~ /<ftnum>/ ) {
                $abell_num = $lut_hash{$mla_num};
                if ( exists( $abell_hash{$abell_num} ) ) {
                    $abell_rec = $abell_hash{$abell_num};
                    delete $lut_hash{$mla_num};



		   #if a record has <subtype> it will have <updated> and in those cases we want the <texttype> line to come after <updated> and before <num>).
                   #If the record doesn’t have <subtype> and <updated>, then <texttype> can come after <type>.

                   if ( $mla_rec =~ /(<updated>.*?<\/updated>)/){



		   if ( $abell_rec =~ /(<texttype>.*?<\/texttype>)/ ) {
					    my $texttype = $1;
					    ###COPYING FROM TARGET
					    ### DO NOTHING
					    if ( $mla_rec =~ s/<\/updated>/<\/updated>\n$texttype/ ) { }

					    else { print LOG "Could not add <texttype> $mla_num\n" } }


		   else {
		   print LOG "Could not find <texttype> in ABELL $abell_num\n";}




		  }


		  else{

		  if ( $abell_rec =~ /(<texttype>.*?<\/texttype>)/ ) {
				    my $texttype = $1;
				    ###COPYING FROM TARGET
				    ### DO NOTHING
				    if ( $mla_rec =~ s/<\/type>/<\/type>\n$texttype/ ) { }
				    else { print LOG "Could not add <texttype> $mla_num\n" }
				}
				else {
				    print LOG "Could not find <texttype> in ABELL $abell_num\n";
		  }


		  }










                    if ( $abell_rec =~ /(<liftjnl>.*?<\/liftjnl>)/ ) {
                        my $liftjnl = $1;
                        if ( $mla_rec =~ s/<\/texttype>/<\/texttype>\n$liftjnl/ ) { }
                        else { print LOG "Could not add <liftjnl> $mla_num\n" }
                    }
                    else {

                        # print LOG "Could not find <liftjnl> in ABELL $abell_num\n";
                    }







                    #change made to ensure that <ftnum> always comes after the last <num>

			if ( $mla_rec =~ /(<\/num>)\n*?(<[^n].*?>)/ ){
				my $abnum=$1;
				print "cut   ";
				my $xl=$2;

			if ( $abell_rec =~ /(<ftnum>.*?<\/ftnum>)/ ) {
			    my $ftnum = $1;
			    if ( $mla_rec =~ s/(<\/num>)\n*?(<[^n].*?>)/<\/num>\n$ftnum\n$2/ ){}
			    #if ( $mla_rec =~ s/$abnum/<\/num>\n$ftnum/ ) {$ftnums++ }
			    else { print LOG "Could not add <ftnum> $mla_num\n" }
			}
			else {
			    print LOG "Could not find <ftnum> in ABELL $abell_num\n";
			}


		    }







		    #include <rpubdtl> as well as <pubdtl> in the records

                    if ( $abell_rec =~ /(<sortpub>.*?<\/sortpub>)/ ) {
			    my $sortpub = $1;
			    if ( $mla_rec =~ s/<\/pubdtl>/<\/pubdtl>\n$sortpub/ ) { }

			    elsif( $mla_rec =~ s/<\/rpubdtl>/<\/rpubdtl>\n$sortpub/ ) { }

			    else { print LOG "Could not add <sortpub> $mla_num\n" }
			}
			else {
			    print LOG "Could not find <sortpub> in ABELL $abell_num\n";

                    }





                    if ( $mla_rec !~ /<ISSN>/ ) {
                        if ( $abell_rec =~ /(<ISSN>.*?<\/ISSN>)/ ) {
                            my $issn = $1;
                            if ( $mla_rec =~ s/<\/sortpub>/<\/sortpub>\n$issn/ ) { }
                            else { print LOG "Could not add <ISSN> $mla_num\n" }
                        }
                        else {
                            print LOG "Could not find <ISSN> in ABELL $abell_num\n";
                        }
                    }
                    else {

                        # MLA record has <ISSN>
                    }
                    if ( $abell_rec =~ /(<pqname.*?<\/pqname>)/ ) {
                        my $pqname = $1;
                        if ( $mla_rec =~ s/<\/record>/$pqname\n<\/record>/ ) { }
                        else { print LOG "Could not add <pqname> $mla_num\n" }
                    }
                    else {

                        # print LOG "Could not find <pqname> in ABELL $abell_num\n";
                    }
                    if ( $abell_rec =~ /(<keyname.*?<\/keyname>)/ ) {
                        my $keyname = $1;
                        if ( $mla_rec =~ s/<\/record>/$keyname\n<\/record>/ ) { }
                        else { print LOG "Could not add <keyname> $mla_num\n" }
                    }
                    else {

                        # print LOG "Could not find <keyname> in ABELL $abell_num\n";
                    }
                    if ( $abell_rec =~ /(<ltname.*?<\/ltname>)/ ) {
                        my $ltname = $1;
                        if ( $mla_rec =~ s/<\/record>/$ltname\n<\/record>/ ) { }
                        else { print LOG "Could not add <ltname> $mla_num\n" }
                    }
                    else {

                        # print LOG "Could not find <ltname> in ABELL $abell_num\n";
                    }
                    if ( $abell_rec =~ /(<noainame.*?<\/noainame>)/ ) {
                        my $noainame = $1;
                        if ( $mla_rec =~ s/<\/record>/$noainame\n<\/record>/ ) { }
                        else { print LOG "Could not add <noainame> $mla_num\n" }
                    }
                    else {

                        # print LOG "Could not find <noainame> in ABELL $abell_num\n";
                    }
                    if ( $abell_rec =~ /(<dururl>.*?<\/dururl>)/ ) {
                        my $dururl = $1;
                        if ( $mla_rec =~ s/<\/record>/$dururl\n<\/record>/ ) { }
                        else { print LOG "Could not add <dururl> $mla_num\n" }
                    }
                    else {
                        print LOG "Could not find <dururl> in ABELL $abell_num\n";
                    }
                    print OUT $mla_rec;
                }
                else {
                    die "$abell_num not in $abell_ft_recs\n";
                }
            }
            else { print OUT $mla_rec }
        }
        else { }    # no <num> in <record>
    }
    print "$ftnums <ftnums> found\n";
    print "Out:\t$out
Also see log...
"
}
