<?php

// full product name for display in title
$prod = 'Theses and Index';

// directories lookup location
$directories_lookup = '/dc/wma-images/Incoming/Ninestars/Samples/directories_'.$user[1].'.txt';

include '../includes/config.php';
///dc/wma-images/Incoming/Ninestars/Samples/19820601/19820601/01/xml/
// directories.php -> dropdown display
$path_substr_begin = 44;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 44;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/wma-images/Incoming/Ninestars/Samples";

// images.php -> network path to images
$network = str_replace("xml", "images", $current_path);

// images.php -> symlink path to images
$image_path = '/xmlviewer/wma/images/'.substr($current_path, 42, -4).'images';

// images.php -> multipliers
$multiplier = 5.5;
$coords_mtp = 5.5;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

?>
