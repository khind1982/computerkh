<?php


// full product name for display in title
$prod = 'Women\'s Magazine Archive';

// directories lookup location
// ls -dl /dc/aaa-images/incoming/*/*/*/
// /dc/wmb-images/incoming/directories_wmb.txt
$directories_lookup = '/dc/wmb-images/editorial/directories_'.$user[1].'.txt';

include '../includes/config.php';
///dc/wmb-images/Incoming/Ninestars/Samples/19820601/19820601/01/xml/
// directories.php -> dropdown display
$path_substr_begin = 24;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 24;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/wmb-images/editorial/";

// images.php -> network path to images
$network = str_replace("xml", "images", $current_path);

// images.php -> symlink path to images
// /xmlviewer/wmb/images/Resend3_wmb0003/wmb000001/200000501/20000501/01images/
$image_path = $os->join('/xmlviewer/wmb/images/', substr($current_path, 24, -4));
$image_path = $os->join($image_path, 'images');

//$image_path = '/xmlviewer/wmb/images/'.substr($current_path, 24, -4).'images';

// images.php -> multipliers
$multiplier = 5.5;
$coords_mtp = 5.5;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

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
