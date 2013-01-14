        /*
            videoURL, thumbnailPath are declared & initialized in the view_exam.html template
        */
        // Define Namespace
        var C2G = window.C2G || {};
        C2G.videoSetup = {};
        // Key methods

        C2G.videoSetup.getMS = function(seconds) {
            var sign = (seconds>=0) ? "" : "-" ;
            seconds=Math.abs(seconds);
            var M = Math.floor(seconds / 60);
            var S = Math.floor(seconds % 60);
            var Mstring = "" + M;
            var Sstring = "" + S;
            
            if (S < 10) Sstring = "0"+Sstring;
            return sign + Mstring + ":" + Sstring;
        };

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
                       thumbManifest[key.trim()] = val;
                       });

                C2G.videoSetup.slideIndices = thumbManifest;
            };

            var initThumbManifest = function () {
                return $.getJSON(thumbnailPath + "manifest.txt", "", loadThumbManifest).always(function() {
                        thumbsChecked = true;
                    });  //The request may fail if there are no thumbs, but we know we tried.
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
                var numi = parseFloat(i);
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
                $('#slideIndex').scrollLeft(selected.offsetLeft-($('#slideIndex').width()-$(selected).width()));
            } else {
                $("#slideIndex div:first-child").addClass("selected");
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
                    window.popcornVideo.play();
                    window.popcornVideo.currentTime(time)
                    C2G.videoSetup.selectSlide(time);
                };})(idxTime);
                $(tempDiv).append('<div class="thumbnailTime">'+C2G.videoSetup.getMS(idxTime)+'</div>');
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
                                 //window.popcornVideo.pause();
                                    window.popcornVideo.currentTime(time);
                                    C2G.videoSetup.selectSlide(time);
                                    C2G.videoSetup.questionController.execute(time);
                };})(idxTime);
                $(tempDiv).append('<div class="thumbnailTime">'+C2G.videoSetup.getMS(idxTime)+'</div>');
                $('#slideIndex').append(tempDiv);
                return tempDiv;
            };
  

            var setupNavPanel = function (){
                var merged = Array();

                for (time in C2G.videoSetup.slideIndices) {
                    merged.push(time)
                }

                for (time in C2G.videoSetup.questions) {
                    if (!isNaN(parseFloat(time))) {
                        merged.push(time);
                    }
                }

                var sorted = merged.sort(function(a,b){return parseFloat(a)-parseFloat(b)});

                var lastTime="-1";

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

        C2G.videoSetup.cueThumbs = function() {
            for (time in C2G.videoSetup.slideIndices) {
                window.popcornVideo.cue(time, C2G.videoSetup.handleTimeUpdate);
            }
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
                //Only show submit button on surveys, otherwise keep continue-video-btn, hide submit btn
                if (__exam_type == "survey") { 
                    if ($('#submit-button').length && $('.question:last').css('display') == "block") {
                        $('.continue-video-btn').hide();
                        $('#submit-button').show();
                    } else {
                        $('.continue-video-btn').show();
                        $('#submit-button').hide();
                    }
                } else {
                    $('#submit-button').hide();
                }
            };

            C2G.videoSetup.handleTimeUpdate = function () {
                //console.log(popcornVideo.currentTime());
                var timeInSec = window.popcornVideo.currentTime().toFixed(1);
                C2G.videoSetup.selectSlide(timeInSec);
                /*
                if ($.inArray(timeInSec, window.slideMap) != -1) {
                    $('.divInIndex.selected').removeClass('selected');
                    $('#slideIndex' + timeInSec.replace('.','-') + 's').addClass('selected');
                }
                */
            };
               
            window.popcornVideo.on('seeked', C2G.videoSetup.handleTimeUpdate);

            /*
             Don't need these
            window.popcornVideo.on('playing', function () {
                window.popcornVideo.on('timeupdate', C2G.videoSetup.handleTimeUpdate);
            });

            window.popcornVideo.on('pause', function () {
                window.popcornVideo.off('timeupdate', C2G.videoSetup.handleTimeUpdate);
            });
            */

            var setExamStage = function() {
                window.popcornVideo.pause();
                $('#demoplayer').css('position', 'absolute');
                $('#demoplayer').css('z-index', '-1');
                $('#demoplayer').hide();
                $('#slideIndex').hide();
                $('.button-tray').hide();
                $('.question').hide();
                $('.explanation').hide();
                $('.hide-button').attr('disabled', 'disabled');
            };

            var removeExamStage = function() {
                $('#slideIndex').show();
                //$('.question').hide();
                $('#exam-pane').fadeTo('fast', '0', 
                    function () {
                        $('#exam-pane').hide();
                        $('#demoplayer').css('position', 'static');
                        $('#demoplayer').css('z-index', '1');
                        $('#demoplayer').show();
                        $('.button-tray').show();
                    });
                window.popcornVideo.play();
            };
                          
            C2G.videoSetup.setExamStage = setExamStage;
            C2G.videoSetup.removeExamStage = removeExamStage;
                          
            var continueVideoBtn = document.createElement('input');
            $(continueVideoBtn).attr('type', 'button');
            $(continueVideoBtn).attr('value', 'Continue Video');
            $(continueVideoBtn).addClass('btn');
            $(continueVideoBtn).addClass('continue-video-btn');
            $('#exam-pane .exam-navigation').append($(continueVideoBtn));
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
                        $('#exam-pane').fadeTo('fast', 1.0);
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
                          
            C2G.videoSetup.questions={};
            C2G.videoSetup.showQuestion = function (questionsToShow, time) {
                return function () {
                    //flip-flop action here. There are 2 ways to get into showQuestion()
                    //The problematic one is when people click the thumbnail.
                    //That makes the time of the video exactly what the cue point is, so
                    //the cue event might fire after we close the question and resume the
                    //video and try to showQuestion() again.  To prevent this second showQuestion(),
                    //we tell the controller to disable showQuestion() the first time around.
                    C2G.videoSetup.questionController.disable(time);
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
                    $('#exam-pane').fadeTo('fast', 1.0);
                };
            };
              
                          
            C2G.videoSetup.questionController = {
                dispFns : {},
                disabledFns : {},
                install : function(time, fn) { this.dispFns[time] = fn;},
                disable : function(time) { this.disabledFns[time] = true; },
                enable : function(time) { delete this.disabledFns[time];},
                execute : function (time) {
                            console.log("exec:"+time);
                            if (!this.disabledFns.hasOwnProperty(time) &&
                                 this.dispFns.hasOwnProperty(time)) {
                                     console.log("ran");
                                     return this.dispFns[time]();
                            }
                },
                execute_closure: function(time) { return function() { C2G.videoSetup.questionController.execute(time);}},
                enable_closure: function(time) { return function() { C2G.videoSetup.questionController.enable(time);}}

            };
                          
                          
            for (q in questionTimes) {
                var cueSecond = q.split('_')[1];
                var questionsToShow = questionTimes[q];
                C2G.videoSetup.questions[cueSecond] = true;
                C2G.videoSetup.questionController.install(cueSecond, C2G.videoSetup.showQuestion(questionsToShow, cueSecond));
                window.popcornVideo.cue(cueSecond, C2G.videoSetup.questionController.execute_closure(cueSecond));
                //We then set up a cue point 1 second after the original cue point
                //when the original cue point is re-enabled.
                window.popcornVideo.cue(parseFloat(cueSecond)+.5, C2G.videoSetup.questionController.enable_closure(cueSecond));
            }
                          

            $.when(C2G.videoSetup.fetchThumbs())
            .then(C2G.videoSetup.displayThumbs)
            .then(C2G.videoSetup.cueThumbs)
            .then(console.log("DONE!"));
                          
            

        });

       

        if (video_rec_id) {
            window.onbeforeunload = function() {
            vidTime = Math.floor(window.popcornVideo.currentTime());
            duration = window.popcornVideo.duration();
            $.ajax({type:"POST", url: "/videos/save/", async:false, data: {videoRec: video_rec_id, playTime: vidTime, duration: duration, csrfmiddlewaretoken: csrf_token}});
            }
	    }
