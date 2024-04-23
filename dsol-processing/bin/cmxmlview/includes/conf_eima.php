<?php
// full product name for display in title
$prod = 'Entertainment Industry Magazine Archive';

// directories lookup location
$directories_lookup = '/dc/popcult-images/directories_popcult_'.$user[1].'.txt';

include '../includes/config.php';

// directories.php -> dropdown display
$path_substr_begin = 26;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 26;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/popcult-images/backup/";

// images.php -> network path to images
// $network = $current_path.'Page/';
$network = $os->join($current_path, 'Page');

// images.php -> symlink path to images
// $image_path = '/eima/backup/'.substr($network, 26);
$image_path = $os->join('/eima/backup/', substr($network, 26));

// images.php -> multipliers
$multiplier = 5.5;
$coords_mtp = 5.5;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

?>
