<ul class="pagination">

<?php
$pagination_files = glob($current_path.'*.xml');
$pagination_first = $pagination_files[0];
$pagination_first_split = explode("/", $pagination_first);
$pagination_file_first = $pagination_first_split[sizeof($pagination_first_split) - 1];

$pagination_last = $pagination_files[sizeof($pagination_files) - 1];
$pagination_last_split = explode("/", $pagination_last);
$pagination_file_last = $pagination_last_split[sizeof($pagination_last_split) - 1];

if (substr($current_file,  -8, -4) > 1) : ?>
    <li class="active">
        <a href="?file=<?php echo $pagination_file_first; ?>&path=<?php echo $current_path; ?>" title="First article">&laquo;</a>
    </li>
    <li class="active">
        <a href="?file=<?php echo substr($current_file,  0, -8).str_pad(ltrim(substr($current_file,  -8, -4), "0") - 1, 4, '0', STR_PAD_LEFT); ?>.xml&path=<?php echo $current_path; ?>">prev article</a>
    </li>
<?php else : ?>
    <li class="disabled"><a href="#">&laquo;</a></li>
    <li class="disabled"><a href="?file=#">prev article</a></li>
<?php endif;

if ($current_file != $pagination_file_last) : ?>
    <li class="active">
        <a href="?file=<?php echo substr($current_file,  0, -8).str_pad(ltrim(substr($current_file,  -8, -4), "0") + 1, 4, '0', STR_PAD_LEFT); ?>.xml&path=<?php echo $current_path; ?>">next article</a>
    </li>
    <li class="active"><a href="?file=<?php echo $pagination_file_last; ?>&path=<?php echo $current_path; ?>" title="Last article">&raquo;</a></li>
<?php else : ?>
    <li class="disabled"><a href="#">next article</a></li>
    <li class="disabled"><a href="#">&raquo;</a></li>
<?php endif; ?>

</ul>



