<?php

require 'os.path.php';

class osTest extends PHPUnit_Framework_TestCase {

  public function testJoin() {
    $j = new OS_Path;
    $this->assertEquals('./a', $j->join('.', 'a'), '. + a != ./a');
    $this->assertEquals('./a', $j->join('.', '/a'), '. + /a != ./a');
    $this->assertEquals('/a/b', $j->join('/a', 'b'), '/a + b != /a/b');
    $this->assertEquals('/a/b', $j->join('/a', '/b'), '/a + /b != /a/b');
    $this->assertEquals('./a/b', $j->join('./a', '/b'), './a + /b != ./a/b');
    $this->assertEquals('a/b', $j->join('a','b'), 'a + b != a/b');
    $this->assertEquals('/a/b', $j->join('/a/','/b'), '/a/ + /b != /a/b');
  }

  public function testListdir() {
    $j = new OS_Path;
    $this->assertEquals(array(2 => '1.htm', 3 => '2.htm', 4 => '3.htm'), $j->listdir('C:\php\www\test\modules\testfiles'), 'array(\'1.htm\', \'2.htm\', \'3.htm\')');
  }

  public function testwalk() {
    $k = new OS_Path;
    $desired_output = array(
      0 => 'C:\php\www\test\modules\tw/1/1.htm',
      1 => 'C:\php\www\test\modules\tw/1/2.htm',
      2 => 'C:\php\www\test\modules\tw/1/3.htm',
      3 => 'C:\php\www\test\modules\tw/1/1/1.htm',
      4 => 'C:\php\www\test\modules\tw/1/1/2.htm',
      5 => 'C:\php\www\test\modules\tw/1/1/3.htm',
      6 => 'C:\php\www\test\modules\tw/1/1/1/1.htm',
      7 => 'C:\php\www\test\modules\tw/1/1/1/2.htm',
      8 => 'C:\php\www\test\modules\tw/1/1/1/3.htm',
      9 => 'C:\php\www\test\modules\tw/1/1/2/1.htm',
      10 => 'C:\php\www\test\modules\tw/1/1/2/2.htm',
      11 => 'C:\php\www\test\modules\tw/1/1/2/3.htm',
      12 => 'C:\php\www\test\modules\tw/1/1/3/1.htm',
      13 => 'C:\php\www\test\modules\tw/1/1/3/2.htm',
      14 => 'C:\php\www\test\modules\tw/1/1/3/3.htm'
      );
    $this->assertEquals($desired_output, $k->walk('C:\php\www\test\modules\tw'));
  }

}

?>
