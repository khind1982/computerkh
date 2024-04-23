<?php

// exec('sh -x /home/rschumac/svn/trunk/bin/xmlviewer/cp_boot.sh');
$filename = 'includes/css/style.css';

echo "$filename was last modified: " . date ("F d Y H:i:s.", filemtime($filename)).'<br>';
echo "$filename was last modified: " . date ("YmdHis", filemtime($filename)).'<br>';
echo "$filename was last modified: " . filemtime($filename);



?>
