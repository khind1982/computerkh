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

    <form class="form-horizontal" action="run_python.php" method="POST">
      <div class="form-group">
        <label for="directory" class="col-sm-2 control-label">Directory</label>
        <div class="col-sm-10">
          <input type="text" class="form-control" id="directory" name="directory">
        </div>
      </div>
      <div class="form-group">
        <div class="col-sm-offset-2 col-sm-10">
          <button type="submit" class="btn btn-default">Submit</button>
        </div>
      </div>
    </form>

    <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.js"></script>
    <script src="http://dsol.private.chadwyck.co.uk/includes/js/bootstrap.js"></script>
    <script src="http://dsol.private.chadwyck.co.uk/includes/js/bootstrap.extra.js"></script>
    <script src="./includes/custom.js"></script>
  </body>

</html>
