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
                                <h3 class="panel-title">Image resolution validation tool</h3>
                            </div>
                            <div class="panel-body">
                                <p class="text-center">This tool will check the resolution of all the tiff images in a given
                                    directory/directories. All images wth a resolution other than 400 dpi will
                                    be logged.</p>
                                <form class="form-horizontal" role="form" action="progress.php" method="POST">
                                    <div class="form-group">
                                        <div class="col-sm-2">
                                            <label for="directory" class="control-label">Image directory</label>
                                        </div>
                                        <div class="col-sm-10">
                                            <input type="text" class="form-control" name="path" id="path" placeholder="/dc/theses/01-IN/..." >
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-sm-2">
                                            <label for="resolution" class="control-label">Valid resolution</label>
                                        </div>
                                        <div class="col-sm-10">
                                            <input type="text" class="form-control" name="resolution" id="resolution" value="400" >
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-sm-offset-2 col-sm-10">
                                          <div class="checkbox">
                                            <label contenteditable="true">
                                              <input type="checkbox" name="type" value="multi">Multiple directories</label>
                                          </div>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-sm-offset-2 col-sm-10">
                                            <div class="radio">
                                                <label>
                                                    <input type="radio" name="image" value="jpg">JPEG</label>
                                            </div>
                                        </div>
                                        <div class="col-sm-offset-2 col-sm-10">
                                            <div class="radio">
                                                <label>
                                                    <input type="radio" name="image" value="tif" checked>TIFF</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <div class="col-sm-offset-2 col-sm-10">
                                            <button type="submit" name="MM_submit" class="btn btn-default">Check!</button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>

</html>
