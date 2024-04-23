<?php
$file_backup = $workfile.'.bkp';

copy($workfile, $file_backup) or die('Could not copy '.$workfile.' to '.$file_backup);
chmod($file_backup,0777) or die('Could not chmod 777 '.$file_backup);

//function html($string) {
//  return htmlspecialchars($string, REPLACE_FLAGS, CHARSET);
//}

foreach ($_POST as $id=>$value) {
  if (strcspn($id, '0123456789') != strlen($id)) {
    preg_match_all('/^([^\d]+)(\d+)/', $id, $match);
    $tag = $match[1][0];
    $pos = $match[2][0];
    // $APS_abstract = $dom->getElementsByTagName('abstract')->item(0)->nodeValue=$_POST["abstract"];
    $dom->getElementsByTagName($tag)->item($pos)->nodeValue=$value;
    $xml_data[$id] = $value;
    // echo 'Tag: '.$tag.'. Position: '.$pos.'. Value: '.$value.'<br/>';
  }
}

$dom->encoding = 'UTF-8';
$str = $dom->saveXML();

$output_file = fopen($workfile, 'w') or die("can't open write file");
fwrite($output_file, $str) or die("can't write to output file");
fclose($output_file);
chmod($output_file,0777);

?>
