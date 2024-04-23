<?php
$path = "/opt/DSol/apache2/htdocs/theses/res_check";

$latest_ctime = 0;
$latest_filename = '';

$d = dir($path);
while (false !== ($entry = $d->read())) {
  $filepath = "{$path}/{$entry}";
  if (is_file($filepath) && filectime($filepath) > $latest_ctime) {
    $latest_ctime = filectime($filepath);
    $latest_filename = $entry;
  }
}

$lines = file($latest_filename) or die('cannot open file');
$failed = $lines[0];
$failed = explode(':', $failed);
$failed = $failed[1];
$passed = $lines[1];
$passed = explode(':', $passed);
$passed = $passed[1];
?>

<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script type="text/javascript" src="../includes/js/jquery.min.js"></script>
    <script type="text/javascript" src="../includes/js/bootstrap.min.js"></script>
    <link href="../includes/css/font-awesome.min.css" rel="stylesheet" type="text/css">
    <link href="../includes/css/bootstrap.css" rel="stylesheet" type="text/css">
</head>

<body>
    <div class="section">
        <div class="container">
            <div class="row">
                <div class="col-md-12">
                    <div class="panel panel-primary">
                        <div class="panel-heading">
                            <h3 class="panel-title">Image resolution validation tool: Results</h3>
                        </div>
                        <div class="panel-body">
                            Total number of images: <?php echo $failed + $passed; ?><br/>
                            Number of images failed: <?php echo $failed; ?><br/>
                            Number of images passed: <?php echo $passed; ?><br/>
                            <a href="<?php echo $latest_filename; ?>" target="_blank">View logfile</a><br/>
                            <a href="index.php">Validate more images</a><br/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>

</html>

