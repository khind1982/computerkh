<?php

$dom = new DOMDocument();
$dom->load($workfile);

$file_backup = $workfile.'.bkp';

copy($workfile, $file_backup) or die('<br>Could not copy '.$workfile.' to '.$file_backup.' dammit!!!');
chmod($file_backup,0777) or die('Could not cchmod 777 '.$file_backup);

if ($product === 'eima') {
    $CHARSET = 'ISO-8859-1';
}
elseif ($product === 'aaa' || $product === 'trench' || $product === 'wwd' || $product === 'vogueitalia') {
    $CHARSET = 'UTF-8';
}
define('REPLACE_FLAGS', ENT_COMPAT | ENT_XHTML);

function html($string) {
    return htmlspecialchars($string, REPLACE_FLAGS, CHARSET);
}

foreach ($_POST as $id=>$value) {
    if (strcspn($id, '0123456789') != strlen($id)) {
        preg_match_all('/^([^\d]+)(\d+)/', $id, $match);
        $tag = $match[1][0];
        $pos = $match[2][0];
        // $APS_abstract = $dom->getElementsByTagName('abstract')->item(0)->nodeValue=$_POST["abstract"];
        // $dom->getElementsByTagName($tag)->item($pos)->nodeValue=mb_convert_encoding($value, $CHARSET);
        $dom->getElementsByTagName($tag)->item($pos)->nodeValue = html($value);
        $xml_data[$id] = htmlentities($value);
        // echo 'Tag: '.$tag.'. Position: '.$pos.'. Value: '.$value.'<br/>';
    }
}

$dom->encoding = $CHARSET;
$str = $dom->saveXML();

$output_file = fopen($workfile, 'w') or die("can't open write file");
fwrite($output_file, $str) or die("can't write to output file");
fclose($output_file);
chmod($output_file,0777);

/*
$elements_array = array(
    "title0" => "APS_title",
    "subhead0" => "APS_subhead",
    "author0" => "APS_author",
    "abstract0" => "APS_abstract"
    );

foreach ($elements_array as $element => $xml_tag) {
    if (!empty($_POST[$element])) {
        $APS_element_tag = $dom->getElementsByTagName($xml_tag);
        foreach ($APS_element_tag as $k => $v) {
            $new_item_id = substr($element, 0, -1).$k;
            $v->nodeValue = html($_POST[$new_item_id]);
        }
    }
}
*/

?>
