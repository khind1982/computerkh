<?php

header("Content-Type:application/json");

if (!empty($_GET['user'])) {
  $logFileHandle = fopen($_GET['log_file'], "a");
  $data = $_GET['feedback-type']."\t".$_GET['problem-type']."\t".$_GET['batch-reference']."\t".$_GET['record-id']."\t".$_GET['delete-images-all']."\t".$_GET['feedback-summary']."\t".$_GET['user']."\t".$_GET['notes']."\n";
  fwrite($logFileHandle, $data);
  fclose($logFileHandle);

  deliver_response(200, 'sucess', $data);
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
