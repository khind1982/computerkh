<?php

// full product name for display in title
$prod = 'Windows';

// directories lookup location
$directories_lookup = '../xml/directories_'.$user[1].'.txt';

include '../includes/config.php';

// directories.php -> dropdown display
$path_substr_begin = 21;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 22;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/wwd-images/master/";

// images.php -> network path to images
$network = str_replace("xml", "jpeg", $current_path);

// images.php -> symlink path to images
$the_path = explode('/', $network, 5);
$image_path = '/xml_viewer/images/'.$the_path[4];

// images.php -> multipliers
$multiplier = 7;
$coords_mtp = 7;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

?>

