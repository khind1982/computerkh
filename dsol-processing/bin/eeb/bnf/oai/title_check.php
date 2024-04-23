<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8">
<head>
  <title>Validation</title>
  <link href="http://dsol.private.chadwyck.co.uk/includes/css/font-awesome.css" rel="stylesheet" type="text/css">
  <!-- custom css location -->
  <link href="./includes/custom_title.css" rel="stylesheet" type="text/css">
</head>

<body style="display: none;">

  <?php
  $today = '/dc/eurobo/scanlists/Scanlist_essentials/extra/'.date("YmdH").'title_check.txt';
  // $METs_dir = $_GET['mets_dir'];
  $METs_dir = '/dc/eurobo/pre-handover/nov15/';
  //echo $METs_dir.'<br>';
  $METS_files = scandir($METs_dir);


  if (!file_exists($today)) {
    foreach ($METS_files as $METS_file) {
      if (substr($METS_file, -4) == '.xml') {
        $full_path = join('/', array(rtrim($METs_dir, '/'), $METS_file));
        $dom = new DOMDocument();
        $dom->load($full_path);
        $current_title = $dom->getElementsByTagName('title')->item(0)->nodeValue;
        $data[$full_path] = $current_title;
      }
    }
    $fp = fopen($today, 'w') or die('could not write file');
    foreach ($data as $k => $v) {
      $line = $k.'|'.$v."\n";
      fwrite($fp, $line);
    }
    fclose($fp);
  }
  else {
    $lines = file($today);
    foreach ($lines as $line) {
      $kv = explode('|', $line);
      $data[$kv[0]] = trim($kv[1]);
    }
  }

function makecoffee($field, $order = 'asc') {
  if ($order == 'asc') {
    
  }
  else {
    
  }
    return "Making a cup of $type.\n";
}


  $rtitles = '';
  $rfiles = '';
  if (isset($_GET['sort'])) {
    if ($_GET['sort'] == 'titles') {
      asort($data);
      $rtitles = 'yes';
    }
    else if ($_GET['sort'] == 'rtitles') {
      arsort($data);
      $rtitles = 'yes';
    }
    else if ($_GET['sort'] == 'rfiles') {
      krsort($data);
      $rfiles = 'yes';
    }
    else {
      ksort($data);
      $rfiles = 'yes';
    }
  }
?>

<div class="CSSTable" >
  <table>
    <tr>
      <th class="left-nums"></th>
      <th class="source-data"><a href="title_check.php?sort=files"><i class="fa fa-sort-asc"></i></a>/<a href="title_check.php?sort=rfiles"><i class="fa fa-sort-desc"></i></a></th>
      <th><a href="title_check.php?sort=titles"><i class="fa fa-sort-asc"></i></a> / <a href="title_check.php?sort=rtitles"><i class="fa fa-sort-desc"></i></a></th>
      <th class="saved-copied"></th>
      <th class="saved-copied"></th>
    </tr>

  <?php

    $i = 0;
    foreach ($data as $f => $t) : ?>
      <tr>
        <form>
          <td class="left-nums"><?php $i++; echo $i; ?></td>
          <td class="source-data">
            <a href="file://localhost/<?php echo $f; ?>" class="link-decoration" title="<?php echo $f; ?>"><i class="fa fa-file-code-o"></i></a>
            <input type="hidden" name="file" id="file<?php echo $i; ?>" value="<?php echo $f; ?>">
          </td>
          <td>
            <input name="title" id="title<?php echo $i; ?>" value="<?php echo str_replace(array('"',"'", '<', '>'), array('&#34;', '&#39;', '&#60;', '&#62;'), $t); ?>">
          </td>
          <td class="saved-copied">
            <input type="submit" value="copy" id="copy-down<?php echo $i; ?>" onclick="copyDown(<?php echo $i; ?>); return false;">
          </td>
          <td class="saved-copied">
            <input name="save" type="submit" id="save-button<?php echo $i; ?>" value="save" onclick="saveData(<?php echo $i; ?>); return false;">
          </td>
        </form>
      </tr>

      <?php
    endforeach;
    ?>
    </table>
  </div>
  <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.js"></script>
  <script src="./includes/custom_title.js"></script>

</body>
</html>
