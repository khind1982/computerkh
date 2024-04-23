<?php

$dom = new DOMDocument();
$dom->load($workfile);
$file_backup = $workfile.'.bkp';

copy($workfile, $file_backup) or die('Could not copy '.$workfile.' to '.$file_backup);
chmod($file_backup,0777) or die('Could not chmod 777 '.$file_backup);

foreach ($_POST as $id=>$value) {

    if ($id === 'page_count') {
        $replaceNode = $dom->getElementsByTagName("DISS_description")->item(0);
        $replaceNode->setAttribute("page_count", $value);

    }
    else {
        $dom->getElementsByTagName($id)->item(0)->nodeValue=$value;
    }

}

$dom->encoding = 'UTF-8';
$str = $dom->saveXML();

$output_file = fopen($workfile, 'w') or die("can't open write file");
fwrite($output_file, $str) or die("can't write to output file");
fclose($output_file);
chmod($output_file,0777);

?>
