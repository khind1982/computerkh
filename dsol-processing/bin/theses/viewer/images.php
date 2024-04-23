<?php
$img = dirname($workfile);
$img = str_replace("/dc/theses/01-IN", "", $img);
?>
<div id="carousel-example-generic" class="carousel slide" data-ride="carousel" data-interval="false">

  <!-- Wrapper for slides -->
  <div class="carousel-inner" role="listbox">
    <div class="item active">
      <img src=".<?php echo $img.'/00001.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00002.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00003.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00004.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00005.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00006.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00007.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00008.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00009.jpg' ?>" alt="...">
    </div>
    <div class="item">
      <img src=".<?php echo $img.'/00010.jpg' ?>" alt="...">
    </div>
  </div>

  <!-- Controls -->
  <a class="left carousel-control" href="#carousel-example-generic" role="button" data-slide="prev">
    <span class="fa fa-angle-left" aria-hidden="true"></span>
    <span class="sr-only">Previous</span>
  </a>
  <a class="right carousel-control" href="#carousel-example-generic" role="button" data-slide="next">
    <span class="fa fa-angle-right" aria-hidden="true"></span>
    <span class="sr-only">Next</span>
  </a>
</div>
