<?php
include '../includes/xml_object_common.php';

$xml_data['docid'] = $dom->getElementsByTagName('docid')->item(0)->nodeValue;
$xml_data['supplement'] = $dom->getElementsByTagName('supplement')->item(0)->nodeValue;
$xml_data['series'] = $dom->getElementsByTagName('series')->item(0)->nodeValue;
$xml_data['volume'] = $dom->getElementsByTagName('volume')->item(0)->nodeValue;
$xml_data['issue'] = $dom->getElementsByTagName('issue')->item(0)->nodeValue;
$xml_data['numdate'] = $dom->getElementsByTagName('numdate')->item(0)->nodeValue;
$xml_data['originaldate'] = $dom->getElementsByTagName('originaldate')->item(0)->nodeValue;
$xml_data['doctype1'] = $dom->getElementsByTagName('doctype1')->item(0)->nodeValue;
$xml_data['doctype2'] = $dom->getElementsByTagName('doctype2')->item(0)->nodeValue;
$xml_data['section1'] = $dom->getElementsByTagName('section1')->item(0)->nodeValue;
$xml_data['section2'] = $dom->getElementsByTagName('section2')->item(0)->nodeValue;
$xml_data['section3'] = $dom->getElementsByTagName('section3')->item(0)->nodeValue;

$xml_data['role'] = $dom->getElementsByTagName('contributor')->item(0)->getAttribute('role');


// foreach($dom->getElementsByTagName('contributor')->attributes as $attribute ) {
//     if $attribute->name === 'role'{
//         $role_tag = $attribute->name;
//     }
// }



$title_tag = $dom->getElementsByTagName('title');
multiple('title', $title_tag, 'vogueitalia');

$abstract_tag = $dom->getElementsByTagName('abstract');
multiple('abstract', $abstract_tag, 'vogueitalia');

$subhead_tag = $dom->getElementsByTagName('subhead');
multiple('subhead', $subhead_tag, 'vogueitalia');

$company_tag = $dom->getElementsByTagName('company');
multiple('company', $company_tag, 'vogueitalia');

$product_tag = $dom->getElementsByTagName('product');
multiple('product', $product_tag, 'vogueitalia');


$feature_tag = $dom->getElementsByTagName('feature');
multiple('feature', $feature_tag, 'vogueitalia');

$credit_tag = $dom->getElementsByTagName('credit');
multiple('credit', $credit_tag, 'vogueitalia');

$caption_tag = $dom->getElementsByTagName('caption');
multiple('caption', $caption_tag, 'vogueitalia');

$language_tag = $dom->getElementsByTagName('language');
multiple('language', $language_tag, 'vogueitalia');

$contributor_tag = $dom->getElementsByTagName('originalform');
multiple('originalform', $contributor_tag, 'vogueitalia');

$contributor_tag_standard = $dom->getElementsByTagName('standardform');
multiple('standardform', $contributor_tag_standard, 'vogueitalia');

$display_pagenumber_tag = $dom->getElementsByTagName('display_pagenumber');
multiple('display_pagenumber', $display_pagenumber_tag, 'vogueitalia');


$contributor_tag = $dom->getElementsByTagName('originalform');
multiple('originalform', $contributor_tag, 'vogueitalia');


?>
