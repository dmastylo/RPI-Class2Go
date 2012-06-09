<?php
$dirs_ary = glob('*',GLOB_ONLYDIR);
foreach ($dirs_ary as $dir) {
  $inputString = file_get_contents($dir.'/SlideManifest.txt');
  $manifests = explode("\n",$inputString);
  $json = Array();
  
  for($i=1;$i < count($manifests);$i++) {  //starts at 1--first line is list of all images and can be skipped.
    sscanf($manifests[$i],"lectureS%d.jpg %d %d %s",$slideNum, $start, $end, $waste); 
    echo "lecture-$slideNum.jpg: $start \n";
    
    $slideTitle = "lecture-$slideNum.jpg";
    $json[$start]=Array("imgsrc"=>$slideTitle);
  }
  if (!isset($json[0])) {
    $json[0]=Array("imgsrc"=>"lecture-0.jpg");
  }
  file_put_contents("/opt/courseware/nlp_test/".$dir."/indices.json", json_encode($json));
}

?>