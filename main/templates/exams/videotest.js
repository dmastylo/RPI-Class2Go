        var videoURL = 'http://www.youtube.com/embed/RD5VCBprVvo?autoplay=0&wmode=transparent&fs=0&controls=0&rel=0&modestbranding=1&showinfo=0&start=0&enablejsapi=1&disablekb=1&amp;';
        //var videoURL = 'http://www.youtube.com/watch?v=RD5VCBprVvo?autoplay=0&wmode=transparent&fs=0&controls=0&rel=0&modestbranding=1&showinfo=0&start=0&enablejsapi=1&disablekb=1&amp;';
        var thumbnailData = {"0":{"imgsrc":"img001.jpeg"},"31":{"imgsrc":"img032.jpeg"},"40":{"imgsrc":"img041.jpeg"},"62":{"imgsrc":"img063.jpeg"},"135":{"imgsrc":"img136.jpeg"},"136":{"imgsrc":"img137.jpeg"},"179":{"imgsrc":"img180.jpeg"},"259":{"imgsrc":"img260.jpeg"},"292":{"imgsrc":"img293.jpeg"},"353":{"imgsrc":"img354.jpeg"},"354":{"imgsrc":"img355.jpeg"},"355":{"imgsrc":"img356.jpeg"} /*,"385":{"imgsrc":"img386.jpeg"}*/};
        var slideIndices = thumbnailData;
        var questionData = {"184": {"fileName": "arp_q1.html", "problemDiv": 974, "order": 0, "time": 384}, "385": {"fileName": "arp_q2.html", "problemDiv": 975, "order": 1, "time": 385}, "385": {"fileName": "arp_q3.html", "problemDiv": 976, "order": 2, "time": 386}};
        var questions = questionData;
        var imgPath = "http://prod-c2g.s3-website-us-west-2.amazonaws.com/networking/Fall2012/videos/1201/jpegs/";
        var popcornVideo = Popcorn.youtube("#demoplayer", videoURL);

        var addSlideIndex = function (idxTime) {
            var indexDiv = document.getElementById('slideIndex');
            var tempDiv = document.createElement('div');
            $(tempDiv).addClass('divInIndex').attr('id','slideIndex'+idxTime.replace('.','-')+'s');
            var slideImg = document.createElement('img');
            slideImg.src = imgPath + slideIndices[idxTime].imgsrc;
            $(slideImg).attr('alt', 'Jump to section ' + idxTime + ' of the video');
            slideIndices[idxTime].displayDiv = tempDiv;
            tempDiv.appendChild(slideImg);
            tempDiv.onclick=(function (time) {return function(evt) {
                //player.seekTo(time);
                popcornVideo.play(time);
                //thumbSet.selectSlide(time);
                selectSlide(time);
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
                                popcornVideo.play(time);
                                //thumbSet.selectSlide(time);
                                selectSlide(time);
            };})(idxTime);
            $('#slideIndex').append(tempDiv);
            return tempDiv;
        };

        var setupNavPanel = function (){
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
                        //thumbSet.addSlideIndex(sorted[i]);
                        addSlideIndex(sorted[i]);
                    }
                    if (questions.hasOwnProperty(sorted[i])) {
                        //var tmpDiv=thumbSet.addQuizSlide(sorted[i]);
                        var tmpDiv=addQuizSlide(sorted[i]);
                        slideIndices[sorted[i]]={displayDiv: tmpDiv}; //Quiz takes precedence and overwrites if both quiz and thumb are at the same time
                    }
                }
                lastTime=sorted[i];
            }

            window.slideMap = sorted;
        };

        var selectSlide = function (time) {
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
                //console.log(nearest);
                //console.log(slideIndices[''+nearest]);
                //console.log(slideIndices);
                var selected = slideIndices[''+nearest].displayDiv;
                $(selected).addClass('selected');
                $(selected).removeClass('unselected');
                $('#slideIndex').scrollLeft(selected.offsetLeft-($('#slideIndex').width()-$(selected).width())/2);
            }
        };

        var handleTimeUpdate = function () {
            //console.log(popcornVideo.currentTime());
            var timeInSec = Math.floor(popcornVideo.currentTime()).toFixed(1);
            selectSlide(timeInSec);
            /*
            console.log(window.slideMap);
            console.log(timeInSec);
            console.log($.inArray(timeInSec, window.slideMap));
            if ($.inArray(timeInSec, window.slideMap) != -1) {
                console.log('in array!');
                $('.divInIndex.selected').removeClass('selected');
                console.log($('#slideIndex' + timeInSec + 's'));
                $('#slideIndex' + timeInSec.replace('.','-') + 's').addClass('selected');
            }
            */
        };
    
        $(document).ready(function() {

            setupNavPanel()
    
            popcornVideo.on('playing', function () {
                popcornVideo.on('timeupdate', handleTimeUpdate);
            });

            popcornVideo.on('pause', function () {
                popcornVideo.off('timeupdate', handleTimeUpdate);
            });

            var setExamStage = function() {
                popcornVideo.pause();
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
                popcornVideo.play();
            };

            var continueVideoBtn = document.createElement('input');
            $(continueVideoBtn).attr('type', 'button');
            $(continueVideoBtn).attr('value', 'Continue Video');
            $(continueVideoBtn).addClass('btn');
            $(continueVideoBtn).addClass('continue-video-btn');
            $('#exam-pane').append($(continueVideoBtn));
            //$(continueVideoBtn).click(removeExamStage);

            var configureExamButton = function (mode) {
                $(continueVideoBtn).unbind('click');
                if (mode == "multi-question") {
                    $(continueVideoBtn).attr('value', 'Next Question');
                    $(continueVideoBtn).click(function () {
                        setExamStage();
                        $('.question').eq(2).show();
                        $('#exam-pane').fadeTo('slow', 1.0);
                        $(continueVideoBtn).attr('value', 'Resume Video');
                        $(continueVideoBtn).click(removeExamStage);
                    });
                } else { 
                    $(continueVideoBtn).attr('value', 'Resume Video');
                    $(continueVideoBtn).click(removeExamStage);
                }
            };

            popcornVideo.cue('184', function () {
                    setExamStage();
                    $('.question').eq(0).show();
                    $('#exam-pane').fadeTo('slow', 1.0);
                    configureExamButton();
                }
            );

            popcornVideo.cue('385', function () {
                    setExamStage();
                    $('.question').eq(1).show();
                    $('#exam-pane').fadeTo('slow', 1.0);
                    configureExamButton("multi-question");
                }
            );

            /*
            popcornVideo.cue('385', function () {
                setExamStage();
                $('.question').eq(2).show();
                $('#exam-pane').fadeTo('slow', 1.0);}
            );
            */
        });
