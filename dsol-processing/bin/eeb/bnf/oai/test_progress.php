<!DOCTYPE html>
<html>

  <head>
    <meta charset="UTF-8">
    <title>BnF data enrichment</title>
	<link href="http://dsol.private.chadwyck.co.uk/includes/css/font-awesome.css" rel="stylesheet" type="text/css">
	<link href="http://dsol.private.chadwyck.co.uk/includes/css/bootstrap.css" rel="stylesheet" type="text/css">
	<link href="http://dsol.private.chadwyck.co.uk/includes/css/bootstrap.extra.css" rel="stylesheet" type="text/css">
	<!-- custom css location -->
	<link href="./includes/custom.css" rel="stylesheet" type="text/css">
  </head>

  <body>
  <?php
  $result_file = '/opt/DSol/apache2/htdocs/eeb/bnf/oai/results.txt';
  $progress_file = '/opt/DSol/apache2/htdocs/eeb/bnf/oai/progress.txt';
  $done_file = '/opt/DSol/apache2/htdocs/eeb/bnf/oai/done.txt';

//
  if (file_exists($done) && (filesize($done_file) > 0)) {
    $page = 'test.htm';
    $sec = "0";
    header("Refresh: $sec; url=$page");
  }
  else {
    $line = fgets(fopen($progress_file, 'r'));
    $percentage = trim($line);
    ?>
    <div class="progress">
      <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="<?php echo $percentage; ?>" aria-valuemin="0" aria-valuemax="100" style="width: <?php echo $percentage; ?>%">
        <span class="sr-only"><?php echo $percentage; ?>% Complete</span>
      </div>
    </div>
    <?php
    $page = 'test_progress.php';
    $sec = "1";
    header("Refresh: $sec; url=$page");
  }
  ?>
    <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.js"></script>
    <script src="http://dsol.private.chadwyck.co.uk/includes/js/bootstrap.js"></script>
    <script src="http://dsol.private.chadwyck.co.uk/includes/js/bootstrap.extra.js"></script>
    <script src="./includes/custom.js"></script>
  </body>

</html>
