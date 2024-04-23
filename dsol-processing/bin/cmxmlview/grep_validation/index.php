<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8">
<head>
  <title>Validation</title>
  <link href="http://dsol.private.chadwyck.co.uk/includes/css/font-awesome-animated.css" rel="stylesheet" type="text/css">
  <link href="http://dsol.private.chadwyck.co.uk/includes/css/font-awesome.css" rel="stylesheet" type="text/css">
  <link href="http://dsol.private.chadwyck.co.uk/includes/css/tablesorter.blue.css" rel="stylesheet" type="text/css">
  <link href="http://dsol.private.chadwyck.co.uk/includes/css/bootstrap.css" rel="stylesheet" type="text/css">

  <!-- custom css location -->
  <link href="./includes/css/custom.css" rel="stylesheet" type="text/css">
  <link href="./includes/css/progress.css" rel="stylesheet" type="text/css">
</head>

<body>

<div id="fountainTextG">
  <div id="fountainTextG_1" class="fountainTextG">L</div>
  <div id="fountainTextG_2" class="fountainTextG">o</div>
  <div id="fountainTextG_3" class="fountainTextG">a</div>
  <div id="fountainTextG_4" class="fountainTextG">d</div>
  <div id="fountainTextG_5" class="fountainTextG">i</div>
  <div id="fountainTextG_6" class="fountainTextG">n</div>
  <div id="fountainTextG_7" class="fountainTextG">g</div>
  <div id="fountainTextG_8" class="fountainTextG">.</div>
  <div id="fountainTextG_9" class="fountainTextG">.</div>
  <div id="fountainTextG_10" class="fountainTextG">.</div>
</div>

<div class="content">
<?php
include 'feedback.php';
?>

<nav class="navbar navbar-default">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
      </button>
      <a class="navbar-brand" href="index.php">Grep validation</a>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <form class="navbar-form navbar-left" role="search" action="index.php" method="POST">
        <div class="form-group">
          <input id="user" name="user" style="width:55px;" type="text" class="form-control"<?php
            if (isset($_POST['user'])) {
              echo ' value="'.$_POST['user'].'"';
            }
            else {
              echo 'placeholder="user"';
            }
          ?>
          >
          <input name="path" style="width:550px;" type="text" class="form-control" <?php
            if (isset($_POST['path'])) {
              echo 'value="'.$_POST['path'].'"';
            }
            else {
              echo 'placeholder="path to data e.g. /dc/hba-images/incoming/batch_001"';
            }
          ?>
            >
          <input name="tag" type="text" class="form-control" placeholder="tag, abstract, author, etc.">
        </div>
        <button type="submit" class="btn btn-default">Submit</button>
      </form>
      <ul class="nav navbar-nav navbar-right">
        <li><a href="index.php"><i style="color:blue;" class="fa fa-info-circle fa-2x"></i></a></li>
      </ul>
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>

<?php
require '../../php_modules/os.path.php';
function htmlDisplay($value) {
  $newValue = str_replace(array('"',"'", '<', '>'), array('&#34;', '&#39;', '&#60;', '&#62;'), $value);
  return $newValue;
}

$os = new OS_Path;
if (isset($_POST['tag']) && $_POST['path']) {
  require 'grep.php';
}
else {
  require 'instructions.htm';
  }
?>


  <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.js"></script>
  <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.tablesorter.js"></script>
  <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.tablesorter.widgets.js"></script>
  <script src="http://dsol.private.chadwyck.co.uk/includes/js/bootstrap.js"></script>

  <script src="./includes/js/custom.js"></script>
</div>
</body>
</html>
