<!DOCTYPE html>
<html lang="en">
<head>
    <title>Theses viewer</title>
    <link href="../includes/css/uxf-1.0.0-blue.min.css" rel="stylesheet" >
    <link href="../includes/css/style.css" rel="stylesheet">
    <link href="../includes/css/font-awesome.min.css" rel="stylesheet" type="text/css">
</head>

<body>
    <div class="section">
        <div class="container" style="
               margin-left: 0px;
               margin-right: 0px">
            <div class="row">
                <div class="col-lg-2">
                    <?php include 'files.php'; ?>
                </div>
                <div class="col-lg-4">
                    <?php include 'xml.php'; ?>
                </div>
                <div class="col-lg-6">
                    <?php include 'images.php'; ?>
                </div>
            </div>
        </div>
    </div>

    <script src="../includes/js/jquery.min.js"></script>
    <script src="../includes/js/uxf-1.0.0.min.js"></script>
</body>
</html>
