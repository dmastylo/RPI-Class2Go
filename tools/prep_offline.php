<?php
$dirs_ary = glob('*',GLOB_ONLYDIR);
foreach ($dirs_ary as $dir) {
	exec("cp index.html $dir/index.html");
	$q=file_get_contents("$dir/questions.json");
	$qjs="var questions=$q;";
	file_put_contents("$dir/questions.js",$qjs);
	$i=file_get_contents("$dir/indices.json");
	$ijs="var slideIndices = $i;";
	file_put_contents("$dir/indices.js",$ijs);

}
?>