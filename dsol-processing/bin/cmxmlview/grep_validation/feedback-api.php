<?php

header("Content-Type:application/json");

if (!empty($_GET['file'])) {

  $myFile = $_GET['file'];
  $fh = fopen($myFile, 'a');
  if ($fh == false) { 
    $return_message = 'Could not open (or create) ' . $myFile . '. Check directory permissions';
    deliver_response(201, 'failed', $return_message);
  }
  else {
    $stringData = $_GET['type']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['tag']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['batch']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['record']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['summary']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['user']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['notes']."\t";
    fwrite($fh, $stringData);
    $stringData = $_GET['offence']."\n";
    fwrite($fh, $stringData);
    fclose($fh);
    chmod($myFile, 0777);
    deliver_response(200, 'sucess', $myFile);
  }
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
