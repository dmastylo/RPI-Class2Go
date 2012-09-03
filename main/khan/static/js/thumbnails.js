// Fetch YouTube Player API as script node
var tag = document.createElement('script');
tag.src = "//www.youtube.com/player_api";
var firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

//Global settings for video player height and width
var vidPlayerHeight = 430;
var videoHeight = vidPlayerHeight - 30;
var vidPlayerWidth = 710;
var videoWidth = vidPlayerWidth;
var hRatio=1; //ratios for the screen size on which the overlay was made to that on which it will be displayed
var wRatio=1; //defaults to 1, calculated when the questions json object is loaded

function onYouTubePlayerAPIReady() {
    thumbSet.getVidID();
}

function onPlayerReady(event) {
    //HotKey(player);
    thumbSet.setupNavPanel();

    $('.quiz-thumb').each(function (idx) {
        $(this).click(function () {
            console.log("Calling makeProblem for " + idx);
            $('#problemarea').show();
            KhanC2G.makeProblem(idx);
        });
    });
}

function onPlayerError(event) {
    alert('error');
}

function onPlayerStateChange(event) {
    thumbSet.recordMe=event;
    if (event.data == YT.PlayerState.PLAYING) 
    setTimeout(thumbSet.checkTime, 200);
}

var initThumbnails = function (c2gVidId, c2gSlideIndicesObj, c2gQuizIndicesObj) {

    var thumbSet = {

        // Set up global vars
        questions: {},
        slideIndices: {},
        vidName: null,
        player: null,
        globalQTime: -1,
        recordMe: null,
        skipSecQ: -1,
        lastTime: -1,

        getVidID: function() {
            vidName = c2gVidId;

            // setTimeout necessary here for everything to be ready at the right time
            // (hacky, but it does the job)
            setTimeout(function () { thumbSet.runQuiz(); }, 1000);
        },

        runQuiz: function() {

            // slideIndices for the thumbnails
            slideIndices = c2gSlideIndicesObj;
            //slideIndices = {"0":{"imgsrc":"lecture-0.jpg"},"5":{"imgsrc":"lecture-1.jpg"},"61":{"imgsrc":"lecture-2.jpg"},"86":{"imgsrc":"lecture-3.jpg"},"110":{"imgsrc":"lecture-4.jpg"},"163":{"imgsrc":"lecture-5.jpg"},"201":{"imgsrc":"lecture-6.jpg"},"284":{"imgsrc":"lecture-7.jpg"},"342":{"imgsrc":"lecture-8.jpg"},"374":{"imgsrc":"lecture-9.jpg"},"418":{"imgsrc":"lecture-10.jpg"}};

            // questions for the specific thumbs which invoke an exercise
            questions = c2gQuizIndicesObj;
            /*
            questions = {
                "162": {"time": 162, "problemDiv": "levenshtein-1"},
                "163": {"time": 163, "problemDiv": "non-levenshtein"},
                "164": {"time": 164, "problemDiv": "levenshtein-2"}
            };
            */

            for (j in questions) {
                questions[j].done = false;
            }

            var mods = document.getElementsByClassName('quizModule');
            for (i=0;i<mods.length;i++) {
                mods[i].style.display='inline';
            }

            // call function to add YT player
            thumbSet.createPlayer(vidName);

            if (questions.videoHeight) {
                hRatio = videoHeight / questions.videoHeight; 
            }

            if (questions.videoWidth) {
                wRatio = videoWidth / questions.videoWidth; 
            }

        },

        // add player to the page
        createPlayer: function (vid) {
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
        },

        setupQPane: function (qTime) {
            
            globalQTime = qTime;

            $('#playerdiv').fadeTo('slow', .7);
            //$('.video-overlay-question').show();
            //$('.video-overlay-hint').show();
            //console.log(questions[qTime]["problemDiv"]);
            $('#' + questions[qTime]["problemDiv"]).show();
            $('#' + questions[qTime]["problemDiv"]).css('z-index', 100);
            $('#problemarea').css('z-index', 2);
            $('#problemarea').show()
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

        },

        stripPx: function (sizeWithPx) {
            return parseInt(sizeWithPx.substr(0,sizeWithPx.search('px')));
        },

        closeQPane: function () {
            
            $("#slideIndex").show();
            
            document.getElementById('qInst').innerHTML="";
            $("div#questionPane").remove();
            $("div#questionBG").remove();

            player.playVideo();
        },

        timeDisplay: function(timeInSec) {
            var min = Math.floor(timeInSec/60);
            var sec = timeInSec - 60*min;
            if (sec<10) sec = '0'+sec;
            return ("" + min + ":" + sec);
        },

        //clears selected sides.  Then, selects the slide whose start
        //time is the nearest one less than or equal to the input time parameter
        selectSlide: function (time) {
            nearest = -1;
            for (i in slideIndices) {
                var numi = parseInt(i);
                $(slideIndices[i].displayDiv).addClass('unselected');
                $(slideIndices[i].displayDiv).removeClass('selected');
                if (numi<=time && numi>nearest) {
                    nearest=numi;
                }
            }

            if (nearest >-1) {
                var selected = slideIndices[''+nearest].displayDiv;
                $(selected).addClass('selected');
                $(selected).removeClass('unselected');
                $('#slideIndex').scrollLeft(selected.offsetLeft-($('#slideIndex').width()-$(selected).width())/2);
            }
        },

        checkTime: function () {    // display quiz
            //console.log('checkTime');
            var curTime = Math.floor(player.getCurrentTime());
            
            if (slideIndices.hasOwnProperty(curTime) || Math.abs(thumbSet.lastTime-curTime)>1){ 
                thumbSet.selectSlide(curTime);
            }
            
            if (questions.hasOwnProperty(curTime) && skipSecQ!=curTime && 
                    player.getPlayerState() == YT.PlayerState.PLAYING) {
                thumbSet.processQuiz(curTime);
            } else if (player.getPlayerState() == YT.PlayerState.PLAYING) {
                    setTimeout(thumbSet.checkTime, 200);
            }

            if (!questions.hasOwnProperty(curTime)) {
                skipSecQ=-1;
            }

            thumbSet.lastTime=curTime;
        },

        processQuiz: function (curTime) {
            player.pauseVideo();

            skipSecQ = curTime;

            if (questions.hasOwnProperty(curTime)) {
                questions[curTime].done=true;
                thumbSet.setupQPane(curTime);
            } else {
                player.playVideo();
            }
        },

        setupNavPanel: function (){
            var merged = Array();

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
                        thumbSet.addSlideIndex(sorted[i]);
                    }
                    if (questions.hasOwnProperty(sorted[i])) {
                        var tmpDiv=thumbSet.addQuizSlide(sorted[i]);
                        slideIndices[sorted[i]]={displayDiv: tmpDiv};
                    }
                }
                lastTime=sorted[i];
            }
        },

        createIndexPanel: function () {
           var indexDiv = document.createElement('div');
            $(indexDiv).attr('id','slideIndex');
              
            $('#playerdiv')[0].appendChild(indexDiv);
        },

        addSlideIndex: function (idxTime) {
            var indexDiv = document.getElementById('slideIndex');
            var tempDiv = document.createElement('div');
            $(tempDiv).addClass('divInIndex').attr('id','slideIndex'+idxTime+'s');
            var slideImg = document.createElement('img');
            slideImg.src = slideIndices[idxTime].imgsrc;
            slideIndices[idxTime].displayDiv = tempDiv;
            tempDiv.appendChild(slideImg);
            tempDiv.onclick=(function (time) {return function(evt) {
                player.seekTo(time);
                thumbSet.selectSlide(time);
            };})(idxTime);
            $('#slideIndex').append(tempDiv);
            return tempDiv;

        },

        addQuizSlide: function (idxTime) {
            var indexDiv = document.getElementById('slideIndex');
            var tempDiv = document.createElement('div');
            var greyDiv = document.createElement('div');
            $(tempDiv).addClass('divInIndex').addClass('quiz-thumb').attr('id','slideIndex'+idxTime+'s');
            $(greyDiv).addClass('greyOverlay').html("<br/><br/>Quiz");
            var slideImg = document.createElement('img');
            slideImg.src = 'q_'+idxTime+'.jpg';

            tempDiv.appendChild(greyDiv);
            tempDiv.appendChild(slideImg);

            tempDiv.onclick=(function (time) {return function(evt) {
            player.seekTo(time-1);
            thumbSet.selectSlide(time);
            };})(idxTime);
            $('#slideIndex').append(tempDiv);
            return tempDiv;
        }

    };  // end of thumbSet object definition

    return thumbSet;

};  // end of initThumbnails definition
