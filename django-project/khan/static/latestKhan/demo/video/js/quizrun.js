// Fetch YouTube Player API as script node
var tag = document.createElement('script');
tag.src = "//www.youtube.com/player_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// Set up global vars
var questions={};
var slideIndices = {};
var vidName;
var player;

//Global settings for video player height and width
var vidPlayerHeight = 430;
var videoHeight = vidPlayerHeight - 30;
var vidPlayerWidth = 710;
var videoWidth = vidPlayerWidth;
var hRatio=1; //ratios for the screen size on which the overlay was made to that on which it will be displayed
var wRatio=1; //defaults to 1, calculated when the questions json object is loaded

function onYouTubePlayerAPIReady() {
    getVidID();
}

function getVidID() {
    vidName="xOfEYI61f3k";

    // setTimeout necessary here for everything to be ready at the right time
    // (hacky, but it does the job)
    setTimeout(function () { runQuiz(); }, 1000);
}


function runQuiz() {

    // slideIndices for the thumbnails
    slideIndices = {"0":{"imgsrc":"lecture-0.jpg"},"5":{"imgsrc":"lecture-1.jpg"},"61":{"imgsrc":"lecture-2.jpg"},"86":{"imgsrc":"lecture-3.jpg"},"110":{"imgsrc":"lecture-4.jpg"},"163":{"imgsrc":"lecture-5.jpg"},"201":{"imgsrc":"lecture-6.jpg"},"284":{"imgsrc":"lecture-7.jpg"},"342":{"imgsrc":"lecture-8.jpg"},"374":{"imgsrc":"lecture-9.jpg"},"418":{"imgsrc":"lecture-10.jpg"}};

    // questions for the specific thumbs which invoke an exercise
    questions = {
        "162": {"time": 162, "problemDiv": "levenshtein-1"},
        "163": {"time": 163, "problemDiv": "non-levenshtein"},
        "164": {"time": 164, "problemDiv": "levenshtein-2"}
    };

    for (j in questions) {
        questions[j].done = false;
    }

    var mods = document.getElementsByClassName('quizModule');
    for (i=0;i<mods.length;i++) {
        mods[i].style.display='inline';
    }

    // call function to add YT player
    createPlayer(vidName);

    if (questions.videoHeight) {
        hRatio = videoHeight / questions.videoHeight; 
    }

    if (questions.videoWidth) {
        wRatio = videoWidth / questions.videoWidth; 
    }

}

// add player to the page
function createPlayer(vid) {
    player = new YT.Player('player', {
        height: vidPlayerHeight,
        width: vidPlayerWidth,
        videoId: vid,
        // wmode: transparent  makes HTML goes on top of Flash
        // fs: disable full screen
        playerVars: {'autoplay': 0, 'wmode': 'transparent', 'fs': 0, 'controls':1, 'rel':0, 'modestbranding':1, 'showinfo':0},
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange,
            'onError': onPlayerError,
        }
    });

    document.getElementById('player').style['z-index']=-10;
    document.getElementById('player').style['-webkit-transform']='translateZ(0)';
}

var globalQTime = -1;


function setupQPane(qTime) {
    
    globalQTime = qTime;

    $('#playerdiv').fadeTo('slow', .7);
    //$('.video-overlay-question').show();
    //$('.video-overlay-hint').show();
    //console.log(questions[qTime]["problemDiv"]);
    $('#' + questions[qTime]["problemDiv"]).show();
    $('#' + questions[qTime]["problemDiv"]).css('z-index', 100);
    $('#answer_area').fadeIn('slow');

    //hide index navigation panel
    $("#slideIndex").hide();

    var curQ = questions[qTime];
    if(curQ.qType=="m-c")
    typeString = "Multiple-choice.  Please check ALL possible correct choices.";
    else
    typeString = "Please answer the following question:";
    
    var bgDiv = document.createElement('div');
    bgDiv.setAttribute('id', 'questionBG');
    $('#player').after(bgDiv);

    var qDiv = document.createElement('div');
    qDiv.setAttribute('class','questionDiv');
    qDiv.setAttribute('id','questionPane');
    $('#questionBG').after(qDiv);

}

function stripPx(sizeWithPx) {
    return parseInt(sizeWithPx.substr(0,sizeWithPx.search('px')));
}

function addChoices(curQ) {
    var i = 1;
    
    
    for (j in curQ.answers) {
    var qTable = document.createElement('table')
    qTable.setAttribute('id','choice'+i);
    qTable.setAttribute('class','qChoice');
    document.getElementById('questionPane').appendChild(qTable);

    var tr = document.createElement('tr');
    tr.setAttribute('class','qTableRow');
    tr.setAttribute("id","ansID" + i);
    var td1 = document.createElement('td');
    td1.setAttribute('class','qTableCheck');
    td1.innerHTML='<input class="choices" id="check'+i+'" type="checkbox" /><label class="checkButton"  id="label'+i+'"  for="check'+i+'"></label>';

    var td2 = document.createElement('td');
    td2.setAttribute('id', 'textCell'+i);
    td2.setAttribute('class','qTableAns');
    td2.innerHTML='<div class="mcAns" id="ansText'+i+'"></div>';
    tr.appendChild(td1);
    tr.appendChild(td2);
    qTable.appendChild(tr);


    $(qTable).css("left",stripPx(curQ.answers[j].tablePos.left)*wRatio);
    $(qTable).css("top",stripPx(curQ.answers[j].tablePos.top)*hRatio);

    $("#ansText"+i).css("height",stripPx(curQ.answers[j].aSize.height)*hRatio);
    $("#ansText"+i).css("width",stripPx(curQ.answers[j].aSize.width)*wRatio);

    $("#check"+i)[0].checked=false;
    $("#check"+i).button({text:false, icons: {primary: "ui-icon-blank"}, label:"Check if choice is correct"});  

    //Handle the toggling graphics (showing check or not) and radio button behavior 
    $("#check"+i).change( function (evt) {handleChange(evt.target);});

    document.getElementById('ansText'+i).innerHTML=curQ.answers[j].text;
    if (curQ.answers[j].text==""){
        
        document.getElementById('ansText'+i).style.opacity=0;
    }
    i+=1;
    }

}

function closeQPane() {
    
    $("#slideIndex").show();
    
    document.getElementById('qInst').innerHTML="";
    $("div#questionPane").remove();
    $("div#questionBG").remove();

    player.playVideo();
}

function handleChange(input) {

    if (questions[globalQTime].hasOwnProperty('mcType') && questions[globalQTime].mcType.toLowerCase()=="radio") {
    //Radio Button Behavior
    if (input.checked) {
        $(".choices").attr('checked',false).button('option','icons', {primary: "ui-icon-blank"}); //unselect all
        input.checked=true;  //reselect this
        $(input).button('option','icons', {primary: "ui-icon-check"});
    }
    else {
        //When someone clicks on an already selected radio button
        //Behavior is exact same as previous case
        $(".choices").attr('checked',false).button('option','icons', {primary: "ui-icon-blank"}); //unselect all
        input.checked=true;
        $(input).button('option','icons', {primary: "ui-icon-check"});
    }
    }

    else {
    //Default Behavior -- Checkbox
    if (input.checked) {
            $(input).button('option','icons', {primary: "ui-icon-check"});
    }
    else { 
            $(input).button('option','icons', {primary: "ui-icon-blank"});
    }
    }
}


function submitAns(qTime) {
    var curQ = questions[qTime];
    var allcorrect;
    if (curQ.qType == "m-c") {
    allcorrect=true;
    for (j in curQ.answers) {
        if((document.getElementById('check'+j).checked && !curQ.answers[j].correct) ||
           (!document.getElementById('check'+j).checked && curQ.answers[j].correct)) {
        allcorrect = false;
        break;
        }
    }
    }
    else { // sa
    allcorrect=false;
    var studentVal = document.getElementById('answerTemplate').value.trim();
    if (!curQ.isRegexp && studentVal.toLowerCase() == curQ.aText.trim().toLowerCase())
        allcorrect = true;
    if (curQ.isRegexp){
        var patt = /^\u002F.*\u002F/;  //A regex to match the string representation of a regex form
        try{
        var pattern = patt.exec(curQ.aText)[0]; //get the pattern including the slashes
        var modifiers = curQ.aText.slice(pattern.length);
        var regex = new RegExp(pattern.slice(1,-1),modifiers);
        if (regex.test(studentVal))
            allcorrect = true;
        } 
        catch (e) {
        allcorrect = false;
        }
    }
    }
    if (allcorrect)
    $('#correct-dialog').dialog('open');
    else
    $('#wrong-dialog').dialog('open');
}

function showExplanation() {
    var explanation="";
    try {
    explanation=questions[globalQTime].qExplanation;
    } catch(e) {
    explanation="";
    }
    $('div.inVidExplanation').html(explanation);
    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"correct-dialog"]);
    MathJax.Hub.Queue(["Typeset",MathJax.Hub,"wrong-dialog"]);

    $('#wrong-dialog').dialog('option', 'buttons',  
                  {
                  "Try Again": function() {
                      $( this ).dialog( "close" );
                      $('div.inVidExplanation').html("");
                      
                      // reset buttons again
                      $('#wrong-dialog').dialog('option','buttons',{
                      "Show Explanation": function() {
                          showExplanation();
                      },
                      "Try Again": function() {
                          $( this ).dialog( "close" );
                          $('div.inVidExplanation').html("");
                          
                      }
                      });
                  },
                  "Continue Video": function() {
                      $( this ).dialog( "close" );
                      $('div.inVidExplanation').html("");
                      closeQPane();
                  }
                  }
                 );

}

function skipQ() {
    $('#skip-dialog').dialog('open');
}

function timeDisplay(timeInSec) {
    var min = Math.floor(timeInSec/60);
    var sec = timeInSec - 60*min;
    if (sec<10) sec = '0'+sec;
    return ("" + min + ":" + sec);
}

function onPlayerReady(event) {
  
    HotKey(player);
    setupNavPanel();
}

function onPlayerError(event) {
    alert('error');
}

var recordMe;
function onPlayerStateChange(event) {
    recordMe=event;
    if (event.data == YT.PlayerState.PLAYING) 
    setTimeout(checkTime, 200);
}

var skipSecQ=-1;

//clears selected sides.  Then, selects the slide whose start
//time is the nearest one less than or equal to the input time parameter
function selectSlide(time) {
    nearest = -1;
    for (i in slideIndices) {
    var numi = parseInt(i);
    $(slideIndices[i].displayDiv).addClass('unselected');
    $(slideIndices[i].displayDiv).removeClass('selected');
    if (numi<=time && numi>nearest) {
        nearest=numi;
    }
    }
    if (nearest >-1){
    var selected = slideIndices[''+nearest].displayDiv;
    $(selected).addClass('selected');
    $(selected).removeClass('unselected');
    $('#slideIndex').scrollLeft(selected.offsetLeft-($('#slideIndex').width()-$(selected).width())/2);
    }
}

var lastTime = -1;

function checkTime() {    // display quiz
    //console.log('checkTime');
    var curTime = Math.floor(player.getCurrentTime());
    
    
    if (slideIndices.hasOwnProperty(curTime) || Math.abs(lastTime-curTime)>1){ 
    selectSlide(curTime);
    }
    
    if (questions.hasOwnProperty(curTime) && skipSecQ!=curTime && 
    player.getPlayerState() == YT.PlayerState.PLAYING) {
    processQuiz(curTime);
    }
    else {
    if (player.getPlayerState() == YT.PlayerState.PLAYING) {
        setTimeout(checkTime, 200);
    }
    }
    if (!questions.hasOwnProperty(curTime))
    skipSecQ=-1;

    lastTime=curTime;
}

function processQuiz(curTime) {
    player.pauseVideo();

    skipSecQ = curTime;

    if (questions.hasOwnProperty(curTime)) {
        questions[curTime].done=true;
        setupQPane(curTime);
    } else {
        player.playVideo();
    }
}

function setupNavPanel(){
    var merged=Array();

    for (time in slideIndices) {
    merged.push(time)
    }
    for (time in questions) {
    if (!isNaN(parseInt(time))) {
        merged.push(time);
    }
    }
    var sorted = merged.sort(function(a,b){return parseInt(a)-parseInt(b)});

    var lastTime=-1;

    for (i in sorted) {
    if (sorted[i] != lastTime) {
        if (slideIndices.hasOwnProperty(sorted[i])) {
        addSlideIndex(sorted[i]);
        }
        if (questions.hasOwnProperty(sorted[i])) {
        var tmpDiv=addQuizSlide(sorted[i]);
        slideIndices[sorted[i]]={displayDiv: tmpDiv};
        }
    }
    lastTime=sorted[i];
    }
}

function createIndexPanel() {
   var indexDiv = document.createElement('div');
    $(indexDiv).attr('id','slideIndex');
      
    $('#playerdiv')[0].appendChild(indexDiv);
}

function addSlideIndex(idxTime) {
    var indexDiv = document.getElementById('slideIndex');
    var tempDiv = document.createElement('div');
    $(tempDiv).addClass('divInIndex').attr('id','slideIndex'+idxTime+'s');
    var slideImg = document.createElement('img');
    slideImg.src = slideIndices[idxTime].imgsrc;
    slideIndices[idxTime].displayDiv = tempDiv;
    tempDiv.appendChild(slideImg);
    tempDiv.onclick=(function (time) {return function(evt) {
        player.seekTo(time);
        selectSlide(time);
    };})(idxTime);
    indexDiv.appendChild(tempDiv);
    return tempDiv;

}


function addQuizSlide(idxTime) {
    var indexDiv = document.getElementById('slideIndex');
    var tempDiv = document.createElement('div');
    var greyDiv = document.createElement('div');
    $(tempDiv).addClass('divInIndex').attr('id','slideIndex'+idxTime+'s');
    $(greyDiv).addClass('greyOverlay').html("<br/><br/>Quiz");
    var slideImg = document.createElement('img');
    slideImg.src = 'q_'+idxTime+'.jpg';

    tempDiv.appendChild(greyDiv);
    tempDiv.appendChild(slideImg);

    tempDiv.onclick=(function (time) {return function(evt) {
    player.seekTo(time-1);
    selectSlide(time);
    };})(idxTime);
    indexDiv.appendChild(tempDiv);
    return tempDiv;
}
