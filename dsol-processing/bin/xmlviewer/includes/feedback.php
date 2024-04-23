<?php
$dropdown = array('', 'Article boundary error', 'Doctype incorrect', 'OCR error', 'Keying/Typographical error', 'Scanning error', 'Truncated text');
?>


 <div class="feedback">
  <div id="feedback-panel">
    <a id="feedback_button">Feedback</a>
    <form class="feedback-form" id="feedback-form">
      <input type="hidden" name="path" value="<?php echo $current_path; ?>">
      <input type="hidden" name="file" value="<?php echo $current_file; ?>">
      <label>Feedback type</label>
      <div class="form-inline">
        <div class="radio">
          <label>
            <input type="radio" value="Problem" name="feedback-type" checked>Problem
          </label>
        </div>
        <div class="radio">
          <label>
            <input type="radio" value="Query" name="feedback-type">Query
          </label>
        </div>
      </div>

      <div class="form-group">
      <label>Problem type</label>
        <select name="problem-type" class="form-control" name="feedback-type">
          <?php
          foreach ($dropdown as $item) : ?>
          <option><?php echo $item; ?></option>
          <?php
          endforeach;
          ?>
        </select>
      </div>

      <div class="form-group">
        <label>Batch reference</label>
        <input class="form-control" name="batch-reference" value="<?php echo $batch_ref; ?>">
      </div>
      <div class="form-group">
        <label>Record</label>
        <input class="form-control" name="record-id" value="<?php echo $current_file; ?>">
      </div>

      <div class="form-group">
        <label>Image reference</label>
        <?php
        foreach ($img_array as $k => $v) : ?>
          <div class="delete-group">
            <input class="delete-image" type="hidden" value="<?php echo $k; ?>">
            <button class="btn btn-link delete-btn" type="button"><?php echo $k; ?> <i class="fa fa-times"></i></button>
          </div>
        <?php
        endforeach;
        ?>
        <input name="delete-images-all" id="delete-images-all" type="hidden" value="">
      </div>

      <div class="form-group">
        <label>Feedback summary</label>
        <textarea class="form-control" name="feedback-summary" rows="3"></textarea>
      </div>

      <div class="form-group">
        <label>Entered by</label>
        <input class="form-control" name="user" value="<?php echo ucfirst($user[1]); ?>">
      </div>
      <label>Notes</label>
      <textarea class="form-control" name="notes" rows="3"></textarea>
      <input name="log_file" type="hidden" value="<?php echo $logFileName; ?>">
      <button type="submit" class="btn btn-default feedback-btn">Submit</button>
    </form>
  </div>
</div>
