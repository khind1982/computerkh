<?php

header("Content-Type:application/json");

/*
function xml_character_encode($string, $trans='') {
  $trans=(is_array($trans)) ? $trans : get_html_translation_table(HTML_ENTITIES, ENT_QUOTES);
  foreach ($trans as $k=>$v) $trans[$k]= "&#".ord($k).";";
  return strtr($string, $trans);
}
*/

if (!empty($_GET['file'])) {
  $work_file = $_GET['file'];
  $file_backup = $work_file.'.bkp';
  copy($work_file, $file_backup) or die('could not copy file');
  chmod($file_backup,0777);

  $dom = new DOMDocument();
  $dom->load($work_file);
  $dom->getElementsByTagName('title')->item(0)->nodeValue = $_GET['title'];
  $dom->getElementsByTagName('author_name')->item(0)->nodeValue = $_GET['author_name'];
  $dom->getElementsByTagName('shelfmark')->item(0)->nodeValue = $_GET['shelfmark'];
  $dom->getElementsByTagName('subject')->item(0)->nodeValue = $_GET['subject'];
  $dom->getElementsByTagName('publisher_printer')->item(0)->nodeValue = $_GET['publisher_printer'];
  $dom->getElementsByTagName('size')->item(0)->nodeValue = $_GET['size'];
  $dom->getElementsByTagName('pagination')->item(0)->nodeValue = $_GET['pagination'];
  $dom->save($work_file);

  deliver_response(200, 'sucess', $work_file);
}
else {
  deliver_response(200, 'failed', 'Something went wrong. Please check');
}

function deliver_response($status, $status_message, $data) {
  header("HTTP/1.1 $status $status_message");

  $response['status'] = $status;
  $response['status_message'] = $status_message;
  $response['data'] = $data;

  $json_response = json_encode($response);

  echo $json_response;
}
?>
