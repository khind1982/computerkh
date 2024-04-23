<?php

class OS_Path {

  public function join() {
    $paths = array();

    foreach (func_get_args() as $arg) {
      if ($arg !== '') {
        array_push($paths, $arg);
      }
    }
    return preg_replace('#/+#', '/', join('/', $paths));
  }

  public function listdir($path) {
    $unfiltered = scandir($path);
    $filtered = array_diff($unfiltered, array('.', '..'));
    return $filtered;
  }

  public function walk($directory) {
    $files = array();
    $dir = dir($directory);
    while (false !== ($file = $dir->read())) {
      if ($file === '.' || $file === '..') continue;
      $file = $this->join($directory, $file);
      if (is_dir($file)) {
        $this->walk($file);
      }
      else {
        echo $file;
        array_push($files, $file);
      }
    }
      return $files;
  }

}
?>
