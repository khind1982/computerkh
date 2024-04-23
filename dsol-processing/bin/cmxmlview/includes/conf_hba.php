<?php

// full product name for display in title
$prod = 'Harper\'s Bazaar';

// directories lookup location
$directories_lookup = '/dc/'.$product[2].'-images/editorial/directories_'.$user[1].'.txt';
include '../includes/config.php';

// directories.php -> dropdown display
$path_substr_begin = 24;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 24;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/'.$product[2].'-images/editorial/";

// images.php -> network path to images
$network = str_replace("xml", "images", $current_path);

// images.php -> symlink path to images
$image_path = $os->join('/xmlviewer/', $product[2]);
$image_path = $os->join($image_path, '/images');

$image_path = $os->join($image_path, substr(str_replace("/dc/hba-images/editorial","",$current_path), 0, -4));
$image_path = $os->join($image_path, '/images');

// $image_path = '/xmlviewer/'.$product[2].'/images/'.substr($current_path, 34, -4).'images';
// echo '$image_path '.$image_path.'<br>';
// $image_path /xmlviewer/hba/images/HBA0003/HBA000001/19940301/01/images
// images.php -> multipliers
$multiplier = 5.5;
$coords_mtp = 5.5;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

// /dc/hba-images/Incoming/Ninestars/Batch1/19900201/01/xml
// /dc/hba-images/Incoming/Ninestars/Batch1/19900201/01/images

// settings for feedback form.
$batch_ref_split = explode('/', $current_path);
$batch_ref = $batch_ref_split[4];

// /dc/hba-images/validation/HBA0011_roeland.xls

$logFileName = '/dc/'.$product[2].'-images/editorial/'.$batch_ref.'_'.$user[1].'.xls';


if (!file_exists($logFileName)) {
  $logFileHandle = fopen($logFileName, "w+") or die('unable to create logfile: '.$logFileName.'. Please check permissions');
  $headers = 'Feedback type'."\t".'Problem type'."\t".'Batch'."\t".'Reference Record'."\t".'Affected images'."\t".'Feedback summary'."\t".'Entered by'."\t".'Notes'."\n";
  fwrite($logFileHandle, $headers);
  fclose($logFileHandle);
  chmod($logFileName, 0777);
}


?>
