<?php 
$dirs_ary = glob('*',GLOB_ONLYDIR);
foreach ($dirs_ary as $dir) {
  echo $dir.'\n';
  $filestring = file_get_contents($dir.'/inVideoQuiz.html');
  $dom = new DOMDocument();
  $dom->loadHTML($filestring);
  $textarea = $dom->getElementById('quiz_xml');
  if ($textarea) {
    if($xml = $textarea->childNodes->item(0))
       file_put_contents($dir.'/question.xml', html_entity_decode(utf8_decode($xml->C14N())));
  }
}
?>
