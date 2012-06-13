<?php 

$title = rawurlencode($_GET['title']);
$fullpath = '/opt/courseware/nlp_test/quizzes/'.$title;
$cmd1 = 'mkdir "'.$fullpath.'"';
echo $cmd1.'<br/>';
exec($cmd1);


$url = $_GET['url'];

$fname = $_GET['fname'];

$cmd2 = 'wget --load-cookies ../cookies.txt -O "'.$fullpath.'/'.$fname.'" '. $url .'&';
exec($cmd2);
$cmd3 = 'wget --load-cookies ../cookies.txt '. $url ."&";



?>