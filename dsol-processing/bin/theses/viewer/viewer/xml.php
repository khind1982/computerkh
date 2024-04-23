<?php
$curr = explode('|', $lines[$current]);
$curr = explode('/', $curr[0]);
$last = count($curr)-1;
$last = $curr[$last];
$last = substr($last, 0, -4);
$next = $current + 1;
$next = explode('|', $lines[$next]);
$next = $next[0];
?>
<form class="form-horizontal" enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
<?php
if (isset($_POST["MM_edit"])) :
    include 'xml_save.php';
    ?>
    <div class="pull-right">
    <a class="btn btn-success disabled">Saved!</a>
    </div>
    <?php
else :
    ?>
    <div class="pull-right">
    <button type="submit" class="btn btn-primary" name="MM_edit" value="Save">Save</button>
    </div>
    <?php
endif;

echo $last.'&nbsp;&nbsp;<a href="?path='.$next.'">>></a>';

$dom = new DOMDocument();
$dom->load($workfile);
$xml_data = array(); ?>

    <table class="table">
        <tr>
            <td>Surname</td>
            <td>
                <input type="text" class="form-control" id="DISS_surname" name="DISS_surname" value="<?php echo $dom->getElementsByTagName('DISS_surname')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>First</td>
            <td>
                <input type="text" class="form-control" id="DISS_fname" name="DISS_fname" value="<?php echo $dom->getElementsByTagName('DISS_fname')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>Middle</td>
            <td>
                <?php $middle = $dom->getElementsByTagName('DISS_middle')->item(0)->nodeValue; ?>
                <input type="text" class="form-control" id="DISS_middle" name="DISS_middle" value="<?php if ($middle) { echo $middle; } ?>"<?php if (!$middle) { echo "disabled"; } ?>>
            </td>
        </tr>
        <tr>
            <td>Title</td>
            <td>
                <textarea rows="3" class="form-control" id="DISS_title" name="DISS_title"><?php echo $dom->getElementsByTagName('DISS_title')->item(0)->nodeValue; ?></textarea>
            </td>
        </tr>
        <tr>
            <td>Date</td>
            <td>
                <input type="text" class="form-control" id="DISS_comp_date" name="DISS_comp_date" value="<?php echo $dom->getElementsByTagName('DISS_comp_date')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>Date</td>
            <td>
                <input type="text" class="form-control" id="DISS_accept_date" name="DISS_accept_date" value="<?php echo $dom->getElementsByTagName('DISS_accept_date')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <?php
        $searchNode = $dom->getElementsByTagName("DISS_description")->item(0);
        ?>
        <tr>
            <td>Pagecount</td>
            <td>
                <input type="text" class="form-control" id="page_count" name="page_count" value="<?php echo $searchNode->getAttribute('page_count'); ?>">
            </td>
        </tr>
        <tr>
            <td>Degree</td>
            <td>
                <input type="text" class="form-control" id="DISS_degree" name="DISS_degree" value="<?php echo $dom->getElementsByTagName('DISS_degree')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>Institute</td>
            <td>
                <input type="text" class="form-control" id="DISS_inst_name" name="DISS_inst_name" value="<?php echo $dom->getElementsByTagName('DISS_inst_name')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>Contact</td>
            <td>
                <input type="text" class="form-control" id="DISS_inst_contact" name="DISS_inst_contact" value="<?php echo $dom->getElementsByTagName('DISS_inst_contact')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>Language</td>
            <td>
                <input type="text" class="form-control" id="DISS_language" name="DISS_language" value="<?php echo $dom->getElementsByTagName('DISS_language')->item(0)->nodeValue; ?>">
            </td>
        </tr>
        <tr>
            <td>Abstract</td>
            <td>
                <textarea rows="20" class="form-control" id="DISS_para" name="DISS_para"><?php echo $dom->getElementsByTagName('DISS_para')->item(0)->nodeValue; ?></textarea>
            </td>
        </tr>
    </table>
</form>
