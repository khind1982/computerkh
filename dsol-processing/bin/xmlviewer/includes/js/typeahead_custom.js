var substringMatcher = function(strs) {
    return function findMatches(q, cb) {
      var matches, substrRegex;

      matches = [];

      substrRegex = new RegExp(q, 'i');

      $.each(strs, function(i, str) {
        if (substrRegex.test(str)) {
          matches.push({ value: str });
        }
      });

      cb(matches);
    };
  };

  var states = <?php echo stripslashes($data); ?>;

  $('#form-group1 .typeahead').typeahead({
    hint: true,
    highlight: true,
    minLength: 1
  },
  {
    name: 'states',
    displayKey: 'value',
    source: substringMatcher(states)
  });

  $('#pathsearch').submit(function() {
    var txt = $('#searchpath');
    txt.val(<?php echo '"'.$typeahead_pre.'"'; ?> + txt.val());
  });
