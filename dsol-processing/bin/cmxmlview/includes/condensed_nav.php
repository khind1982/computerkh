<?php

// This module needs $files as an array of files and $current_file as the current file.
// This module will return a filtered list called $navi_list.

$navi_list = array();
$lenght = count($files);
$current_item_position = array_search($current_file, $files);
$limit = 13;
$pos = ($current_item_position + 1);


function future($current) {
    global $files;
    if (count($files) > ($current + 25)) {
        return $current + 24;
    }
    else {
        return $current;
    }
}

function past($current) {
    global $files;
    if ($current - 25 > 0) {
        return $current - 24;
    }
    else {
        return $current;
    }
}

if (count($files) < $limit) {
    $navi_list = $files;
}
else {

    array_push($navi_list, $files[0]);

    if (($pos <= ($lenght - 1) && $pos >= 1) && ($pos >= 1 && $pos <= 6)) {
        for ($i=0; $i < 10; $i++) {
            array_push($navi_list, $files[($i+1)]);
        }
        array_push($navi_list, $files[future(11)]);
    }
    elseif (($pos <= $lenght && $pos >= 3) && ($pos <= $lenght && $pos >= ($lenght - 6))) {
        array_push($navi_list, $files[past(($pos  - 6))]);
        for ($i=0; $i < 10; $i++) {
            array_push($navi_list, $files[((($lenght - 1) - 10) + $i)]);
        }
    }
    else {
        array_push($navi_list, $files[past(($pos  - 6))]);
        array_push($navi_list, $files[($pos - 5)]);
        array_push($navi_list, $files[($pos - 4)]);
        array_push($navi_list, $files[($pos - 3)]);
        array_push($navi_list, $files[($pos - 2)]);
        array_push($navi_list, $files[($pos - 1)]);
        array_push($navi_list, $files[$pos]);
        array_push($navi_list, $files[($pos + 1)]);
        array_push($navi_list, $files[($pos + 2)]);
        array_push($navi_list, $files[($pos + 3)]);
        array_push($navi_list, $files[future(($pos + 4))]);
    }
    array_push($navi_list, $files[($lenght - 1)]);
}
?>
