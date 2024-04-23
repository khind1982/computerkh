<?php
$directory = $_POST['directory'];
echo $directory.'<br>';
$cmd = '/usr/local/versions/Python-2.6.2/bin/python /packages/dsol/eeb/bnf/oai/01_create_ark_lookup.py > /dev/null 2>&1 &';
//$cmd = 'python /packages/dsol/eeb/bnf/oai/01_create_ark_lookup.py > /dev/null 2>&1 &';
//$cmd = '/usr/local/versions/Python-2.6.2/bin/python /packages/dsol/eeb/bnf/oai/check_dates.py -i '.$directory.' > /dev/null 2>&1 &';
echo $cmd.'<br>';
//exec($cmd) or die('could not run command');
exec($cmd);

$page = 'ark_progress.php';
$sec = '2';
header("Refresh: $sec; url=$page");
?>
