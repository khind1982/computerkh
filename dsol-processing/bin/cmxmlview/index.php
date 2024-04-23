<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <?php
  require '../../php_modules/os.path.php';
  $os = new OS_Path;

  $user = explode('.php', $_SERVER["REQUEST_URI"]);
  $user = explode('_', $user[0]);
  $product = explode('/', $_SERVER["REQUEST_URI"]);
  // echo $product[2];
  $ux_css = '../includes/css/uxf-1.0.0-blue.min.css';
  $typea_css = '../includes/css/typeahead.css';
  $fa_css = '../includes/css/font-awesome.css';
  $custom_css = '../includes/css/style.css';
  $jqm_js = '../includes/js/jquery.min.js';
  $ux_js = '../includes/js/uxf-1.0.0.min.js';
  $jq_js = '../includes/js/jquery.js';
  $typea_js = '../includes/js/typeahead.bundle.js';
  $custom_js = '../includes/js/custom.js';
  ?>

  <title><?php echo $product[2].' '.$user[1]; ?></title>
  <link rel="stylesheet" href="<?php echo $ux_css.'?v='.date("YmdHis", filemtime($ux_css)); ?>">
  <link rel="stylesheet" href="<?php echo $typea_css.'?v='.date("YmdHis", filemtime($typea_css)); ?>">
  <link rel="stylesheet" href="<?php echo $fa_css.'?v='.date("YmdHis", filemtime($fa_css)); ?>">
  <link rel="stylesheet" href="<?php echo $custom_css.'?v='.date("YmdHis", filemtime($custom_css)); ?>">

</head>

<?php
include 'conf_'.$product[2].'.php';
?>

<body>
  <div class="navbar navbar-inverse">
    <div class="navbar-header">
      <ul class="nav navbar-nav">
        <li>
          <a class="navbar-brand diagonal" href="#">
          <img alt="" src="../includes/imgs/sample-icon.png" style= "width:24px; height:24px;"></a>
        </li>
        <li>
          <div class="navbar-brand product-name">
            <div class="pq-logo"></div>
            <a href="#">XML viewer
              <span class="subtitle"><?php echo $prod; ?></span>
            </a>
          </div>
        </li>
      </ul>
    </div>
  </div>

  <div class="container-fluid">
    <div class="row">
      <div class="col-md-3"><?php include '../includes/directories.php'; ?></div>
      <div class="col-md-3"><?php include '../includes/xml.php'; ?></div>
      <div class="col-md-6"><?php
        if (in_array($product[2], array('aaa', 'eima', 'trench', 'wwd', 'win'))) {
          include '../includes/images_aaa_eima_trench_wwd.php';
        }
        else {
          include '../includes/images_bpc.php';
        }
        ?>
    </div>
  </div>

  <?php
  include '../includes/feedback.php';
  ?>

  <script src="<?php echo $jqm_js.'?v='.date("YmdHis", filemtime($jqm_js)); ?>"></script>
  <script src="<?php echo $ux_js.'?v='.date("YmdHis", filemtime($ux_js)); ?>"></script>
  <script src="<?php echo $jq_js.'?v='.date("YmdHis", filemtime($jq_js)); ?>"></script>
  <script src="<?php echo $typea_js.'?v='.date("YmdHis", filemtime($typea_js)); ?>"></script>
  <script src="<?php echo $custom_js.'?v='.date("YmdHis", filemtime($custom_js)); ?>"></script>

  <script type="text/javascript">
    //typeahead functionality

    var substringMatcher = function (strs) {
      return function findMatches(q, cb) {
        var matches, substrRegex;

        matches = [];

        substrRegex = new RegExp(q, 'i');

        $.each(strs, function (i, str) {
          if (substrRegex.test(str)) {
            matches.push({
              value: str
            });
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
    }, {
      name: 'states',
      displayKey: 'value',
      source: substringMatcher(states)
    });

    $('#pathsearch').submit(function () {
      var txt = $('#searchpath');
      txt.val(<?php echo '"'.$typeahead_pre.'"'; ?> + txt.val());
    });

  </script>
</body>
</html>


