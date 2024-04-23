<?php
// full product name for display in title
$prod = 'Trench Journals and Unit Magazines of the First World War';

// directories lookup location
$directories_lookup = '/dc/trench-images/utils/directories_'.$user[1].'.txt';

include '../includes/config.php';

// directories.php -> dropdown display
$path_substr_begin = 17;
$path_substr_end = -4;

// directories.php -> typeahead details
// trim ammount for display
$path_trim = 20;

// directories.php -> typeahead trim replacement
$typeahead_pre = "/dc/trench-images/bl";

// images.php -> network path to images
$temp_path = explode('/', $current_path);
$sub_dir = explode('_', $temp_path[count($temp_path)-2]);
//$network = '/sd/web/images/trj/'.$sub_dir[0].'/'.$temp_path[count($temp_path)-2].'/jpeg/';
$network = $os->join('/sd/web/images/trj/', $sub_dir[0]);
$network = $os->join($network, $temp_path[count($temp_path)-2]);
$network = $os->join($network, '/jpeg/');

// images.php -> symlink path to images
$image_path = '/trench/images/'.$sub_dir[0].'/'.$temp_path[count($temp_path)-2].'/jpeg';
$image_path = $os->join('/trench/images/', $sub_dir[0]);
$image_path = $os->join($image_path, $temp_path[count($temp_path)-2]);
$image_path = $os->join($image_path, '/jpeg/');

// images.php -> multipliers
$multiplier = 4;
$coords_mtp = 9.2;

// xml_display.php -> xml_object and xml_edit
include '../includes/xml_select.php';

?>

