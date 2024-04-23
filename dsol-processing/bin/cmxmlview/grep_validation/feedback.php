<!--
Feedback type
Problem type
Batch Reference
Record/image reference
Feedback summary
Entered by
Notes
Rejectable Offence/Action
-->

 <div class="feedback">
  <div id="feedback-panel">
    <form class="feedback-form" id="feedback-form">
      <input type="hidden" id="feedback-file" value="">
      <div class="form-group">
        <label>Problem type</label>
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
      </div>
      <div class="form-group">
        <label>Problem type</label>
        <input class="form-control" name="record-id" id="feedback-record-id" value="">
      </div>

      <div class="form-group">
        <label>Batch reference</label>
        <input class="form-control" name="batch-reference" id="feedback-batch-reference" value="">
      </div>
      <div class="form-group">
        <label>Record</label>
        <input class="form-control" name="record" id="feedback-record" value="">
      </div>

      <div class="form-group">
        <label>Feedback summary</label>
        <textarea class="form-control" name="feedback-summary" id="feedback-summary" rows="3"></textarea>
      </div>

      <div class="form-group">
        <label>Entered by</label>
        <input class="form-control" name="feedback-user" id="feedback-user" value="">
      </div>
      <div class="form-group">
        <label>Notes</label>
        <textarea class="form-control" name="notes" name="feedback-notes" id="feedback-notes" rows="3"></textarea>
      </div>
      <div class="form-group">
        <label>Rejectable Offence/Action</label>
        <textarea class="form-control" name="notes" name="feedback-offence" id="feedback-offence" rows="3"></textarea>
      </div>
      <input name="icon_id_for_colour" id="icon_id_for_colour" type="hidden" value="">
      <button type="submit" onclick="submitFeedback(); return false;" class="btn btn-default feedback-btn">Submit</button>
    </form>
  </div>
</div>
