<?php
$manifest = file_get_contents('course_manifest.txt');
$ary = explode("\n", $manifest);
$section = "";
foreach ($ary as $line) {
  if (substr($line,0,9)=="Section: ") {
    $section = str_replace(array(" ",":"), "-",substr($line,9)); 
    echo "Section Name: $section\n";
    exec("mkdir videos/$section");
  } else {
    $raw = rawurldecode($line);
    if($pos=strpos($raw,"("))
      $pos=$pos-1;
    else
      $pos=strlen($raw);
    $dir = str_replace(array("/",",",".","?"," ", ":"), "-", substr($raw,0,$pos));
    echo "Dir: $dir\n";
    if ($line !="") {
      exec("rm -rf videos/$section/$dir");
      exec("cp -r nlp_test/$line videos/$section/$dir");
    }
  }
}



?>