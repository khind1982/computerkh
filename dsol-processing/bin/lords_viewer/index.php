<!DOCTYPE html>
<html>

  <head>
    <meta charset="UTF-8">
    <title><!-- Title --></title>
      <link href="http://dsol.private.chadwyck.co.uk/includes/css/font-awesome.css" rel="stylesheet" type="text/css">
      <link href="http://dsol.private.chadwyck.co.uk/includes/css/bootstrap.css" rel="stylesheet" type="text/css">
      <link href="http://dsol.private.chadwyck.co.uk/lordsviewer/includes/custom.css" rel="stylesheet" type="text/css">
  </head>

  <body>
    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container-fluid">
        <div class="navbar-header">
          <!-- link to index page -->
          <a class="navbar-brand" href="#">Title</a>
        </div>
        <div id="navbar">
          <ul class="nav navbar-nav">
            <!-- Nav item 1 -->
            <li><a href="link1.php">link1</a>
            </li>
            <!-- Nav item 2 -->
            <li class="active"><a href="link2.php">link2</a>
            </li>
          </ul>
          <ul class="nav navbar-nav navbar-right">
            <!-- Link to instructions -->
            <li><a href="instructions.htm">Instructions</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container-fluid">
      <div class="custom-body">
        <div class="row">
          <div class="col-md-2 sidebar">
            <?php include 'files.php'; ?>
          </div>
          <div class="col-md-4">
            xml here
            <?php

            ?>
          </div>
          <div class="col-md-6 main">
            images here
          </div>
        </div>
      </div>
    </div>

    <script src="http://dsol.private.chadwyck.co.uk/includes/js/jquery.js"></script>
    <script src="http://dsol.private.chadwyck.co.uk/includes/js/bootstrap.js"></script>
  </body>

</html>
