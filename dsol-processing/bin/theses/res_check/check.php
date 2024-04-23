<?php
header('Content-Type: text/event-stream');
header('Cache-Control: no-cache');

$lines = file('/opt/DSol/apache2/htdocs/theses/res_check/config.txt') or die('cannot open file');
$input_directory = trim($lines[0]);
$image_type = trim($lines[1]);
$image_resolution = trim($lines[2]);
$directory_type = trim($lines[3]);

if ($directory_type == 'multi') {
    $root_path = new RecursiveDirectoryIterator($input_directory);
    $iterator = new RecursiveIteratorIterator($root_path,RecursiveIteratorIterator::SELF_FIRST);
    foreach ($iterator as $fileObject) {
        $files_raw[] = $fileObject;
    }
}
else {
    $files_raw = array();
    $files = scandir($input_directory);
    foreach ($files as $f) {
        $full_image = preg_replace('#/+#','/',join('/', array($input_directory, $f)));
        array_push($files_raw, $full_image);
    }
}

$files_tif = array();
foreach ($files_raw as $file) {
    if (strtolower(substr($file, -3)) === $image_type) {
        array_push($files_tif, $file);
    }
}

sort($files_tif);

$failed = 0;
$passed = 0;

$logFile = '/opt/DSol/apache2/htdocs/theses/res_check/'.date("ymdHis").'.txt';
$fh = fopen($logFile, 'w');

foreach ($files_tif as $i => $image) {
    $data = array();
    $cmd = '/usr/local/versions/ImageMagick-6.7.2/bin/identify -format "%x x %y" '.$image;
    @exec(escapeshellcmd($cmd), $data);
    $returned = explode(' ', $data[0]);
    if (($i % 50) == 0) {
        echo "data: Checking image: ".$i.': '.$image.' '.$returned[0].PHP_EOL;
        echo PHP_EOL;
        flush();
    }
    if ($returned[0] != $image_resolution || $returned[3] != $image_resolution) {
        $failed++;
        $log_entry = $image.' '.$returned[0].'x'.$returned[3]."\n";
        fwrite($fh, $log_entry);
    }
    else {
        $passed++;
    }
}

fclose($fh);
chmod($logFile,0777);

echo 'data: 404'.PHP_EOL;
echo PHP_EOL;
flush();

if ($failed > 0) {
    $log_data = 'failed:'.$failed."\n";
}
else {
    $log_data = 'failed:0'."\n";
}
if ($passed > 0) {
    $log_data .= 'passed:'.$passed."\n";
}
else {
    $log_data .= 'passed:0'."\n";
}

$log_data .= file_get_contents($logFile);
file_put_contents($logFile, $log_data);

$page = 'results.php';
$sec = "0";
header("Refresh: $sec; url=$page");

?>
