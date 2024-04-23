<?php

// full product name for display in title
$prod = 'Arts and Architecture Archive';

// directories lookup location
$directories_lookup = '/dc/aaa-images/incoming/directories_'.$user[1].'.txt';

include '../includes/config.php';

// directories.php -> dropdown display
$path_substr_begin = 23;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 24;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/aaa-images/incoming/";

// images.php -> network path to images
$network = str_replace("xml", "images", $current_path);

// images.php -> symlink path to images
//$image_path = '/aaa'.substr($current_path, 14, -4).'images';
$image_path = $os->join('/aaa', substr($current_path, 14, -4));
$image_path = $os->join($image_path, 'images');


// images.php -> multipliers
$multiplier = 5.5;
$coords_mtp = 5.5;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

?>
