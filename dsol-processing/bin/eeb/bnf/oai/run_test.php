<?php

//$cmd = '/usr/local/versions/Python-2.6.2/bin/python /packages/dsol/eeb/bnf/oai/test_php-python.py > /dev/null 2>&1 &';
$cmd = 'test_php-python > /dev/null 2>&1 &';
//$cmd = 'python /packages/dsol/eeb/bnf/oai/01_create_ark_lookup.py > /dev/null 2>&1 &';
//$cmd = '/usr/local/versions/Python-2.6.2/bin/python /packages/dsol/eeb/bnf/oai/check_dates.py -i '.$directory.' > /dev/null 2>&1 &';
echo $cmd.'<br>';
//exec($cmd) or die('could not run command');
exec($cmd);

$page = 'test_progress.php';
$sec = '2';
header("Refresh: $sec; url=$page");
?>
