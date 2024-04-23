<?php

// $directory = '/dc/hba-images/incoming/ninestars/HBA0011/HBA000001/20010501/01/xml';
$directory = '/dc/hba-images/incoming/ninestars/HBA0011';
echo $directory.'<br>';
$root_path = new RecursiveDirectoryIterator($directory);
$raw_files = new RecursiveIteratorIterator($root_path,RecursiveIteratorIterator::SELF_FIRST);
foreach ($raw_files as $work_file) {
  if (substr($work_file, -4) === '.xml') {
    echo $work_file.'<br>';
  }
}
