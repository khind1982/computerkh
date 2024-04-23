<?php

$lines = file($directories_lookup) or die('cannot open file: <br>'.$directories_lookup.'<br>or '.$directories_lookup.' is empty.');

$typeahead_arr = array();
$dropdown_arr = array();
//$issues_arr = array();

foreach ($lines as $k => $v) {
    $path = explode("|", $v);
    //echo $v.'<br>';
    if ($path[0] == $current_path) {
        $path_number = $k;
    }
}

$first = explode("|", $lines[0]);
//echo $first[0].'<br/>';
$last = explode("|", $lines[count($lines)-1]);
//echo $last[0].'<br/>';

?>
<ul class="pagination">
    <?php
    if ($current_path != $first[0]) :
        $prev_iss = $lines[$path_number - 1];
        $prev_iss_path = explode("|", $prev_iss);
        ?>
        <li class="active"><a href="?path=<?php echo $first[0]; ?>" title="First issue">&laquo;</a></li>
        <li class="active"><a href="?path=<?php echo $prev_iss_path[0]; ?>">prev issue</a></li>
    <?php
    else : ?>
        <li class="disabled"><a href="#">&laquo;</a></li>
        <li class="disabled"><a href="#">prev issue</a></li>
    <?php
    endif;

    if ($current_path != $last[0]) :
        $next_iss = $lines[$path_number + 1];
        $next_iss_path = explode("|", $next_iss);
        ?>
        <li class="active"><a href="?path=<?php echo $next_iss_path[0]; ?>">next issue</a></li>
        <li class="active"><a href="?path=<?php echo $last[1]; ?>"  title="Last issue">&raquo;</a></li>
    <?php
    else : ?>
        <li class="disabled"><a href="#">next issue</a></li>
        <li class="disabled"><a href="#">&raquo;</a></li>
    <?php
    endif;
    ?>
</ul>

<form id="pathsearch" enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF']?>" method="POST">
    <div id="form-group1" class="input-group">
        <input type="text" id="searchpath" name="path" class="form-control typeahead">
        <span class="input-group-btn">
            <button type="submit" class="btn btn-default" type="button"><i class="uxf-search"></i></button>
        </span>
    </div>
</form>

<div class="dropdown">
    <button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenu1" data-toggle="dropdown"  aria-expanded="true">
    <?php echo substr($current_path, $path_substr_begin, $path_substr_end); ?>
    <span class="caret"></span>
    </button>
    <ul class="dropdown-menu scrollable-menu" role="menu" aria-labelledby="dropdownMenu1">
    <?php
    $list = array();
    foreach ($lines as $line) {
        $pieces = explode("|", $line);
        array_push($list, substr(rtrim($pieces[0]), $path_trim));
        if ($current_path != $pieces[0]) : ?>
            <li role="presentation">
                <a role="menuitem" tabindex="-1" href="?path=<?php echo $pieces[0]; ?> " class="list-group-item">
                    <?php echo $pieces[1]; ?>
                </a>
            </li>
        <?php elseif ($current_path === $pieces[0]) : ?>
            <li role="presentation">
                <a role="menuitem" tabindex="-1" href="?path=<?php echo $pieces[0]; ?> " class="list-group-item active">
                    <?php echo $pieces[1]; ?>
                </a>
            </li>
        <?php endif;
    }
    $data = json_encode($list);
    ?>
    </ul>
</div>

<?php

$files_raw = scandir($current_path);
//echo $files_raw;
$files = array();
foreach ($files_raw as $file) {
    if (substr($file, -3) === 'xml') {
        array_push($files, $file);
    }
}

include '../includes/condensed_nav.php';

?>
<div class="list-group">
<?php
foreach ($navi_list as $item) :
  ?>
  <a href="?file=<?php echo $item; ?>&path=<?php echo $current_path; ?>" class="list-group-item<?php if ($item === $current_file) { echo ' active'; } ?>"><?php echo $item; ?></a>
  <?php
endforeach;
?>
</div>
