<?php
    $course_name = "Natural Language Processing";
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"> 
<html xmlns='http://www.w3.org/1999/xhtml'> 

<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <title><?php echo $course_name; ?></title>
    <link rel="stylesheet" href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.17/themes/smoothness/jquery-ui.css" type="text/css" media="all" />
    <link rel="stylesheet" href="css/quiz.css" />
    <link rel="icon" href="favicon.ico" />
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" type="text/javascript"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.17/jquery-ui.min.js" type="text/javascript"></script>
    <script src="js/c2gSections.js" type="text/javascript"></script>
    <script src="js/demorun.js" type="text/javascript"></script>
    <script src="../js/jquery.blockUI.js" type="text/javascript"></script>
    <script type="text/javascript" src="../js/hotkey.js"> </script>
    <script>

    </script>
</head>

<body>
<header>
	    <div class="header-img" >
	      <!--<img src="http://www.stanford.edu/group/identity/images/de_block1.gif" alt="Stanford University logo" height="23" width="21" />-->
	      <img src="http://identity.stanford.edu/images/de_emb3.gif" alt="Stanford University logo" height="23" width="21" />
	    </div>
	    <div class="header-text">
	      <h1>Stanford University</h1> <h2><?php echo $course_name; ?></h2>
	    </div>
        <div class="other-links">
            <a href="http://piazza.com/stanford/winter2012/nlp" target="forum">Discussion Forums</a>
        </div>
</header>

<?php
    require_once('syllabus_nav.php');
?>

<div id="import-container">
<iframe id="importer" height="620" width="740" border="0"></iframe>
</div>

</body>
</html>
