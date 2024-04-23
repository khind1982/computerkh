<?php

$zone_tag = $dom->getElementsByTagName('zone');

$prev_img = $zone_tag->item(0)->getElementsByTagName('page_ref')->item(0)->nodeValue;

$zones_array = array();

$img_array = array();
foreach ($zone_tag as $zone) {
  $img = $zone->getElementsByTagName('page_ref')->item(0)->nodeValue;
  if ($img != $prev_img) {
    $img_array[$prev_img] = $zones_array;
    $prev_img = $img;
    $zones_array = array();
  }
  $zone_array = array();
  $zonecoords = $zone->getElementsByTagName('zonecoords');
  $zone_array['uly'] = $zonecoords->item(0)->getAttribute('uly');
  $zone_array['ulx'] = $zonecoords->item(0)->getAttribute('ulx');
  $zone_array['lry'] = $zonecoords->item(0)->getAttribute('lry');
  $zone_array['lrx'] = $zonecoords->item(0)->getAttribute('lrx');
  $zones_array[] = $zone_array;
}
$img_array[$img] = $zones_array;

// grab the first image in that array and use it to determine the dimensions

$first_image = key($img_array);

$first_image = $os->join($network, $first_image);
$dimensions = getimagesize($first_image);
$image_width = $dimensions[0];
$image_height = $dimensions[1];
// display the image and use the zone coordinates to display the zones
// use $zone_padding to make sure images are displayed next to each other

$zone_padding = 0;
foreach ($img_array as $image => $zones) {
  
  echo '<a href="'.$os->join($image_path, $image).'" target="_blank">';
  echo '<img style="position: absolute; ';
  echo 'left: '.$zone_padding.'px; top: 0 px; ';
  echo 'width: '.round($image_width / $multiplier).'px; ';
  echo 'height: '.round($image_height / $multiplier).'px;"';
  echo 'src="'.$os->join($image_path, $image).'"';
  echo 'alt="'.$os->join($image_path, $image).'">';

  foreach ($zones as $zone) {
      echo '<div style="position: absolute; color: #666600; border: 1px solid red;';
      echo 'left: '.(round($zone['ulx'] / $coords_mtp) + $zone_padding).'px; ';
      echo 'top: '.round($zone['uly'] / $coords_mtp).'px; ';
      echo 'width: '.round(($zone['lrx'] / $coords_mtp) - ($zone['ulx'] / $coords_mtp)).'px; ';
      echo 'height: '.round(($zone['lry'] / $coords_mtp) - ($zone['uly'] / $coords_mtp)).'px;">';
      echo '</div>';
  }
  $zone_padding = ($zone_padding + ($image_width / $multiplier));
  echo '</a>';
}

?>
