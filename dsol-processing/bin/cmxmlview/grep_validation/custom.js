$(document).ready(function () {

  if (typeof usedTags != 'undefined') {

    var totalDocs = document.getElementsByClassName("doc").length;
    var tagsArray = [];
    if (usedTags.indexOf(',') > -1) {
      var singleTags = usedTags.split(',');
      for (var i = 0; i < singleTags.length; i++) {
        tagsArray.push(singleTags[i].trim());
      }
    }
    else {
      tagsArray.push(usedTags);
    }
    console.log(fullPath);
    for (var i = 0; i < tagsArray.length; i++) {
      var countTagName = tagsArray[i] + '_class';
      var tagCount = document.getElementsByClassName(countTagName).length;
      console.log(tagCount);
      if (tagCount == totalDocs) {
        var newInput = document.createElement('input');
        newInput.className = 'top_element';
        newInput.setAttribute('id', tagsArray[i] + 'top');
        var spanToAppend = document.getElementById(tagsArray[i] + '_edit_all');
        spanToAppend.appendChild(newInput);
        var newLink = document.createElement('a');
        newLink.setAttribute('href', '#');
        var functionString = 'normaliseTag(' + tagCount + ', "' + tagsArray[i] + '", "' + fullPath + '"); return false;';
        newLink.setAttribute('onclick', functionString);
        spanToAppend.appendChild(newLink);
        var newIcon = document.createElement('i');
        newIcon.className = 'fa fa-floppy-o fa-2x save_button';
        var iconString = tagsArray[i] + '_edit_icon';
        newIcon.setAttribute('id', iconString);
        newLink.appendChild(newIcon);

      }
    }
  }

  $('#fountainTextG').hide();
  $('.content').fadeIn();
  $('.feedback').hide();
  $("#myTable").tablesorter({
  widgets: ['stickyHeaders']}
  );
});

// onclick="normaliseTag("title", "/dc/hba-images/incoming/ninestars/HBA0011/HBA000001/20010501/01/xml/"); return false;"
function normaliseTag(num, tag, path) {
  var numberOfDocs = parseInt(num);
  var tagicon = tag + '_edit_icon';
  var inputBox = tag + 'top';
  var replaceValue = document.getElementById(inputBox).value
  console.log(tag);
  console.log(tagicon);
  document.getElementById(tagicon).style.color = 'Crimson';
  submitData = {
    'editTag' : tag,
    'fullPath' : path,
    'newValue' : replaceValue
  }
  console.log(document.getElementById(inputBox).value);
  document.getElementById(tagicon).style.color = 'Crimson';
  $.ajax({
    url: "normalise-api.php",
    type: "GET",
    data: submitData,
    success: function (data) {
      $('.feedback_error').fadeIn("slow");
      $('.feedback_error').hide();
      console.log(data);
      document.getElementById(tagicon).style.color = 'MediumSeaGreen';
      for (var k = 1; k <= numberOfDocs; k++) {
        replaceId = tag + k;
        console.log(replaceId);
        document.getElementById(replaceId).value = replaceValue
      }
    },
    error: function (data) {
      $('.feedback_error').fadeIn("slow");
      $('.feedback_error').hide();
      console.log(data);
      document.getElementById(tagicon).style.color = 'OrangeRed';
    }
  });
}

// feedback button slide toggle
function showFeedback(num, tag, full_file_path) {
  var file = full_file_path.substring(full_file_path.lastIndexOf("/") + 1);
  console.log("file: " + file)
  var batch = full_file_path.split('/')[4]
  var journal = full_file_path.split('/')[5]
  var number = parseInt(num);
  var itemTag = tag + number;
  var sourceValue = document.getElementById(itemTag).value;
  var currentUser = document.getElementById("user").value;
  var icon = tag + num + 'icon';
  document.getElementById("icon_id_for_colour").value = icon;
  document.getElementById("feedback-record-id").value = tag;
  document.getElementById("feedback-record").value = file;
  document.getElementById("feedback-summary").value = sourceValue;
  document.getElementById("feedback-user").value = currentUser
  document.getElementById("feedback-batch-reference").value = batch;
  document.getElementById("feedback-file").value = full_file_path;
  $('.feedback').slideToggle();
};

function submitFeedback () {
  $('.feedback').slideToggle();
  var full_file = document.getElementById("feedback-file").value.split('/');
  var temp_path = [];
  for (var i = 0; i < 3; i++) {
    temp_path.push(full_file[i]);
  }
  var feedbackPath =  temp_path.join('/');
  var batch = document.getElementById("feedback-batch-reference").value;
  var user = document.getElementById("feedback-user").value;
  var product = full_file[2];
  product = product.split('-');
  product = product[0];

  var updated_products = ['hba', 'wma', 'bpd', 'vogueitalia'];
  if (updated_products.indexOf(product) != -1) {
    var val_file_location = '/editorial/';
  }
  else {
    var val_file_location = '/validation/';
  }
  console.log(feedbackPath, val_file_location, batch, user)
  feedbackPath = feedbackPath + val_file_location + batch + '_greps-phase2-' + user + '.xls';
  console.log(feedbackPath);

  var formData = {
    'file' : feedbackPath,
    // 'type' : document.getElementById("feedback-type").value,
    'type' : document.querySelector('input[name="feedback-type"]:checked').value,
    'record' : document.getElementById("feedback-record").value,
    'tag' : document.getElementById("feedback-record-id").value,
    'summary' : document.getElementById("feedback-summary").value,
    'batch' : batch,
    'user' : user,
    'notes' : document.getElementById("feedback-notes").value,
    'offence' : document.getElementById("feedback-offence").value
  };

  $.ajax({
    url: "feedback-api.php",
    type: "GET",
    data: formData,
    success: function (data) {
      if (data['status'] == 201) {
        window.alert(data['data']);
      }
      else {
        console.log(data);
      }

    }
  });
  document.getElementById("feedback-notes").value = "";
  var icon_to_change = document.getElementById("icon_id_for_colour").value

  document.getElementById(icon_to_change).style.color = 'Crimson';
}

// resize columns
$(function () {
  var pressed = false;
  var start = undefined;
  var startX, startWidth;

  $("table th").not(".top_element").mousedown(function (e) {
    start = $(this);
    pressed = true;
    startX = e.pageX;
    startWidth = $(this).width();
  });

  $(document).mousemove(function (e) {
    if (pressed) {
      $(start).width(startWidth + (e.pageX - startX));
    }
  });

  $(document).mouseup(function () {
    if (pressed) {
      pressed = false;
    }
  });
});

function saveData(num, file, tags) {
  var split_tags = tags.split(',');
  var number = parseInt(num);
  var saveButton = 'save' + number;
  var values = [];

  for (var i = 0; i < split_tags.length; ++i) {
    var temp_tag = split_tags[i] + number;
    values.push(document.getElementById(temp_tag).value);
  }

  document.getElementById(saveButton).value = 'saved';
  var joined_values = values.join('||');

  var formData = {
    'file' : file,
    'tag' : tags,
    'value' : joined_values
  };
  $.ajax({
    url: "grep-api.php",
    type: "GET",
    data: formData,
    success: function (data) {
      console.log(data);
    }
  });
};
