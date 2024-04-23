#!/usr/local/bin/perl5.8.8
# -*- mode: cperl -*-

print $ARGV;
if (@ARGV == 1) {
  die "No file name given."
}

%seen = {};
@uniq = [];

while(<>) {
  chomp $_;
  next if m/^$/;
  if ($_ !~ m/^<([^>]+)(?:[^>]+)?>.*<\/\1>$/) {
    unless ($seen{$_}) {
      $seen{$_} = 1;
      push(@uniq, $_);
    }
  }
}

foreach $thing (@uniq) {
  # TODO: For some reason, without this if modifier,
  # the array seems to have another array as its 0th
  # element. Find out why, and fix it!
  print "$thing\n" if $thing =~ /<\/?.*>/;
}

