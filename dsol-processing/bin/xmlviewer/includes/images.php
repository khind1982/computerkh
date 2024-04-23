<?php

//echo 'Title: '.$APS_zone_pagenumber;
$img_tags = $dom->getElementsByTagName('APS_page_image');
$imgs = array();

foreach ($img_tags as $image_tag) {
    $image = $image_tag->nodeValue;
    if ($image[(strlen($image) - 1)] === '2') {
        $image = substr_replace($image, 'g', -1);
    }
    array_push($imgs, $image);
}

$unique_image = array_unique($imgs);

$dimensions = getimagesize($network.$unique_image[0]);
$image_width = $dimensions[0];
$image_height = $dimensions[1];

$APS_zone_tag = $dom->getElementsByTagName('APS_zone');
$zone_padding = 0;

foreach ($unique_image as $image) {

    echo '<a href="'.$image_path.'/'.$image.'" target="_blank">';
    echo '<img style="position: absolute; ';
    echo 'left: '.$zone_padding.'px; top: 0 px; ';
    echo 'width: '.$image_width / $multiplier.'px; ';
    echo 'height: '.$image_height / $multiplier.'px;"';
    echo 'src="'.$image_path.'/'.$image.'"';
    echo 'alt="'.$image_path.'/'.$image.'">';

    foreach ($APS_zone_tag as $zone) {
        if ($product[2] === 'trench') {
            $image = substr_replace($image, '2', -1);
        }

        if ($zone->getElementsByTagName("APS_page_image")->item(0)->nodeValue == $image) {
            echo '<div style="position: absolute; color: #666600; border: 2px solid red;';
            echo 'left: '.(round($zone->getElementsByTagName("APS_ULX")->item(0)->nodeValue / $coords_mtp) + $zone_padding).'px; ';
            echo 'top: '.round($zone->getElementsByTagName("APS_ULY")->item(0)->nodeValue / $coords_mtp).'px; ';
            echo 'width: '.round(($zone->getElementsByTagName("APS_LRX")->item(0)->nodeValue / $coords_mtp) - ($zone->getElementsByTagName("APS_ULX")->item(0)->nodeValue / $coords_mtp)).'px; ';
            echo 'height: '.round(($zone->getElementsByTagName("APS_LRY")->item(0)->nodeValue / $coords_mtp) - ($zone->getElementsByTagName("APS_ULY")->item(0)->nodeValue / $coords_mtp)).'px;">';
            echo '</div>';
        }

    }
    $zone_padding = ($zone_padding + ($image_width / $multiplier));
    echo '</a>';
}


?>
