<?php

if (isset($_POST["MM_edit"])) {
  include $xml_object;
  include $xml_edit;
}
else {
  include $xml_object;
}
?>

<form class="form-horizontal" enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">

<table class="table table-condensed">
  <tr>
    <td><?php include '../includes/navigation.php'; ?></td>
    <td>
      <?php
      if (isset($_POST["MM_edit"])) : ?>
        <a class="btn btn-success disabled">Saved!</a>
        <?php
      else :
        ?>
        <div class="pull-right">
        <button type="submit" class="btn btn-primary" name="MM_edit" value="Save">Save</button>
        </div>
        <?php
      endif;
      ?>
    </td>
  </tr>
</table>

<table class="table table-condensed">
<?php
$editable = array('doctype', 'title', 'abstract', 'credit', 'standardform', 'originalform', 'subhead', 'APS_author', 'APS_feature', 'APS_title', 'APS_subhead', 'APS_abstract', 'section', 'caption');
$display_subs = array('pmid' => 'PQID');
foreach ($xml_data as $key => $val) :
  if (!empty($val)) : ?>
    <tr>
      <div class="form-group">
        <td>
          <label for="<?php echo $key; ?>" class="control-label col-md-2">
            <?php
            if (array_key_exists($key, $display_subs)) {
              echo $display_subs[$key];
            }
            elseif (substr($key, 0, 4) === "APS_") {
              echo preg_replace("/\d+$/", "",(substr($key, 4)));
            }
            else {
              echo preg_replace("/\d+$/", "", $key);
            }
            ?>
          </label>
        </td>
        <td>
         <?php
          if (in_array(preg_replace("/\d+$/","",$key), $editable)) :
            if (strlen($val) <= 29) : ?>
              <div class="col-md-10">
                <input type="text" class="form-control" id="<?php echo $key; ?>" name="<?php echo $key; ?>" value="<?php echo $val; ?>">
              </div>
              <?php
            else: ?>
              <textarea class="form-control" rows="<?php echo floor(strlen($val) / 35); ?>" name="<?php echo $key; ?>" id="<?php echo $key; ?>"><?php echo $val; ?></textarea>
            <?php
            endif;
          else: ?>
          <div class="col-md-10">
            <p class="form-control-static">
            <?php echo $val; ?>
            </p>
          </div>
          <?php
          endif; ?>
        </td>
      </div>
    </tr>
  <?php
  endif;
endforeach;
?>

</table>

<input type="hidden" name="path" value="<?php echo $current_path; ?>">
<input type="hidden" name="file" value="<?php echo $current_file; ?>">
</form>


