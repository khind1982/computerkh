<div id="feedback_error" style="display: none; border:1px solid; border-color: black; background: white; border-raduis: 5px;">
  this went wrong, please fix it!
</div>
  <?php
  $current_directory = $_POST['path'];
  $tag = $_POST['tag'];
  $tags = array();
  if (strpos($tag, ',') !== FALSE) {
    $tags_split = explode(',', $tag);
    foreach ($tags_split as $t) {
      array_push($tags, trim($t));
    }
  }
  else {
    array_push($tags, trim($tag));
  }
  #$raw_files = scandir($current_directory);
  $root_path = new RecursiveDirectoryIterator($current_directory);
  $raw_files = new RecursiveIteratorIterator($root_path,RecursiveIteratorIterator::SELF_FIRST);

  $files = array();

  foreach ($raw_files as $file) {
    if (substr($file, -4) === '.xml') {
      array_push($files, $file);
    }
  }
  sort($files);

  $product = preg_replace('/[0-9]+/', '', substr(basename($files[0]), 0, 6));
  $p1 = explode('/', $current_directory);
  $psplit = explode('-', $p1[2]);
  if ($psplit[0] == 'wmb') {
    $product = $psplit[0];
  }
  $path_parts = pathinfo($files[0]);
  $root = $path_parts['dirname'];
?>


<div>
  <table id="myTable" class="tablesorter-blue">
    <thead>
      <tr>
        <th></th>
        <th>
          Title
        <?php
        foreach ($tags as $tag) : ?>
        <th>
          <?php echo $tag; ?>
          <span style="display: none;" id="<?php echo $tag.'_edit_all'; ?>">
          </span>
        </th>
        <?php
        endforeach;
        ?>
        <th></th>
      </tr>
    </thead>
    <tbody>
    <?php
    $i = 0;
    foreach ($files as $f) :
      $dom = new DOMDocument();
      $dom->load($f);
      ?>
      <tr>
        <form>
          <td><?php $i++; echo $i; ?></td>
          <td>
            <input class="doc" type="hidden" name="file" value="<?php echo $f; ?>">
            <?php
			  if (strtolower($product) == 'via') {
				  $prod = 'vogueitalia';
			  }
			  else {
				  $prod = strtolower($product);
			  }
			?>
            <a href="http://dsol.private.chadwyck.co.uk/xmlviewer/<?php echo $prod; ?>/index_<?php echo strtolower($product); ?>.php?file=<?php echo basename($f); ?>&path=<?php echo dirname($f); ?>" target="_blank">
            <?php echo basename($f); ?>
            </a>
          </td>
          <?php
          $save_tags = array();
          foreach ($tags as $tag) :

          ?>
          <td>
            <?php
            $value = $dom->getElementsByTagName($tag)->item(0)->nodeValue;
            if (isset($value)):
            array_push($save_tags, $tag);
            ?>
            <span style="display: none;"><?php echo htmlDisplay($value); ?></span>
            <input class="<?php echo $tag; ?>_class" id="<?php echo $tag.$i; ?>" style="width:95%; border:none;" value="<?php echo htmlDisplay($value); ?>">

            <span style="float: right;">
              <a href="#" onclick="showFeedback(<?php echo $i.', \''.$tag.'\', \''.$f.'\''; ?>); return false;">
                <i id="<?php echo $tag.$i.'icon'; ?>" style="color: DodgerBlue;" class="fa fa-exclamation-circle"></i>
              </a>
            </span>
            <?php
            endif;
            ?>
          </td>
          <?php
          endforeach;
          ?>
          <td>
            <input name="save" type="submit" id="save<?php echo $i ?>" value="save" onclick="saveData(<?php echo $i.', \''.$f.'\', \''.join(',', $save_tags).'\''; ?>); return false;">
          </td>
        </form>
      </tr>
      <?php
  endforeach;
?>

    </tbody>
  </table>
</div>
<script>
  var usedTags = '<?php print $_POST['tag']; ?>';
  var fullPath = '<?php print $_POST['path']; ?>';
</script>
