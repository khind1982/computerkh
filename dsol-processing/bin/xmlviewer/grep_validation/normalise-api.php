<?php

header("Content-Type:application/json");

if (!empty($_GET['fullPath'])) {
  $root_path = new RecursiveDirectoryIterator($_GET['fullPath']);
  $raw_files = new RecursiveIteratorIterator($root_path,RecursiveIteratorIterator::SELF_FIRST);

  foreach ($raw_files as $work_file) {
    if (substr($work_file, -4) === '.xml') {
      $file_backup = $work_file.'.bkp';
      copy($work_file, $file_backup) or die('could not copy file');
      chmod($file_backup,0777);

      $dom = new DOMDocument();
      $dom->load($work_file);
      $dom->getElementsByTagName($_GET['editTag'])->item(0)->nodeValue = $_GET['newValue'];
      $dom->save($work_file);
    }
  }

  deliver_response(200, 'sucess', 'Changes saved');
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
