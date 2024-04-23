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
$first_image = $os->join($network, $unique_image[0]);

$dimensions = getimagesize($first_image);
$image_width = $dimensions[0];
$image_height = $dimensions[1];

$APS_zone_tag = $dom->getElementsByTagName('APS_zone');
$zone_padding = 0;

foreach ($unique_image as $image) {
  $full_image = $os->join($image_path, $image);
  $width = round($image_width / $multiplier);
  $height = round($image_height / $multiplier);
  ?>
  <a href="<?php echo $full_image; ?>" target="_blank">
  <img style="position: absolute; left: <?php echo $zone_padding; ?>px; top: 0 px; width: <?php $width; ?>px; height: <?php echo $height; ?>px;" src="<?php echo $full_image; ?>" alt="<?php echo $full_image; ?>">
  </a>
  <?php
  foreach ($APS_zone_tag as $zone) {
    if ($product[2] === 'trench') {
      $image = substr_replace($image, '2', -1);
    }

    if ($zone->getElementsByTagName("APS_page_image")->item(0)->nodeValue == $image) {
      $zone_left = round($zone->getElementsByTagName("APS_ULX")->item(0)->nodeValue / $coords_mtp) + $zone_padding;
      $zone_top = round($zone->getElementsByTagName("APS_ULY")->item(0)->nodeValue / $coords_mtp);
      $zone_width = round(($zone->getElementsByTagName("APS_LRX")->item(0)->nodeValue / $coords_mtp) - ($zone->getElementsByTagName("APS_ULX")->item(0)->nodeValue / $coords_mtp));
      $zone_height = round(($zone->getElementsByTagName("APS_LRY")->item(0)->nodeValue / $coords_mtp) - ($zone->getElementsByTagName("APS_ULY")->item(0)->nodeValue / $coords_mtp));
      ?>
      <div style="position: absolute; color: #666600; border: 2px solid red; left: <?php echo $zone_left; ?>px; top: <?php echo $zone_top; ?>px; width: <?php echo $zone_width; ?>px;
      height: <?php echo $zone_height; ?>px;">
      </div>
      <?php
    }

  }
  $zone_padding = $zone_padding + $width;
  echo 'zone';

}

?>
