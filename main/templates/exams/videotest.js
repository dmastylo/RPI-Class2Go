        /*
            videoURL, thumbnailPath are declared & initialized in the view_exam.html template
        */
        // Define Namespace
        var C2G = window.C2G || {};
        C2G.videoSetup = {};

        // Key methods
        C2G.videoSetup.fetchThumbs = function () {

            // set up deferred object for proper chaining of function calls
            var fetchDeferred = $.Deferred();

            // private vars
            var thumbManifest = {};
            var psManifest = {};
            var thumbsChecked = false;
            var psChecked = false;

            // private methods
            var loadThumbManifest = function (data, textStatus, jqXHR) {

                $.each(data, function (key, val) {
                       $.each(val, function (k, v) {
                              if (k == "imgsrc") {
                              val[k] = thumbnailPath + v;
                              }
                              })
                       thumbManifest[parseInt(key)] = val;
                       });

                C2G.videoSetup.slideIndices = thumbManifest;
            };

            // TODO: This function should go away soon, as real data will be in XML metadata
            var loadPSManifest = function (data, textStatus, jqXHR) {
                $.each(data, function (key, val) {
                       $.each(val, function (k, v) {
                              if (k == "imgsrc") {
                              val[k] = thumbnailPath + v;
                              }
                              })
                       psManifest[parseInt(key)] = val;
                       });
                C2G.videoSetup.questions = psManifest;
            };

            var initThumbManifest = function () {
                return $.getJSON(thumbnailPath + "manifest.txt", "", loadThumbManifest).always(function() {
                        thumbsChecked = true;
                    });  //The request may fail if there are no thumbs, but we know we tried.
            }

            var initPSManifest = function () {
                return $.getJSON("/get_video_exercises?video_id={{video.id}}", "", loadPSManifest).always(function() {
                    psChecked = true;
                });  //The request may fail if there are no exercises, but we know we tried.
            }

            $.when(initThumbManifest()).then(function () {
                //console.log("thumbsChecked: " + thumbsChecked);
                //console.log("psChecked: " + psChecked);
            }).then(function () {fetchDeferred.resolve();});

            return fetchDeferred.promise();
        };

        C2G.videoSetup.selectSlide = function (time) {
            nearest = -1;
            for (i in C2G.videoSetup.slideIndices) {
                var numi = parseInt(i);
                $(C2G.videoSetup.slideIndices[i].displayDiv).addClass('unselected');
                $(C2G.videoSetup.slideIndices[i].displayDiv).removeClass('selected');
                if (numi<=time && numi>nearest) {
                    nearest=numi;
                }
            }

            if (nearest >-1) {
                var selected = C2G.videoSetup.slideIndices[''+nearest].displayDiv;
                $(selected).addClass('selected');
                $(selected).removeClass('unselected');
                $('#slideIndex').scrollLeft(selected.offsetLeft-($('#slideIndex').width()-$(selected).width())/2);
            }
        };

        C2G.videoSetup.displayThumbs = function () {

            var imgPath = "";

            var addSlideIndex = function (idxTime) {
                var indexDiv = document.getElementById('slideIndex');
                var tempDiv = document.createElement('div');
                $(tempDiv).addClass('divInIndex').attr('id','slideIndex'+idxTime.replace('.','-')+'s');
                var slideImg = document.createElement('img');
                slideImg.src = imgPath + C2G.videoSetup.slideIndices[idxTime].imgsrc;
                $(slideImg).attr('alt', 'Jump to section ' + idxTime + ' of the video');
                C2G.videoSetup.slideIndices[idxTime].displayDiv = tempDiv;
                tempDiv.appendChild(slideImg);
                tempDiv.onclick=(function (time) {return function(evt) {
                    //player.seekTo(time);
                    window.popcornVideo.play(time);
                    //thumbSet.selectSlide(time);
                    C2G.videoSetup.selectSlide(time);
                };})(idxTime);
                $('#slideIndex').append(tempDiv);
                return tempDiv;

            };

            var addQuizSlide = function (idxTime) {
                var indexDiv = document.getElementById('slideIndex');
                var tempDiv = document.createElement('div');
                $(tempDiv).addClass('divInIndex').addClass('quiz-thumb').attr('id','slideIndex'+idxTime.replace('.','-')+'s');
                var slideImg = document.createElement('img');
                slideImg.src = '/static/graphics/core/question.png';
                $(slideImg).attr('alt', 'Go to quiz at section ' + idxTime);
                tempDiv.appendChild(slideImg);

                tempDiv.onclick=(function (time) {return function(evt) {
                                    //player.seekTo(time-0.5);
                                    window.popcornVideo.play(time);
                                    //thumbSet.selectSlide(time);
                                    C2G.videoSetup.selectSlide(time);
                };})(idxTime);
                $('#slideIndex').append(tempDiv);
                return tempDiv;
            };

            var setupNavPanel = function (){
                var merged = Array();

                for (time in C2G.videoSetup.slideIndices) {
                    merged.push(time)
                }

                for (time in C2G.videoSetup.questions) {
                    if (!isNaN(parseInt(time))) {
                        merged.push(time);
                    }
                }

                var sorted = merged.sort(function(a,b){return parseInt(a)-parseInt(b)});

                var lastTime=-1;

                for (i in sorted) {
                    if (sorted[i] != lastTime) {
                        if (C2G.videoSetup.slideIndices.hasOwnProperty(sorted[i])) {
                            //thumbSet.addSlideIndex(sorted[i]);
                            addSlideIndex(sorted[i]);
                        }
                        if (C2G.videoSetup.questions.hasOwnProperty(sorted[i])) {
                            //var tmpDiv=thumbSet.addQuizSlide(sorted[i]);
                            var tmpDiv=addQuizSlide(sorted[i]);
                            C2G.videoSetup.slideIndices[sorted[i]]={displayDiv: tmpDiv}; //Quiz takes precedence and overwrites if both quiz and thumb are at the same time
                        }
                    }
                    lastTime=sorted[i];
                }

                window.slideMap = sorted;
            };

            setupNavPanel();

        };

        $(document).ready(function() {
            /*
            Chain of events:
            1. Fetch video, cue question breakpoints via Popcorn
            2. Fetch screenshot thumbnails, quiz thumbnails manifests 
            2. Load thumbnail strip
            4. ???
            5. PROFIT!!!
            */

            window.popcornVideo = Popcorn.youtube("#demoplayer", videoURL);

            C2G.checkSubmitStatus = function () {
                if ($('#survey-submit').length && $('.question:last').css('display') == "block") {
                    $('.continue-video-btn').hide();
                    $('#survey-submit').show();
                }
            };

            C2G.videoSetup.handleTimeUpdate = function () {
                //console.log(popcornVideo.currentTime());
                var timeInSec = Math.floor(window.popcornVideo.currentTime()).toFixed(1);
                C2G.videoSetup.selectSlide(timeInSec);
                /*
                if ($.inArray(timeInSec, window.slideMap) != -1) {
                    $('.divInIndex.selected').removeClass('selected');
                    $('#slideIndex' + timeInSec.replace('.','-') + 's').addClass('selected');
                }
                */
            };

            window.popcornVideo.on('playing', function () {
                window.popcornVideo.on('timeupdate', C2G.videoSetup.handleTimeUpdate);
            });

            window.popcornVideo.on('pause', function () {
                window.popcornVideo.off('timeupdate', C2G.videoSetup.handleTimeUpdate);
            });

            var setExamStage = function() {
                window.popcornVideo.pause();
                $('#demoplayer').css('position', 'absolute');
                $('#demoplayer').css('z-index', '-1');
                $('#demoplayer').hide();
                $('#slideIndex').hide();
                $('.question').hide();
            };

            var removeExamStage = function() {
                $('#slideIndex').show();
                //$('.question').hide();
                $('#exam-pane').fadeTo('slow', '0', 
                    function () {
                        $('#exam-pane').hide();
                        $('#demoplayer').css('position', 'static');
                        $('#demoplayer').css('z-index', '1');
                        $('#demoplayer').show();
                    });
                window.popcornVideo.play();
            };

            var continueVideoBtn = document.createElement('input');
            $(continueVideoBtn).attr('type', 'button');
            $(continueVideoBtn).attr('value', 'Continue Video');
            $(continueVideoBtn).addClass('btn');
            $(continueVideoBtn).addClass('continue-video-btn');
            $('#exam-pane').append($(continueVideoBtn));
            //$(continueVideoBtn).click(removeExamStage);

            var currentQuestionId = "";
            var configureExamButton = function (mode, questionArray) {
                $(continueVideoBtn).unbind('click');
                if (mode == "multi-question") {
                    $(continueVideoBtn).attr('value', 'Next Question');
                    $(continueVideoBtn).click(function () {
                        var curQ = $('#' + currentQuestionId);
                        console.log("curQ...");
                        console.log($(curQ));
                        setExamStage();
                        currentQuestionId = $(curQ).next().attr('id');
                        console.log("Now currentQuestionId...");
                        console.log(currentQuestionId);
                        $(curQ).next().show(0, C2G.checkSubmitStatus);
                        $('#exam-pane').fadeTo('slow', 1.0);
                        console.log("questionArray[questionArray.length - 1]...");
                        console.log(questionArray[questionArray.length - 1]);
                        if (currentQuestionId == questionArray[questionArray.length - 1]) {
                            $(continueVideoBtn).attr('value', 'Resume Video');
                            $(continueVideoBtn).click(removeExamStage);
                        }
                    });
                } else { 
                    $(continueVideoBtn).attr('value', 'Resume Video');
                    $(continueVideoBtn).click(removeExamStage);
                }
            };

            for (q in questionTimes) {
                
                var cueSecond = q.split('_')[1];
                var questionsToShow = questionTimes[q];

                var showQuestion = function (questionsToShow) {
                    return function () {
                        setExamStage();
                        var firstQuestionId = "";
                        if ($.isArray(questionsToShow)) {
                            firstQuestionId = questionsToShow[0];
                            if (questionsToShow.length > 1) {
                                configureExamButton("multi-question", questionsToShow);
                            } else {
                                configureExamButton();
                            }
                        } else {
                            firstQuestionId = questionsToShow;
                            configureExamButton();
                        } 
                        $('#' + firstQuestionId).show(0, C2G.checkSubmitStatus);
                        currentQuestionId = firstQuestionId;
                        $('#exam-pane').fadeTo('slow', 1.0);
                    };
                };

                window.popcornVideo.cue(cueSecond, showQuestion(questionsToShow));

            }

            $.when(C2G.videoSetup.fetchThumbs())
            .then(C2G.videoSetup.displayThumbs)
            .then(console.log("DONE!"));

        });
