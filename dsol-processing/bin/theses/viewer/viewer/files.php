<?php $current = 0; ?>
<ul class="list-group">
    <?php
    $lookup = 'files.txt';
    $lines = file($lookup) or die('cannot open file');
    if ($_GET['path']) {
        $workfile = $_GET['path'];
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
            <li><b><a href="?path=<?php echo $path[0]; ?>"><?php echo $path[1]; ?></a></b></li>
        <?php
        else: ?>
            <li><a href="?path=<?php echo $path[0]; ?>"><?php echo $path[1]; ?></a></li>
        <?php
        endif;
    }
    ?>
</ul>
