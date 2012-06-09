<?php
//This does the 2 level descend into subdirectories to convert videos from youtube to offline
//Requires: index.html to be at the root of directory structure, which will get copied to each sub-subdir

$dirs_ary = glob('*',GLOB_ONLYDIR);
foreach ($dirs_ary as $dir) {
	$subdirs_ary = glob("$dir/*", GLOB_ONLYDIR);
	foreach ($subdirs_ary as $subdir) {
		$path = "$subdir";
		echo "$path\n";
		$q=file_get_contents("$path/question.json");
		$qjs="var __c2g_questions=$q;renderQuiz(__c2g_questions);";
		file_put_contents("$path/question.js",$qjs);
	}
}
?>