<?php
//This does the 2 level descend into subdirectories to convert videos from youtube to offline
//Requires: index.html to be at the root of directory structure, which will get copied to each sub-subdir

$dirs_ary = glob('*',GLOB_ONLYDIR);
foreach ($dirs_ary as $dir) {
	$subdirs_ary = glob("$dir/*", GLOB_ONLYDIR);
	foreach ($subdirs_ary as $subdir) {
		$path = "$subdir";
		echo "$path\n";
		exec("rm $path/*.html $path/question.xml $path/vidID.json");
		exec("cp index.html $path/index.html");
		$q=file_get_contents("$path/questions.json");
		$qjs="var questions=$q;";
		file_put_contents("$path/questions.js",$qjs);
		$i=file_get_contents("$path/indices.json");
		$ijs="var slideIndices = $i;";
		file_put_contents("$path/indices.js",$ijs);

		
	}
}
?>