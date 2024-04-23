function saveData(num) {
  var number = parseInt(num);
  var saveButton = 'save-button' + number;
  var saveFile = 'file' + number;
  var saveTitle = 'title' + number;

  document.getElementById(saveButton).value = 'saved';

  var formData = {
    'title' : document.getElementById(saveTitle).value,
    'file' : document.getElementById(saveFile).value
  };
  $.ajax({
    url: "title-api.php",
    type: "GET",
    data: formData,
    success: function (data) {
      console.log(data);
    }
  });
};

function copyDown(num) {
  var number = parseInt(num);
  var copyButton = 'copy-down' + number;
  document.getElementById(copyButton).value = 'copied';
  copyHandler(number);
};

function copyHandler(n) {
  var srceTitle = 'title' + n;
  var destTitle = 'title' + (n + 1);
  var copyVal = document.getElementById(srceTitle).value;
  var replaceInput = document.getElementById(destTitle);

  replaceInput.value = copyVal;
};

$(document).ready(function() {
  $('body').fadeIn();
  $("#myTable").tablesorter();

});



/*

window.onload = function() {
  init();
  doSomethingElse();
};
$('.save-btn').click(function () {
  console.log('something');
  event.preventDefault(); // prevent submit button from submitting
  console.log($(this).closest("form").serializeArray());
  $.ajax({
    url: "title-api.php",
    type: "GET",
    data: $(this).closest("form").serializeArray(),
    success: function (data) {
      console.log(data);
    }
  });
});
*/

