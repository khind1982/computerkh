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
  $tags = $_GET['tag'];
  $split_tags = explode(',', $tags);
  $value = $_GET['value'];
  $split_values = explode('||', $value);

  $file_backup = $work_file.'.bkp';
  copy($work_file, $file_backup) or die('could not copy file');
  chmod($file_backup,0777);

  $dom = new DOMDocument();
  $dom->load($work_file);

  foreach ($split_tags as $i => $indiv_tag) {
    $dom->getElementsByTagName($indiv_tag)->item(0)->nodeValue = $split_values[$i];
  }

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
