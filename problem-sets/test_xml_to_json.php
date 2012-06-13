<?php


$xmlString = file_get_contents('nlp_example_quiz.xml');
$xmlObj = simplexml_load_string($xmlString,"SimpleXMLElement", LIBXML_NOCDATA);

$jsonString = json_encode($xmlObj);
file_put_contents('nlp_example_quiz.json',$jsonString);

$printString = print_r($xmlObj,true);
file_put_contents('nlp_example_quiz.print_r',$printString);

?>