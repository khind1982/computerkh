// feedback button slide toggle
$("#feedback_button").click(function () {
  $('.feedback-form').slideToggle();
});

// feedback remove images
$('.delete-btn').click(function() {
  $(this).parents('.delete-group').remove();
});

// feedback submit ajax call
$('.feedback-btn').click(function () {
  event.preventDefault(); // prevent submit button from submitting
  console.log($("#feedback-form").serializeArray());
  var images = document.getElementsByClassName("delete-image");
  var imagesArr = [];
  // for(var i = 0, ll = images.length; i != ll; imagesArr.push(images[i++].value));
  for (var i = 0; i < images.length; i++) {
    imagesArr.push(images[i].value);
  }
  console.log(imagesArr.join(', '));
  document.getElementById("delete-images-all").value = imagesArr.join(', ');

  $.ajax({
    url: "../includes/feedback-api.php",
    type: "GET",
    data: $("#feedback-form").serializeArray(),
    success: function (data) {
      $('#feedback-panel').html("<div id='response-message'></div>");
      $('#response-message').html("<a id=\"feedback_button\">Done</a>")
      .fadeIn(10000);
      console.log(data);
    }
  });

});
