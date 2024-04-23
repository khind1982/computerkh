<?php
$current = 0;
$path = $_GET['path'];
?>
<ul class="nav nav-sidebar">
    <?php
    $lookup = '/dc/dsol/lords_viewer_data/1819.txt';
    $lines = file($lookup) or die('cannot open file');
    if ($path) {
        $workfile = $path;
    }
    else {
        $xml = explode('|', $lines[0]);
        $workfile = $xml[0];
    }

    foreach ($lines as $k => $v) {
        $path = explode("|", $v);
        if ($path[0] === $workfile) :
            $current = $k;
            ?>
            <li class="active"><a href="?path=<?php echo $path[0]; ?>"><?php echo $path[1]; ?> <span class="sr-only">(current)</span></a></li>
        <?php
        else: ?>
            <li><a href="?path=<?php echo $path[0]; ?>"><?php echo $path[1]; ?></a></li>
        <?php
        endif;
    }
    ?>
</ul>
