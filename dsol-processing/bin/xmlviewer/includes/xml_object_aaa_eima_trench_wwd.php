<?php
include '../includes/xml_object_common.php';

$APS_article_tag = $dom->getElementsByTagName('APS_article');
$xml_data['pmid'] = $APS_article_tag->item(0)->getAttribute('pmid');
$xml_data['type'] = $APS_article_tag->item(0)->getAttribute('type');
$xml_data['issue'] = $dom->getElementsByTagName('APS_issue')->item(0)->nodeValue;
$xml_data['volume'] = $dom->getElementsByTagName('APS_volume')->item(0)->nodeValue;
$xml_data['date_8601'] = $dom->getElementsByTagName('APS_date_8601')->item(0)->nodeValue;
$xml_data['printed_date'] = $dom->getElementsByTagName('APS_printed_date')->item(0)->nodeValue;

$zone_imagetype_tag = $dom->getElementsByTagName('APS_zone_imagetype');
multiple('zone_imagetype',$zone_imagetype_tag);

$author_tag = $dom->getElementsByTagName('APS_author');
multiple('APS_author', $author_tag);

$feature_tag = $dom->getElementsByTagName('APS_feature');
multiple('APS_feature', $feature_tag);

$title_tag = $dom->getElementsByTagName('APS_title');
multiple('APS_title', $title_tag);

$subhead_tag = $dom->getElementsByTagName('APS_subhead');
multiple('APS_subhead', $subhead_tag);

$abstract_tag = $dom->getElementsByTagName('APS_abstract');
multiple('APS_abstract', $abstract_tag);
?>
