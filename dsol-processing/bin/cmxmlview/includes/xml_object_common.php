<?php

$dom = new DOMDocument();

if ($product[2] === 'vogueitalia') {
  //$dom->load($workfile);
  //$dom->loadXML($workfile, 'HTML-ENTITIES', 'UTF-8');
  $file_contents = file_get_contents($workfile);
  //echo gettype($file_contents).'<br>';
  //$content = utf8_encode($file_contents);
  $content = iconv('UTF-8', 'UTF-8', $file_contents);
  //echo $content.'<br>';

  //echo gettype($content).'<br>';
  $dom->loadXML($content);
  //$dom->load($workfile);

  //$dom->loadXML($workfile, 'HTML-ENTITIES', 'UTF-8');

}
else {
  $dom->load($workfile);
}
$xml_data = array();
// echo $product[2]; //vogueitalia
function multiple($name, $element_tag, $product_name) {
  global $xml_data;
  //global $product[2];
  foreach ($element_tag as $j => $element) {
    $tag = $name.$j;
    if ($product_name === 'vogueitalia') {
      //echo $product_name;
      //echo gettype($element->nodeValue);
      $xml_value = $element->nodeValue;
      $xml_data[$tag] = $element->nodeValue;
    }
    else {
      $xml_data[$tag] = htmlentities($element->nodeValue);
    }
  }
}

?>
