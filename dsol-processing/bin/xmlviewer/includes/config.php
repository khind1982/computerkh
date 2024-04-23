<?php
if ($_GET['path']) {
  $current_path = $_GET['path'];
}
else if ($_POST['path']) {
  $current_path = $_POST['path'];
}
else {
  $lines = file($directories_lookup);
  $pieces = explode("|", $lines[0]);
  $current_path = $pieces[0];
}

if ($prod === 'Windows') {
  $current_path = substr($current_path, 21);
  $current_path = '../xml'.$current_path;
  // echo $current_path;
}

if ($_GET['file']) {
  $current_file = $_GET['file'];
}
else if ($_POST['file']) {
  $current_file = $_POST['file'];
  }
else {
  $files = array_diff(scandir($current_path), array('..', '.'));
  foreach ($files as $file) {
    if (substr($file, -3) === 'xml') {
      $current_file = $file;
      break;
    }
  }
}

$products = array('aaa', 'bpc', 'bpd', 'eima', 'hba', 'wma', 'wwd');



//$workfile = $current_path.$current_file;
$workfile = $os->join($current_path, $current_file);


  // logfile
if (isset($_POST["MM_edit"])) {
  $edit = 'true';
}
else {
  $edit = 'false';

}
if ($prod != 'Windows') {
  $log_entry = date("ymd")."\t".$product[2]."\t".$user[1]."\t".$edit."\t".$workfile."\n";
  $logFile = "/home/rschumac/work/xmlviewer/viewer_log.txt";
  $fh = fopen($logFile, 'a');
  fwrite($fh, $log_entry);
  fclose($fh);
}
?>
