<!DOCTYPE html>
<html>
<body>
<?php
$logFile = '/opt/DSol/apache2/htdocs/theses/res_check/config.txt';
$fh = fopen($logFile, 'w');
$log_entry = $_POST['path']."\n";
fwrite($fh, $log_entry);
$log_entry = $_POST['image']."\n";
fwrite($fh, $log_entry);
$log_entry = $_POST['resolution']."\n";
fwrite($fh, $log_entry);
if (isset($_POST['type'])) {
    $log_entry = $_POST['type']."\n";
    fwrite($fh, $log_entry);
}
else {
    $log_entry = 'single'."\n";
    fwrite($fh, $log_entry);
}
fclose($fh);
chmod($logFile,0777);
?>
<script>
if(typeof(EventSource) !== "undefined") {
    var source = new EventSource("check.php");
    source.onmessage = function(event) {
        if (event.data !== "404") {
            document.body.innerHTML += event.data + '<br>';
            console.log(event.data);
        }
        else {
            console.log("we have to stop now");
            source.close();
            window.location.href = "results.php";
        }
    };
}
else {
    document.getElementById("result").innerHTML = "Sorry, your browser does not support server-sent events...";
}
</script>

</body>
</html>
