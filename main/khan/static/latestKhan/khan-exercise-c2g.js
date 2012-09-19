/* khan-exercise.js

    The main entry point here is actually the loadScripts method which is defined
    as Khan.loadScripts and then evaluated around line 500.

    When this loadScripts is called, it loads in many of the pre-reqs and then
    calls, one way or another, setUserExercise concurrently with loadModules.

    setProblemNum updates some instance vars that get looked at by other functions.

    loadModules takes care of loading an individual exercise's prereqs (i.e.
    word problems, etc). It _also_ loads in the khan academy site skin and
    exercise template via injectSite which runs prepareSite first then
    makeProblemBag and makeProblem when it finishes loading dependencies.

    pepareSite and makeProblem are both fairly heavyweight functions.

    If you are trying to register some behavior when the page loads, you
    probably want it to go in prepareSite. (which also registers server-initiated
    behavior via api.js) as well. By the time prepareSite is called, jquery and
    any core plugins are already available.

    If you are trying to do something each time a problem loads, you probably
    want to look at makeProblem.

    At the end of evaluation, the inner Khan object is returned/exposed as well
    as the inner Util object.



    Catalog of events fired on the Khan object by khan-exercises:

    * newProblem -- when a new problem has completely finished rendering

    * hintUsed -- when a hint has been used by the user

    * allHintsUsed -- when all possible hints have been used by the user

    * checkAnswer -- when the user attempts to check an answer, incorrect or
      correct

    * problemDone -- when the user has completed a problem which, in this case,
      usually means supplying the correct answer

    * attemptSaved -- when an attempt has been recorded successfully via the
      API

    * attemptError -- when an error occurs during an API attempt

    * apiRequestStarted / apiRequestEnded -- when an API request is sent
      outbound or completed, respectively. Listeners can keep track of whether
      or not khan-exercises is still waiting on API responses.

    * exerciseLoaded:[exercise-id] -- when an exercise and all of its
      dependencies are loaded and ready to render

    * updateUserExercise -- when an updated userExercise has been received
      and is being used by khan-exercises, either via the result of an API
      call or initialization
*/
var KhanC2G={};

var Khan = (function() {
    function warn(message, showClose) {
        $(function() {
            var warningBar = $("#warning-bar");
            $("#warning-bar-content").html(message);
            if (showClose) {
                warningBar.addClass("warning")
                      .children("#warning-bar-close").show();
            } else {
                warningBar.addClass("error")
                      .children("#warning-bar-close").hide();
            }
            warningBar.fadeIn("fast");
        });
    }

    // Prime numbers used for jumping through exercises
    var primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
    47, 53, 59, 61, 67, 71, 73, 79, 83],

    /*
    ===============================================================================
    Crc32 is a JavaScript function for computing the CRC32 of a string
    ...............................................................................

    Version: 1.2 - 2006/11 - http://noteslog.com/category/javascript/

    -------------------------------------------------------------------------------
    Copyright (c) 2006 Andrea Ercolino
    http://www.opensource.org/licenses/mit-license.php
    ===============================================================================
    */

    // CRC32 Lookup Table
    table = "00000000 77073096 EE0E612C 990951BA 076DC419 706AF48F E963A535 " +
            "9E6495A3 0EDB8832 79DCB8A4 E0D5E91E 97D2D988 09B64C2B 7EB17CBD " +
            "E7B82D07 90BF1D91 1DB71064 6AB020F2 F3B97148 84BE41DE 1ADAD47D " +
            "6DDDE4EB F4D4B551 83D385C7 136C9856 646BA8C0 FD62F97A 8A65C9EC " +
            "14015C4F 63066CD9 FA0F3D63 8D080DF5 3B6E20C8 4C69105E D56041E4 " +
            "A2677172 3C03E4D1 4B04D447 D20D85FD A50AB56B 35B5A8FA 42B2986C " +
            "DBBBC9D6 ACBCF940 32D86CE3 45DF5C75 DCD60DCF ABD13D59 26D930AC " +
            "51DE003A C8D75180 BFD06116 21B4F4B5 56B3C423 CFBA9599 B8BDA50F " +
            "2802B89E 5F058808 C60CD9B2 B10BE924 2F6F7C87 58684C11 C1611DAB " +
            "B6662D3D 76DC4190 01DB7106 98D220BC EFD5102A 71B18589 06B6B51F " +
            "9FBFE4A5 E8B8D433 7807C9A2 0F00F934 9609A88E E10E9818 7F6A0DBB " +
            "086D3D2D 91646C97 E6635C01 6B6B51F4 1C6C6162 856530D8 F262004E " +
            "6C0695ED 1B01A57B 8208F4C1 F50FC457 65B0D9C6 12B7E950 8BBEB8EA " +
            "FCB9887C 62DD1DDF 15DA2D49 8CD37CF3 FBD44C65 4DB26158 3AB551CE " +
            "A3BC0074 D4BB30E2 4ADFA541 3DD895D7 A4D1C46D D3D6F4FB 4369E96A " +
            "346ED9FC AD678846 DA60B8D0 44042D73 33031DE5 AA0A4C5F DD0D7CC9 " +
            "5005713C 270241AA BE0B1010 C90C2086 5768B525 206F85B3 B966D409 " +
            "CE61E49F 5EDEF90E 29D9C998 B0D09822 C7D7A8B4 59B33D17 2EB40D81 " +
            "B7BD5C3B C0BA6CAD EDB88320 9ABFB3B6 03B6E20C 74B1D29A EAD54739 " +
            "9DD277AF 04DB2615 73DC1683 E3630B12 94643B84 0D6D6A3E 7A6A5AA8 " +
            "E40ECF0B 9309FF9D 0A00AE27 7D079EB1 F00F9344 8708A3D2 1E01F268 " +
            "6906C2FE F762575D 806567CB 196C3671 6E6B06E7 FED41B76 89D32BE0 " +
            "10DA7A5A 67DD4ACC F9B9DF6F 8EBEEFF9 17B7BE43 60B08ED5 D6D6A3E8 " +
            "A1D1937E 38D8C2C4 4FDFF252 D1BB67F1 A6BC5767 3FB506DD 48B2364B " +
            "D80D2BDA AF0A1B4C 36034AF6 41047A60 DF60EFC3 A867DF55 316E8EEF " +
            "4669BE79 CB61B38C BC66831A 256FD2A0 5268E236 CC0C7795 BB0B4703 " +
            "220216B9 5505262F C5BA3BBE B2BD0B28 2BB45A92 5CB36A04 C2D7FFA7 " +
            "B5D0CF31 2CD99E8B 5BDEAE1D 9B64C2B0 EC63F226 756AA39C 026D930A " +
            "9C0906A9 EB0E363F 72076785 05005713 95BF4A82 E2B87A14 7BB12BAE " +
            "0CB61B38 92D28E9B E5D5BE0D 7CDCEFB7 0BDBDF21 86D3D2D4 F1D4E242 " +
            "68DDB3F8 1FDA836E 81BE16CD F6B9265B 6FB077E1 18B74777 88085AE6 " +
            "FF0F6A70 66063BCA 11010B5C 8F659EFF F862AE69 616BFFD3 166CCF45 " +
            "A00AE278 D70DD2EE 4E048354 3903B3C2 A7672661 D06016F7 4969474D " +
            "3E6E77DB AED16A4A D9D65ADC 40DF0B66 37D83BF0 A9BCAE53 DEBB9EC5 " +
            "47B2CF7F 30B5FFE9 BDBDF21C CABAC28A 53B39330 24B4A3A6 BAD03605 " +
            "CDD70693 54DE5729 23D967BF B3667A2E C4614AB8 5D681B02 2A6F2B94 " +
            "B40BBE37 C30C8EA1 5A05DF1B 2D02EF8D",

    /* Number */
    crc32 = function(str, crc) {
        if (crc == window.undefined) {
            crc = 0;
        }
        var n = 0; //a number between 0 and 255
        var x = 0; //a hex number

        crc = crc ^ (-1);
        for (var i = 0, iTop = str.length; i < iTop; i++) {
            n = (crc ^ str.charCodeAt(i)) & 0xFF;
            x = "0x" + table.substr(n * 9, 8);
            crc = (crc >>> 8) ^ x;
        }
        return Math.abs(crc ^ (-1));
    },

    userExercise = undefined,

    // Check to see if we're in test mode
    testMode = typeof Exercises === "undefined",

    // The main server we're connecting to for saving data
    server = typeof apiServer !== "undefined" ? apiServer :
        testMode ? "http://localhost:8080" : "",

    // The ID, filename, and name of the exercise -- these will only be set here in testMode
    exerciseId = ((/([^\/.]+)(?:\.html)?$/.exec(window.location.pathname) || [])[1]) || "",
    exerciseFile = exerciseId + ".html",
    exerciseName = deslugify(exerciseId),

    // Bin users into a certain number of realms so that
    // there is some level of reproducability in their questions
    bins = 200,

    // Number of past problems to consider when avoiding duplicates
    dupWindowSize = 5,

    // The seed information
    randomSeed,

    // Holds the current username
    user = null,
    userCRC32,

    // The current problem and its corresponding exercise
    problem,
    exercise,

    // The number of the current problem that we're on
    problemNum = 1,

    // Info for constructing the seed
    seedOffset = 0,
    jumpNum = 1,
    problemSeed = 0,
    seedsSkipped = 0,
    consecutiveSkips = 0,

    problemID,

    // The current validator function
    validator,

    hints,

    // The exercise elements
    exercises,

    // Where we are in the shuffled list of problem types
    problemBag,
    problemBagIndex = 0,

    // How many problems are we doing? (For the fair shuffle bag.)
    problemCount = 10,

    // For saving problems to the server
    hintsUsed,
    lastAction,
    attempts,

    guessLog,
    userActivityLog,

    // A map of jQuery queues for serially sending and receiving AJAX requests.
    requestQueue = {},

    // Debug data dump
    dataDump = {
        "exercise": exerciseId,
        "problems": [],
        "issues": 0
    },

    // Dict of exercise ids that are loading.
    // Values are number of remote exercises that are currently
    // pending in the middle of a load.
    loadingExercises = {},

    // C2G: manual location for Khan static files
    urlBaseOverride="/static/latestKhan/",
    urlBase = typeof urlBaseOverride !== "undefined" ? urlBaseOverride :
        testMode ? "../" : "/khan-exercises/",

    // Use later for finding exercises -- they're not stored with the static Khan files, but in S3
    urlBaseExercise = "../",

    lastFocusedSolutionInput = null,

    issueError = "Communication with GitHub isn't working. Please file " +
        "the issue manually at <a href=\"" +
        "http://github.com/Khan/khan-exercises/issues/new\">GitHub</a>. " +
        "Please reference exercise: " + exerciseId + ".",
    issueSuccess = function(url, title, suggestion) {
        return ["Thank you for your feedback! Your issue has been created and can be ",
            "found at the following link:",
            "<p><a id=\"issue-link\" href=\"", url, "\">", title, "</a>",
            "<p>", suggestion, "</p>"].join("");
    },
    issueIntro = "Remember to check the hints and double check your math. All provided information will be public. Thanks for your help!",

    // True once we've sent a request to load all modules
    modulesLoaded = false,

    // jQuery.Deferred object that registers
    // callbacks to be run when all modules are done
    // loading.
    modulesDeferred = null,

    gae_bingo = window.gae_bingo || { bingo: function() {} },

    // The ul#examples (keep in a global because we need to modify it even when it's out of the DOM)
    examples = null;

    // Add in the site stylesheets
    if (testMode) {
        (function() {
            var link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = urlBase + "css/khan-site.css";
            document.getElementsByTagName("head")[0].appendChild(link);

            link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = urlBase + "css/khan-exercise.css";
            document.getElementsByTagName("head")[0].appendChild(link);

            link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = urlBase + "css/c2g-khan.css";
            document.getElementsByTagName("head")[0].appendChild(link);
        })();
    }

    // The main Khan Module
    var Khan = {
        modules: {},
            
        getExercises:function() {return exercises;},
        getProblems:function() {return exercises.children(".problems").children();},


        // So modules can use file paths properly
        urlBase: urlBase,

        moduleDependencies: {
            "math": [{
                src: urlBase + "utils/MathJax/1.1a/MathJax.js?config=KAthJax-62e7a7b628ba168df6b9cd3de8feac38"
            }, "raphael"],

            // Load Raphael locally because IE8 has a problem with the 1.5.2 minified release
            // http://groups.google.com/group/raphaeljs/browse_thread/thread/c34c75ad8d431544

            // The normal module dependencies.
            "calculus": ["math", "expressions", "polynomials"],
            "exponents": ["math", "math-format"],
            "kinematics": ["math"],
            "math-format": ["math", "expressions"],
            "polynomials": ["math", "expressions"],
            "stat": ["math"],
            "word-problems": ["math"],
            "derivative-intuition": ["jquery.mobile.vmouse"],
            "unit-circle": ["jquery.mobile.vmouse"],
            "interactive": ["jquery.mobile.vmouse"],
            "mean-and-median": ["stat"],
            "math-model": ["ast"],
            "simplify": ["math-model", "ast", "expr-helpers", "expr-normal-form", "steps-helpers"],
            "congruency": ["angles", "interactive"]
        },

        warnTimeout: function() {
            warn("Your internet might be too slow to see an exercise. Refresh the page " +
                'or <a href="" id="warn-report">report a problem</a>.', false);
            $("#warn-report").click(function(e) {
                e.preventDefault();
                $("#report").click();
            });
        },

        warnFont: function() {
            var enableFontDownload = "enable font download in your browser";
            if ($.browser.msie) {
                enableFontDownload = '<a href="http://missmarcialee.com/2011/08/how-to-enable-font-download-in-internet-explorer-8/"  target="_blank">enable font download</a>';
            }

            warn("You should " + enableFontDownload + " to improve the appearance of math expressions.", true);
        },

        require: function(mods) {
            if (mods == null) {
                return;
            } else if (typeof mods === "string") {
                mods = mods.split(" ");
            } else if (!$.isArray(mods)) {
                mods = [mods];
            }

            $.each(mods, function(i, mod) {
                var src, deps;

                if (typeof mod === "string") {
                    var cachebust = "";
                    if (testMode && Khan.query.nocache != null) {
                        cachebust = "?" + Math.random();
                    }
                    src = urlBase + "utils/" + mod + ".js" + cachebust;
                    deps = Khan.moduleDependencies[mod];
                    mod = {
                        src: src,
                        name: mod
                    };
                } else {
                    src = mod.src;
                    deps = mod.dependencies;
                    delete mod.dependencies;
                }

                if (!Khan.modules[src]) {
                    Khan.modules[src] = mod;
                    Khan.require(deps);
                }

            });
        },

        // Populate this with modules
        Util: {
            // http://burtleburtle.net/bob/hash/integer.html
            // This is also used as a PRNG in the V8 benchmark suite
            random: function() {
                // Robert Jenkins' 32 bit integer hash function.
                var seed = randomSeed;
                seed = ((seed + 0x7ed55d16) + (seed << 12)) & 0xffffffff;
                seed = ((seed ^ 0xc761c23c) ^ (seed >>> 19)) & 0xffffffff;
                seed = ((seed + 0x165667b1) + (seed << 5)) & 0xffffffff;
                seed = ((seed + 0xd3a2646c) ^ (seed << 9)) & 0xffffffff;
                seed = ((seed + 0xfd7046c5) + (seed << 3)) & 0xffffffff;
                seed = ((seed ^ 0xb55a4f09) ^ (seed >>> 16)) & 0xffffffff;
                return (randomSeed = (seed & 0xfffffff)) / 0x10000000;
            },

            crc32: crc32
        },

        // Load in a collection of scripts, execute callback upon completion
        loadScripts: function(urls, callback) {
            var loaded = 0,
                loading = urls.length,
                head = document.getElementsByTagName("head")[0];

            callback || (callback = function() {});

            for (var i = 0; i < loading; i++) { (function(mod) {

                var isMathJax = mod.src.indexOf("/MathJax/") !== -1,
                    onScriptLoad = function() {
                        // Bump up count of scripts loaded
                        loaded++;

                        // Run callback in case we're finished loading all
                        // modules
                        runCallback();
                    };

                if (!testMode && mod.src.indexOf("/khan-exercises/") === 0 && !isMathJax) {
                    // Don't bother loading khan-exercises content in production
                    // mode, this content is already packaged up and available
                    // (*unless* it's MathJax, which is silly still needs to be loaded)
                    loaded++;
                    return;
                }

                // Adapted from jQuery getScript (ajax/script.js)
                var script = document.createElement("script");
                script.async = "async";

                for (var prop in mod) {
                    script[prop] = mod[prop];
                }

                script.onerror = function() {
                    // No error in IE, but this is mostly for debugging during development so it's probably okay
                    // http://stackoverflow.com/questions/2027849/how-to-trigger-script-onerror-in-internet-explorer
                    Khan.error("Error loading script " + script.src);
                };

                script.onload = script.onreadystatechange = function() {
                    if (!script.readyState || (/loaded|complete/).test(script.readyState)) {
                        // Handle memory leak in IE
                        script.onload = script.onreadystatechange = null;

                        // Remove the script
                        if (script.parentNode) {
                            script.parentNode.removeChild(script);
                        }

                        // Dereference the script
                        script = undefined;

                        if (isMathJax) {
                            // If we're loading MathJax, don't bump up the
                            // count of loaded scripts until MathJax is done
                            // loading all of its dependencies.
                            MathJax.Hub.Queue(onScriptLoad);
                        } else {
                            onScriptLoad();
                        }
                    }
                };

                head.appendChild(script);
            })(urls[i]); }
            
            runCallback();

            function runCallback() {
                if (callback && loading === loaded) {
                    callback();
                }
            }
        },

        // Query String Parser
        // Original from:
        // http://stackoverflow.com/questions/901115/get-querystring-values-in-javascript/2880929#2880929
        queryString: function() {
            var urlParams = {},
                e,
                a = /\+/g,  // Regex for replacing addition symbol with a space
                r = /([^&=]+)=?([^&]*)/g,
                d = function(s) { return decodeURIComponent(s.replace(a, " ")); },
                q = window.location.search.substring(1);

            while ((e = r.exec(q))) {
                urlParams[d(e[1])] = d(e[2]);
            }

            return urlParams;
        },

        // Display error messages
        error: function() {
            if (typeof console !== "undefined") {
                $.each(arguments, function(ix, arg) {
                    console.error(arg);
                });
            }
        },

        scratchpad: (function() {
            var disabled = false, wasVisible, pad;

            var actions = {
                disable: function() {
                    wasVisible = actions.isVisible();
                    actions.hide();

                    $("#scratchpad-show").hide();
                    $("#scratchpad-not-available").show();
                    disabled = true;
                },

                enable: function() {
                    if (wasVisible) {
                        actions.show();
                        wasVisible = false;
                    }

                    $("#scratchpad-show").show();
                    $("#scratchpad-not-available").hide();
                    disabled = false;
                },

                isVisible: function() {
                    return $("#scratchpad").is(":visible");
                },

                show: function() {

                    if (actions.isVisible()) {
                        return;
                    }

                    var makeVisible = function() {
                        $("#workarea, #hintsarea").css("padding-left", 60);
                        $("#scratchpad").show();
                        $("#scratchpad-show").text("Hide scratchpad");

                        // If pad has never been created or if it's empty
                        // because it was removed from the DOM, recreate a new
                        // scratchpad.
                        if (!pad || !$("#scratchpad div").children().length) {
                            pad = new Scratchpad($("#scratchpad div")[0]);
                        }
                    };

                    if (!pad) {
                        Khan.loadScripts([{src: urlBase + "utils/scratchpad.js"}], makeVisible);
                    } else {
                        makeVisible();
                    }
                },

                hide: function() {
                    if (!actions.isVisible()) {
                        return;
                    }

                    $("#workarea, #hintsarea").css("padding-left", 0);
                    $("#scratchpad").hide();
                    $("#scratchpad-show").text("Show scratchpad");
                },

                toggle: function() {
                    actions.isVisible() ? actions.hide() : actions.show();
                },

                clear: function() {
                    if (pad) {
                        pad.clear();
                    }
                },

                resize: function() {
                    if (pad) {
                        pad.resize();
                    }
                }
            };

            return actions;
        })(),

        relatedVideos: {
            exercise: null,
            cache: {},

            getVideos: function() {
                return this.cache[this.exercise.name] || [];
            },

            setVideos: function(exercise) {

                if (exercise.relatedVideos) {
                    this.cache[exercise.name] = exercise.relatedVideos;
                }

                this.exercise = exercise;
                this.render();
            },

            showThumbnail: function(index) {
                $("#related-video-list .related-video-list li").each(function(i, el) {
                    if (i === index) {
                        $(el)
                            .find("a.related-video-inline").hide().end()
                            .find(".thumbnail").show();
                    }
                    else {
                        $(el)
                            .find("a.related-video-inline").show().end()
                            .find(".thumbnail").hide();
                    }
                });
            },

            // make a link to a related video, appending exercise ID.
            makeHref: function(video) {
                return video.relativeUrl + "?exid=" + this.exercise.name;
            },

            anchorElement: function(video, needComma) {
                var template = Templates.get("video.related-video-link");
                return $(template({
                    href: this.makeHref(video),
                    video: video,
                    separator: needComma
                })).data("video", video);
            },

            renderInSidebar: function() {
                var container = $(".related-video-box");
                var jel = container.find(".related-video-list");
                jel.empty();

                var template = Templates.get("video.thumbnail");
                _.each(this.getVideos(), function(video, i) {
                    var thumbnailDiv = $(template({
                        href: this.makeHref(video),
                        video: video
                    })).find("a.related-video").data("video", video).end();

                    var inlineLink = this.anchorElement(video)
                        .addClass("related-video-inline");

                    var sideBarLi = $("<li>")
                        .append(inlineLink)
                        .append(thumbnailDiv);

                    if (i > 0) {
                        thumbnailDiv.hide();
                    } else {
                        inlineLink.hide();
                    }
                    jel.append(sideBarLi);
                }, this);

                container.toggle(this.getVideos().length > 0);
            },

            hookup: function() {
                // make caption slide up over the thumbnail on hover
                var captionHeight = 45;
                var marginTop = 23;
                // queue:false to make sure these run simultaneously
                var options = {duration: 150, queue: false};
                $(".related-video-box")
                    .delegate(".thumbnail", "mouseenter mouseleave", function(e) {
                        var el = $(e.currentTarget);
                        if (e.type == "mouseenter") {
                            el.find(".thumbnail_label").animate(
                                    {marginTop: marginTop},
                                    options)
                                .end()
                                .find(".thumbnail_teaser").animate(
                                    {height: captionHeight},
                                    options)
                                .end();
                        } else {
                            el.find(".thumbnail_label").animate(
                                    {marginTop: marginTop + captionHeight},
                                    options)
                                .end()
                                .find(".thumbnail_teaser").animate(
                                    {height: 0},
                                    options)
                                .end();
                        }
                    });
            },

            render: function() {
                // don't try to render if templates aren't present (dev mode)
                if (!window.Templates) return;

                this.renderInSidebar();
            }
        },

        showSolutionButtonText: function() {
            return hintsUsed ? "Show next step (" + hints.length + " left)" : "Show Solution";
        }

    };
    // see line 183. this ends the main Khan module

    // Load query string params
    Khan.query = Khan.queryString();

    if (Khan.query.activity !== undefined) {
        userExercise = {
            current: true,
            exerciseModel: {},
            readOnly: true,
            userActivity: JSON.parse(Khan.query.activity)
        };
    }

    // Seed the random number generator with the user's hash
    randomSeed = testMode && parseFloat(Khan.query.seed) || userCRC32 || (new Date().getTime() & 0xffffffff);

    // Load in jQuery
    var scripts = (typeof jQuery !== "undefined") ? [] : [{src: "../jquery.js"}];

    // Actually load the scripts. This is getting evaluated when the file is loaded.
    Khan.loadScripts(scripts, function() {

        if (testMode) {
            Khan.require(["../jquery-ui", "../jquery.qtip"]);
        }

        // Base modules required for every problem
        Khan.require(["answer-types", "tmpl", "underscore", "jquery.adhesion", "hints"]);

        Khan.require(document.documentElement.getAttribute("data-require"));

        // Initialize to an empty jQuery set
        exercises = jQuery();

        // [C2G] Is this problem set formative or summative? Default is 
        // formative, but check problem set div for summative CSS class; 
        // otherwise, check the class name on the article element in the page
        exAssessType = 'formative';
        if ($("div.summative").length || $("div.assessive").length ||
            $("article.summative").length || $("article.summative").length) {
            exAssessType = 'summative';
        }

        $(function() {
            var remoteExercises = $("div.exercise[data-name]");

            if (remoteExercises.length) {

                KhanC2G.remoteExercises = [];
                // [C2G] controlLoad is a helper to ensure exercise fetching 
                // happens sequentially and synchronously
                var controlLoad = function(exArr) {
                    if (exArr.length > 0) {
                        currentEx = exArr.shift();
                        loadExercise.call(currentEx).done(function () {
                            controlLoad(exArr);
                        });
                    } else {
                        return;
                    }
                }
                controlLoad(remoteExercises.toArray());


            // Only run loadModules if exercises are in the page
            } else if ($("div.exercise").length) {
                loadModules();
            }
        });

        $.fn.extend({
            // Pick a random element from a set of elements
            getRandom: function() {
                return this.eq(Math.floor(this.length * KhanUtil.random()));
            },

            // Run the methods provided by a module against some elements
            runModules: function(problem, type) {
                type = type || "";

                var info = {
                    testMode: testMode
                };

                return this.each(function(i, elem) {
                    elem = $(elem);

                    // Run the main method of any modules
                    $.each(Khan.modules, function(src, mod) {
                        var name = mod.name;
                        if ($.fn[name + type]) {
                            elem[name + type](problem, info);
                        }
                    });
                });
            }
        });

        // See if an element is detached
        $.expr[":"].attached = function(elem) {
            return $.contains(elem.ownerDocument.documentElement, elem);
        };
    });

    // Add up how much total weight is in each exercise so we can adjust for
    // it later
    function weighExercises(problems) {
        if (exercises.length > 1) {
            $.map(problems, function(elem) {
                elem = $(elem);

                var exercise = elem.parents("div.exercise").eq(0);

                var exerciseTotal = exercise.data("weight-sum");
                exerciseTotal = exerciseTotal !== undefined ? exerciseTotal : 0;

                var weight = elem.data("weight");
                weight = weight !== undefined ? weight : 1;

                exercise.data("weight-sum", exerciseTotal + weight);
            });
        }
    }

    // Create a set of n problems fairly from the weights - not random; it
    // ensures that the proportions come out as fairly as possible with ints
    // (still usually a little bit random).
    // There has got to be a better way to do this.
    function makeProblemBag(problems, n) {
        var bag = [], totalWeight = 0;

        if (testMode && Khan.query.test != null) {
            // Just do each problem 10 times
            $.each(problems, function(i, elem) {
                elem = $(elem);
                elem.data("id", elem.attr("id") || "" + i);

                for (var j = 0; j < 10; j++) {
                    bag.push(problems.eq(i));
                }
            });

            problemCount = bag.length;

        } else if (problems.length > 0) {
            // Collect the weights for the problems and find the total weight
            var weights = $.map(problems, function(elem, i) {
                elem = $(elem);

                var exercise = elem.parents("div.exercise").eq(0);
                var exerciseWeight = exercise.data("weight");
                exerciseWeight = exerciseWeight !== undefined ? exerciseWeight : 1;
                var exerciseTotal = exercise.data("weight-sum");

                var weight = elem.data("weight");
                weight = weight !== undefined ? weight : 1;

                if (exerciseTotal !== undefined) {
                    weight = weight * exerciseWeight / exerciseTotal;
                    elem.data("weight", weight);
                }

                // Also write down the index/id for each problem so we can do
                // links to problems (?problem=17)
                elem.data("id", elem.attr("id") || "" + i);

                totalWeight += weight;
                return weight;
            });

            while (n) {
                bag.push((function() {
                    // Figure out which item we're going to pick
                    var index = totalWeight * KhanUtil.random();

                    for (var i = 0; i < problems.length; i++) {
                        if (index < weights[i] || i === problems.length - 1) {
                            var w = Math.min(weights[i], totalWeight / (n--));
                            weights[i] -= w;
                            totalWeight -= w;
                            return problems.eq(i);
                        } else {
                            index -= weights[i];
                        }
                    }

                    // This will never happen
                    return Khan.error("makeProblemBag got confused w/ index " + index);
                })());
            }
        }

        return bag;
    }

    function enableCheckAnswer() {
        $("#check-answer-button")
            .removeAttr("disabled")
            .removeClass("buttonDisabled");
        // [C2G] Added text change for Summative exercises
        if (typeof exAssessType != "undefined" && exAssessType == "summative") {
            $("#check-answer-button").val("Submit Answer");
        } else {
            $("#check-answer-button").val("Check Answer");
        }
    }

    function disableCheckAnswer() {
        $("#check-answer-button")
            .attr("disabled", "disabled")
            .addClass("buttonDisabled")
            .val("Please wait...");
    }

    function isExerciseLoaded(exerciseId) {
        return _.any(exercises, function(exercise) {
            return $.data(exercise, "rootName") === exerciseId;
        });
    }

    function startLoadingExercise(exerciseId, exerciseName, exerciseFile) {

        if (typeof loadingExercises[exerciseId] !== "undefined") {
            // Already started loading this exercise.
            return;
        }

        if (isExerciseLoaded(exerciseId)) {
            return;
        }

        var exerciseElem = $("<div>")
            .data("name", exerciseId)
            .data("displayName", exerciseName)
            .data("fileName", exerciseFile)
            .data("rootName", exerciseId);

        // Queue up an exercise load
        loadExercise.call(exerciseElem, function() {

            // Trigger load completion event for this exercise
            $(Khan).trigger("exerciseLoaded:" + exerciseId);

            delete loadingExercises[exerciseId];

        });

    }

    function loadAndRenderExercise(nextUserExercise) {

        setUserExercise(nextUserExercise);
        exerciseId = userExercise.exerciseModel.name;
        exerciseName = userExercise.exerciseModel.displayName;
        exerciseFile = userExercise.exerciseModel.fileName;
        // TODO(eater): remove this once all of the exercises in the datastore have filename properties
        if (exerciseFile == null || exerciseFile == "") {
            exerciseFile = exerciseId + ".html";
        }

        function finishRender() {

            // Get all problems of this exercise type...
            var problems = exercises.filter(function() {
                return $.data(this, "rootName") === exerciseId;
            }).children(".problems").children();

            // ...and create a new problem bag with problems of our new exercise type.
            problemBag = makeProblemBag(problems, 10);

            // Update related videos
            Khan.relatedVideos.setVideos(userExercise.exerciseModel);

            // Make scratchpad persistent per-user
            if (user) {
                var lastScratchpad = window.localStorage["scratchpad:" + user];
                if (typeof lastScratchpad !== "undefined" && JSON.parse(lastScratchpad)) {
                    Khan.scratchpad.show();
                }
            }

            // Generate a new problem
            makeProblem();

        }

        if (isExerciseLoaded(exerciseId)) {
            finishRender();
        } else {
            startLoadingExercise(exerciseId, exerciseName, exerciseFile);

            $(Khan)
                .unbind("exerciseLoaded:" + exerciseId)
                .bind("exerciseLoaded:" + exerciseId, function() {
                    finishRender();
                });
        }

    }

    /**
     * Returns whether we should skip the current problem because it's
     * a duplicate (or too similar) to a recently done problem in the same
     * exercise.
     */
    function shouldSkipProblem() {
        // We don't need to skip duplicate problems in test mode, which allows
        // us to use the LocalStore localStorage abstraction from shared-package
        if (typeof LocalStore === "undefined") {
            return false;
        }

        var cacheKey = "prevProblems:" + user + ":" + exerciseName;
        var cached = LocalStore.get(cacheKey);
        var lastProblemNum = (cached && cached["lastProblemNum"]) || 0;

        if (lastProblemNum === problemNum) {
            // Getting here means the user refreshed the page or returned to
            // this exercise after being away. So, we don't need to and
            // shouldn't skip this problem.
            return false;
        }

        var pastHashes = (cached && cached["history"]) || [];
        var varsHash = $.tmpl.getVarsHash();

        // Should skip the current problem if we've already seen it in the past
        // few problems, but not if we've been fruitlessly skipping for a while.
        // The latter situation could happen if a problem has very few unique
        // problems (eg. exterior angles problem type of angles_of_a_polygon).
        if (_.contains(pastHashes, varsHash) && consecutiveSkips < dupWindowSize) {
            consecutiveSkips++;
            return true;
        } else {
            consecutiveSkips = 0;
            pastHashes.push(varsHash);
            while (pastHashes.length > dupWindowSize) {
                pastHashes.shift();
            }

            LocalStore.set(cacheKey, {
                lastProblemNum: problemNum,
                history: pastHashes
            });
            return false;
        }
    }


    function checkIfAnswerEmpty() {
        return $.trim(validator.guess) === "" ||
                 (validator.guess instanceof Array && $.trim(validator.guess.join("").replace(/,/g, "")) === "");
    }

    function makeProblem(id, seed) {

        // Enable scratchpad (unless the exercise explicitly disables it later)
        Khan.scratchpad.enable();

        // [C2G] Build and return a localStorage key
        function getLSSeedKey () {
            var seedKey = c2gConfig.user || 'anon';
            seedKey += '-';
            if ($('#exercise_type').length && $('#exercise_type').val() === 'problemset') {
                seedKey += 'ps-' + $('#pset_id').val();
            } else if ($('#exercise_type').length && $('#exercise_type').val() === 'video') {
                seedKey += 'vid-' + $('#video_id').val();
            }
            seedKey += '-' + id;
            return seedKey;
        }

        // [C2G] Has a problem seed been stored? Only important for non-video exercises
        // 1. Check data object of current question card (list item)
        // 2. Check data on KhanC2G.PSActivityLog
        // 3. Check localStorage
        // 4. Check userPSData object (last resort, as it's a little messier)
        function getLocalSeed () {
            // If in-video exercise, no problems should be called with seeds
            // (because we want to allow random answer choices for these exercises)
            if ($('#exercise_type').val() == "video") {
                return null;
            }

            // try the seed data stored in the question card
            if ($('.current-question').data('problemSeed')) {
                return $('.current-question').data('problemSeed');
            // try one stored in KhanC2G.PSActivityLog 
            } else if (typeof KhanC2G != "undefined" &&
                        typeof KhanC2G.PSActivityLog != "undefined" &&
                        typeof KhanC2G.PSActivityLog.problems != "undefined" &&
                        typeof KhanC2G.PSActivityLog.problems[id] != "undefined" &&
                        typeof KhanC2G.PSActivityLog.problems[id].problemSeed != "undefined") {
                return KhanC2G.PSActivityLog.problems[id].problemSeed;
            // try one stored in localStorage
            } else if (localStorage.getItem(getLSSeedKey())) {
                return localStorage.getItem(getLSSeedKey());
            // finally, try the userPSData object
            } else if (typeof userPSData != "undefined" && 
                        typeof userPSData.problems != "undefined" &&
                        typeof userPSData.problems.length > 0) {
                var userPSDataProbLen = userPSData.problems.length;
                for (var p = 0; p < userPSDataProbLen; p += 1) {
                    if (userPSData.problems[p].problem_index = id) {
                        return userPSData.problems[p].problem_seed; 
                    }
                }
            }
            // no seed has been stored locally
            return null;
        }

        // Allow passing in a random seed
        if (typeof seed !== "undefined") {
            problemSeed = seed;
        // [C2G] Check to see if there has been a seed stored for this problem
        } else if (getLocalSeed()) {
            problemSeed = parseInt(getLocalSeed());
        // In either of these testing situations,
        } else if ((testMode && Khan.query.test != null) || user == null) {
            problemSeed = randomSeed % bins;
        }

        // Set randomSeed to what problemSeed is (save problemSeed for recall later)
        randomSeed = problemSeed;

        if (KhanC2G.PSActivityLog.exerciseType == 'problemset') {
            // [C2G] Store locally
            if (!localStorage.getItem(getLSSeedKey())) {
                localStorage.setItem(getLSSeedKey(), problemSeed);
            }

            // store in KhanC2G.PSActivityLog object
            var loggedProbSeed = KhanC2G.PSActivityLog.problems[id]["problemSeed"];
            if (!loggedProbSeed) {
                KhanC2G.PSActivityLog.problems[id]['problemSeed'] = parseInt(problemSeed);
            }

            // store in current-question data object
            if(!$('.current-question').data('problemSeed')) {
                $('.current-question').data('problemSeed', parseInt(problemSeed));
            }
        }

        // Check to see if we want to test a specific problem
        if (testMode) {
            id = typeof id !== "undefined" ? id : Khan.query.problem;
        }

        if (typeof id !== "undefined") {
            var problems = exercises.children(".problems").children();

            problem = /^\d+$/.test(id) ?
                // Access a problem by number
                problems.eq(parseFloat(id)) :

                // Or by its ID
                problems.filter("#" + id);

        // Otherwise we grab a problem at random from the bag of problems
        // we made earlier to ensure that every problem gets shown the
        // appropriate number of times

        // [C2G] Removing this as we're not dealing with a problemBag at this time
        /*
        } else if (problemBag.length > 0) {
            problem = problemBag[problemBagIndex];
            id = problem.data("id");
        */

        // No valid problem was found, bail out
        // [C2G] Actually, just return first problem
        } else {
            // [C2G] Don't just return
            //return;
            problem = problems[0];
            id = problem.data("id");
        }

        problemID = id;

        // Find which exercise this problem is from
        exercise = problem.parents("div.exercise").eq(0);

        // JASON BAU -- for C2G problems sets we want to display the exercise title
        if (exercise.data('title')) {
            $("#container .exercises-header h2").children().last().text(exercise.data('title')[0]);
        } else {
            $("#container .exercises-header h2").children().last().text(exercise.attr('title'));
        }
        // Work with a clone to avoid modifying the original
        problem = problem.clone();

        // [C2G] Adding clearExistingProblem to clear out Loading message
        clearExistingProblem();

        // problem has to be child of visible #workarea for MathJax metrics to all work right
        $("#workarea").append(problem);

        // If there's an original problem, add inherited elements
        var parentType = problem.data("type");

        while (parentType) {
            // Copy over the parent element to the child
            var original = exercise.find(".problems #" + parentType).clone();
            problem.prepend(original.children().data("inherited", true));

            // Keep copying over the parent elements (allowing for deep inheritance)
            parentType = original.data("type");
        }

        // Add any global exercise defined elements
        problem.prepend(exercise.children(":not(.problems)").clone().data("inherited", true));

        // Apply templating
        var children = problem
            // var blocks append their contents to the parent
            .find(".vars").tmplApply({attribute: "class", defaultApply: "appendVars"}).end()

            // Individual variables override other variables with the same name
            .find(".vars [id]").tmplApply().end()

            // We also look at the main blocks within the problem itself to override,
            // ignoring graphie and spin blocks
            .children("[class][class!='graphie'][class!='spin']").tmplApply({attribute: "class"});

        // Finally we do any inheritance to the individual child blocks (such as problem, question, etc.)
        children.each(function() {
            // Apply while adding problem.children() to include
            // template definitions within problem scope
            $(this).find("[id]").add(children).tmplApply();
        });

        // Remove and store hints to delay running modules on it
        hints = problem.children(".hints").remove();

        // Hide the hint box if there are no hints in the problem

        $(".hint-box").show();

        // [C2G] Adding check for summative exercises, which shouldn't have hints
        if (hints.length === 0 || exAssessType == "summative") {
            $(".hint-box").hide();
        }


        // Evaluate any inline script tags in this exercise's source
        $.each(exercise.data("script") || [], function(i, scriptContents) {
            $.globalEval(scriptContents);
        });

        // ...and inline style tags.
        if (exercise.data("style")) {
            var exerciseStyleElem = $("head #exercise-inline-style");

            // Clear old exercise style definitions
            if (exerciseStyleElem.length && exerciseStyleElem[0].styleSheet) {
                // IE refuses to modify the contents of <style> the normal way
                exerciseStyleElem[0].styleSheet.cssText = "";
            } else {
                exerciseStyleElem.empty();
            }

            // Then add rules specific to this exercise.
            $.each(exercise.data("style"), function(i, styleContents) {
                if (exerciseStyleElem.length && exerciseStyleElem[0].styleSheet) {
                    // IE refuses to modify the contents of <style> the normal way
                    exerciseStyleElem[0].styleSheet.cssText = exerciseStyleElem[0].styleSheet.cssText + styleContents;
                } else {
                    exerciseStyleElem.append(styleContents);
                }
            });
        }

        // Run the main method of any modules
        problem.runModules(problem, "Load");
        problem.runModules(problem);

        if (shouldSkipProblem()) {
            // If this is a duplicate problem we should skip, just generate
            // another problem of the same problem type but w/ a different seed.
            clearExistingProblem();
            nextSeed(1);
            return makeProblem();
        }

        // Store the solution to the problem
        var solution = problem.find(".solution"),

            // Get the multiple choice problems
            choices = problem.find(".choices"),

            // Get the area into which solutions will be inserted,
            // Removing any previous answer
            solutionarea = $("#solutionarea").empty(),

            // See if we're looking for a specific style of answer
            answerType = solution.data("type");

        // Make sure that the answer type exists
        if (answerType) {
            if (Khan.answerTypes && !Khan.answerTypes[answerType]) {
                Khan.error("Unknown answer type specified: " + answerType);
                return;
            }
        }

        if (!answerType) {
            // If a multiple choice block exists
            if (choices.length) {
                answerType = "radio";

            // Otherwise we assume the smart number type
            } else {
                answerType = "number";
            }
        }


        // [C2G] Hide solutionarea until ready
        //console.log('Hiding solution area...');
        $('#solutionarea').css('visibility', 'hidden');

        // Generate a type of problem
        // (this includes possibly generating the multiple choice problems,
        // if this fails then we will need to try generating another one.)
        guessLog = [];
        userActivityLog = [];
        validator = Khan.answerTypes[answerType](solutionarea, solution);

        // A working solution was generated
        if (validator) {
            // Focus the first input
            // Use .select() and on a delay to make IE happy
            var firstInput = solutionarea.find(":input").first();
            setTimeout(function() {
                if (!firstInput.is(":disabled")) {
                    firstInput.focus();
                    if (firstInput.is("input:text")) {
                        firstInput.select();
                    }
                }
            }, 1);

            lastFocusedSolutionInput = firstInput;
            solutionarea.find(":input").focus(function() {
                // Save which input is focused so we can refocus it after the user hits Check Answer
                lastFocusedSolutionInput = this;
            });
        } else {
            // Making the problem failed, let's try again
            problem.remove();
            makeProblem(id, randomSeed);
            return;
        }

        // Remove the solution and choices elements from the display
        solution.remove();
        choices.remove();

        // Add the problem into the page
        Khan.scratchpad.resize();

        // Enable the all answer input elements except the check answer button.
        $("#answercontent input").not("#check-answer-button")
            .removeAttr("disabled");

        var maxAttempts, penaltyPct, alreadyAttempted;
        var maxCredit = 100; 
        // [C2G] Check c2gConfig first, which defines overall Problem Set parameters
        if (typeof c2gConfig != "undefined") {
            maxAttempts = (typeof c2gConfig.maxAttempts != "undefined" && c2gConfig.maxAttempts > 0) ? c2gConfig.maxAttempts : 3;
            penaltyPct = (typeof c2gConfig.penaltyPct != "undefined") ? c2gConfig.penaltyPct + "%" : "25%";
        } else {
            maxAttempts = 3;
            penaltyPct = "25%";
        }
        var exerciseRef = ($('.current-question').data("problemIndex")) ? parseInt($('.current-question').data("problemIndex")) : id;

        // [C2G] Default to no attempts
        alreadyAttempted = 0;
        isCorrect = false;
        if (typeof KhanC2G.PSActivityLog != "undefined" && 
                typeof KhanC2G.PSActivityLog.problems != "undefined" && 
                KhanC2G.PSActivityLog.problems[exerciseRef]) {
            if (KhanC2G.PSActivityLog.problems[exerciseRef]["alreadyAttempted"]) {
                alreadyAttempted = KhanC2G.PSActivityLog.problems[exerciseRef]["alreadyAttempted"];
            }
            if (KhanC2G.PSActivityLog.problems[exerciseRef]["correct"]) {
                isCorrect = true;
            }
        }

        // [C2G] If it's been attempted at all
        if (alreadyAttempted > 0) {
            maxCredit = (alreadyAttempted < maxAttempts) ? (maxCredit - alreadyAttempted * parseInt(penaltyPct)) : 0; 
            // if last attempt was correct and user hasn't exceeded the maximum number
            // of attempts, it shouldn't be deducted from score; add back in 1x penaltyPct
            if (isCorrect && (alreadyAttempted <= maxAttempts)) {
                maxCredit = 100 - ((alreadyAttempted - 1) * parseInt(penaltyPct));
            }
            if (KhanC2G.PSActivityLog.problems[exerciseRef]['userEntered']) {
                var userSelVal = KhanC2G.PSActivityLog.problems[exerciseRef]['userEntered'];
                if ($('#solutionarea input:radio').length) {
                    $('#solutionarea input:radio')[parseInt(userSelVal)].checked = true;
                } else {
                    $('#solutionarea #testinput').val(userSelVal);
                }
            } else if ($('.current-question').data('userEntered')) {
                var userSelVal = $('.current-question').data('userEntered');
                if ($('#solutionarea input:radio').length) {
                    $('#solutionarea input:radio')[parseInt(userSelVal)].checked = true;
                } else {
                    $('#solutionarea #testinput').val(userSelVal);
                }
            }
        } 
        
        // [C2G] If user got this one right, remove penalty description and replace with summary
        if (typeof KhanC2G.PSActivityLog != "undefined" && 
            typeof KhanC2G.PSActivityLog.problems != "undefined" &&
            KhanC2G.PSActivityLog.problems[exerciseRef] && 
            KhanC2G.PSActivityLog.problems[exerciseRef]['correct']) {
            $('#solutionarea input').attr('disabled', 'disabled');
            $('#solutionarea').remove('p');
            $('#check-answer-button').hide();
            $('.hint-box').hide();
            if (exAssessType == "summative") {
                $('#solutionarea').append('<p><strong class="attempts-so-far">Attempts: <span id="attempt-count">' + alreadyAttempted + '</span></strong></p> <p>You received <span id="max-credit">' + maxCredit + '</span>% credit</p>');
            }
        } else {
            // [C2G] If summative problem set, add note about penalties per try
            if (exAssessType == "summative") {
                $('#solutionarea').append('<p><strong>Note:</strong> Maximum of <strong>' + maxAttempts + '</strong> attempts accepted for credit. </p>');
                $('#solutionarea p').append('<span id="penalty-pct">' + penaltyPct + '</span> penalty per attempt.');
                $('#solutionarea').append('<p><strong class="attempts-so-far">Attempts so far: <span id="attempt-count">' + alreadyAttempted + '</span></strong> (Maximum credit <span id="max-credit">' + maxCredit + '</span>%)</p>');
            }
            $("#check-answer-button").val("Submit Answer");
            $("#check-answer-button").show();
        }

        if (exAssessType == "summative" && $('.current-question').is($('#questions-stack li:last'))) {
            if ($('#submit-problemset-button').length) {
                $('#submit-problemset-button').parent().show();
            } else {
                $('#answer_area').append('<div class="info-box"><input type="button" class="simple-button green full-width" id="submit-problemset-button" value="Submit Problem Set"/></div>');
                $('#submit-problemset-button').click(function () {
                    location.href = (typeof c2gConfig != "undefined") ? c2gConfig.progressUrl : 'problemsets';
                });
            }
        } else if ($('#submit-problemset-button').length) {
            $('#submit-problemset-button').parent().hide();
        }

        if (examples !== null && validator.examples && validator.examples.length > 0) {
            $("#examples-show").show();
            examples.empty();

            $.each(validator.examples, function(i, example) {
                examples.append("<li>" + example + "</li>");
            });

            examples.children().tmpl();
        } else {
            $("#examples-show").hide();
        }
        // save a normal JS array of hints so we can shift() through them later
        hints = hints.tmpl().children().get();

        if (hints.length === 0) {
            // Disable the get hint button
            $("#hint").attr("disabled", true);
        }

        // Hook out for exercise test runner
        if (testMode && parent !== window && typeof parent.jQuery !== "undefined") {
            parent.jQuery(parent.document).trigger("problemLoaded", [makeProblem, validator.solution]);
        }

        // Save problem info in dump data for testers
        if (testMode && Khan.query.test != null) {
            var testerInfo = $("#tester-info");

            // Deep clone the elements to avoid some straaaange bugs
            var lastProblem = $.extend(true, {}, {
                seed: problemSeed,
                type: problemID,
                VARS: $.tmpl.VARS,
                solution: validator.solution
            });

            dataDump.problems.push(lastProblem);

            $(testerInfo).find(".problem-no")
                .text(dataDump.problems.length + dataDump.issues + " of " + problemCount);

            var answer = $(testerInfo).find(".answer").empty();

            var displayedSolution = validator.solution;
            if (!$.isArray(displayedSolution)) {
                displayedSolution = [displayedSolution];
            }

            $.each(displayedSolution, function(i, el) {
                if ($.isArray(el)) {
                    // group nested arrays of answers, for sets of multiples or multiples of sets.
                    // no reason answers can't be nested arbitrarily deep, but here we assume no
                    // more than one sub-level.
                    var subAnswer = $("<span>").addClass("group-box").appendTo(answer);
                    $.each(el, function(i, el) {
                        $("<span>").text(el).addClass("box").appendTo(subAnswer);
                    });
                } else {
                    $("<span>").text(el).addClass("box").appendTo(answer);
                }
            });
        }

        if (typeof userExercise !== "undefined" && userExercise.readOnly) {
            if (!userExercise.current) {
                warn("This exercise may have changed since it was completed", true);
            }

            var timelineEvents, timeline;

            var timelinecontainer = $("<div id='timelinecontainer'>")
                .append("<div>\n" +
                        "<div id='previous-problem' class='simple-button'>Previous Problem</div>\n" +
                        "<div id='previous-step' class='simple-button'><span>Previous Step</span></div>\n" +
                        "</div>")
                .insertBefore("#problem-and-answer");

            $.fn.disable = function() {
                this.addClass("disabled")
                    .css({
                        cursor: "default !important"
                    })
                    .data("disabled", true);
                return this;
            }

            $.fn.enable = function() {
                this.removeClass("disabled")
                    .css({
                        cursor: "pointer"
                    })
                    .data("disabled", false);
                return this;
            }

            if (userExercise.totalDone === 0) {
                $("#previous-problem").disable();
            }

            timeline = $("<div id='timeline'>").appendTo(timelinecontainer);
            timelineEvents = $("<div id='timeline-events'>").appendTo(timeline);

            timelinecontainer
                .append("<div>\n" +
                        "<div id='next-problem' class='simple-button'>Next Problem</div>\n" +
                        "<div id='next-step' class='simple-button'><span>Next Step</span></div>\n" +
                        "</div>");

            $("<div class='user-activity correct-activity'>Started</div>")
                .data("hint", false)
                .appendTo(timelineEvents);

            var hintNumber = 0,
                answerNumber = 1;

            /* value[0]: css class
             * value[1]: guess
             * value[2]: time taken since last guess
             */
            $.each(userExercise.userActivity, function(index, value) {
                var guess = value[1] === "Activity Unavailable" ? value[1] : JSON.parse(value[1]),
                    thissolutionarea;

                timelineEvents
                    .append("<div class='timeline-time'>" + value[2] + "s</div>");

                thissolutionarea = $("<div>")
                    .addClass("user-activity " + value[0])
                    .appendTo(timelineEvents);

                if (value[0] === "hint-activity") {
                    thissolutionarea.attr("title", "Hint used");
                    thissolutionarea
                        .data("hint", hintNumber)
                        .prepend("Hint #" + (hintNumber + 1));
                    hintNumber += 1;
                } else { // This panel is a solution (or the first panel)
                    thissolutionarea.data("hint", false);
                    if (guess === "Activity Unavailable") {
                        thissolutionarea.text(guess);
                    } else {
                        if (answerType === "radio") {
                            // radio is the only answer type that can't display its own guesses
                            thissolutionarea.append($(
                                "<p class='solution'>" + guess + "</p>").tmpl()
                            );

                            if (index === userExercise.userActivity.length - 1) {
                                thissolutionarea
                                    .removeClass("incorrect-activity")
                                    .addClass("correct-activity");

                                thissolutionarea.attr("title", "Correct Answer");
                            } else {
                                thissolutionarea.attr("title", "Incorrect Answer");
                            }
                        } else {
                            var thisValidator = Khan.answerTypes[answerType](thissolutionarea, solution);

                            thisValidator.showGuess(guess);

                            if (thisValidator() === true) {
                                // If the user didn't get the problem right on the first try, all
                                // answers are labelled incorrect by default
                                thissolutionarea
                                    .removeClass("incorrect-activity")
                                    .addClass("correct-activity");

                                thissolutionarea.attr("title", "Correct Answer");
                            } else {
                                thissolutionarea
                                    .removeClass("correct-activity")
                                    .addClass("incorrect-activity");
                                thissolutionarea.attr("title", "Incorrect Answer");
                            }
                        }

                        thissolutionarea
                            .data("guess", guess)
                                .find("input")
                                .attr("disabled", true)
                            .end()
                                .find("select")
                                .attr("disabled", true);
                    }
                }
            });

            if (timelinecontainer.height() > timeline.height()) {
                timeline.height(timelinecontainer.height());
            }

            var states = timelineEvents.children(".user-activity"),
                currentSlide = states.length - 1,
                numSlides = states.length,
                firstHintIndex = timeline.find(".hint-activity:first")
                    .index(".user-activity"),
                lastHintIndex = timeline.find(".hint-activity:last")
                    .index(".user-activity"),
                totalHints = timeline.find(".hint-activity:last")
                    .index(".hint-activity"),
                hintButton = $("#hint"),
                timelineMiddle = timeline.width() / 2,
                realHintsArea = $("#hintsarea"),
                realWorkArea = $("#workarea"),
                statelist = [],
                previousHintNum = 100000;

            // So highlighting doesn't fade to white
            $("#solutionarea").css("background-color", $("#answercontent").css("background-color"));

            $.fn.scrubber = function() {
                // create triangular scrubbers above and below current selection
                var timeline = $("#timeline"),
                    scrubber1 = $("#scrubber1"),
                    scrubber2 = $("#scrubber2"),
                    scrubberCss = {
                        display: "block",
                        width: "0",
                        height: "0",
                        "border-left": "6px solid transparent",
                        "border-right": "6px solid transparent",
                        position: "absolute",
                        left: (timeline.scrollLeft() + this.position().left + this.outerWidth() / 2 + 2) + "px"
                    };

                scrubber1 = scrubber1.length ? scrubber1 : $("<div id='scrubber1'>").appendTo(timeline);
                scrubber2 = scrubber2.length ? scrubber2 : $("<div id='scrubber2'>").appendTo(timeline);

                scrubber1.css($.extend({}, scrubberCss, {
                    "border-bottom": "6px solid #888",
                    bottom: "0"
                }));

                scrubber2.css($.extend({}, scrubberCss, {
                    "border-top": "6px solid #888",
                    top: "0"
                }));

                return this;
            };

            // Set the width of the timeline (starts as 10000px) after MathJax loads
            MathJax.Hub.Queue(function() {
                var maxHeight = 0;
                timelineEvents.children().each(function() {
                    maxHeight = Math.max(maxHeight, $(this).outerHeight(true));
                });

                if (maxHeight > timelinecontainer.height()) {
                    timelinecontainer.height(maxHeight);
                    timeline.height(maxHeight);
                }
            });

            var create = function(i) {
                var thisSlide = states.eq(i);

                var thisHintArea, thisProblem,
                    hintNum = $("#timeline-events .user-activity:lt(" + (i + 1) + ")")
                            .filter(".hint-activity").length - 1,
                    // Bring the currently focused panel as close to the middle as possible
                    itemOffset = thisSlide.position().left,
                    itemMiddle = itemOffset + thisSlide.width() / 2,
                    offset = timelineMiddle - itemMiddle,
                    currentScroll = timeline.scrollLeft(),
                    timelineMax = states.eq(-1).position().left + states.eq(-1).width(),
                    scroll = Math.min(currentScroll - offset, currentScroll + timelineMax - timeline.width() + 25);

                if (hintNum >= 0) {
                    $(hints[hintNum]).appendTo(realHintsArea).runModules(problem);
                }

                MathJax.Hub.Queue(function() {
                    var recordState = function() {
                        $("#problemarea input").attr({disabled: "disabled"});
                        thisHintArea = realHintsArea.clone();
                        thisProblem = realWorkArea.clone();

                        var thisState = {
                            slide: thisSlide,
                            hintNum: hintNum,
                            hintArea: thisHintArea,
                            problem: thisProblem,
                            scroll: scroll
                        };

                        statelist[i] = thisState;

                        if (i + 1 < states.length) {
                            MathJax.Hub.Queue(function() {
                                create(i + 1);
                            });
                        } else {
                            activate(i);
                        }
                    };

                    if (thisSlide.data("guess") !== undefined && $.isFunction(validator.showCustomGuess)) {
                        KhanUtil.currentGraph = $(realWorkArea).find(".graphie").data("graphie");
                        validator.showCustomGuess(thisSlide.data("guess"));
                        MathJax.Hub.Queue(recordState);
                    } else {
                        recordState();
                    }

                });
            };

            var activate = function(slideNum) {
                var hint, thisState,
                    thisSlide = states.eq(slideNum),
                    fadeTime = 150;

                // All content for this state has been built before
                if (statelist[slideNum]) {
                    thisState = statelist[slideNum];

                    timeline.animate({
                        scrollLeft: thisState.scroll
                    }, fadeTime, function() {
                        thisState.slide.scrubber();
                    });

                    $("#workarea").remove();
                    $("#hintsarea").remove();
                    $("#problemarea").append(thisState.problem).append(thisState.hintArea);

                    if (thisSlide.data("guess")) {
                        solutionarea.effect("highlight", {}, fadeTime);

                        // If there is a guess we show it as if it was filled in by the user
                        validator.showGuess(thisSlide.data("guess"));
                    } else {
                        validator.showGuess();
                    }

                    // TODO: still highlight even if hint modifies problem (and highlight following hints)
                    if (slideNum > 0 && (thisState.hintNum > statelist[slideNum - 1].hintNum)) {
                        $("#hintsarea").children().each(function(index, elem) {
                            if (index > previousHintNum) {
                                $(elem).effect("highlight", {}, fadeTime);
                            }
                        });

                        previousHintNum = thisState.hintNum;
                    }

                    $("#previous-step, #next-step").enable();
                    if (slideNum === 0) {
                        previousHintNum = -1;
                        $("#previous-step").disable();
                    } else if (slideNum === numSlides - 1) {
                        $("#next-step").disable();
                    }
                }
            };

            MathJax.Hub.Queue(function() {create(0);});

            // Allow users to use arrow keys to move up and down the timeline
            $(document).keydown(function(event) {
                if (event.keyCode !== 37 && event.keyCode !== 39) {
                    return;
                }

                if (event.keyCode === 37) { // left
                    currentSlide -= 1;
                } else { // right
                    currentSlide += 1;
                }

                currentSlide = Math.min(currentSlide, numSlides - 1);
                currentSlide = Math.max(currentSlide, 0);

                activate(currentSlide);

                return false;
            });

            // Allow users to click on points of the timeline
            $(states).click(function(event) {
                var index = $(this).index("#timeline .user-activity");

                currentSlide = index;
                activate(currentSlide);

                return false;
            });

            $("#previous-step").click(function(event) {
                if (currentSlide > 0) {
                    currentSlide -= 1;
                    activate(currentSlide);
                }

                return false;
            });

            $("#next-step").click(function(event) {
                if (currentSlide < numSlides - 1) {
                    currentSlide += 1;
                    activate(currentSlide);
                }

                return false;
            });

            $("#next-problem").click(function(event) {
                window.location.href = userExercise.nextProblemUrl;
            });

            $("#previous-problem").click(function(event) {
                if (!$(this).data("disabled")) {
                    window.location.href = userExercise.previousProblemUrl;
                }
            });

            // Some exercises use custom css
            $("#timeline input[type='text']").css("width",
                $("#answer_area input[type='text']").css("width")
            );

            $("#hint").attr("disabled", true);
            $("#answercontent input").attr("disabled", true);
            $("#answercontent select").attr("disabled", true);
        }


        if (userExercise == null || Khan.query.debug != null) {
            /* JASON BAU COMMENT OUT -- here because the permalinks won't be correct in problem sets
            $("#problem-permalink").text("Permalink: "
                + problemID + " #"
                + problemSeed)
                .attr("href", window.location.protocol + "//" + window.location.host + window.location.pathname + "?debug&problem=" + problemID + "&seed=" + problemSeed);
             */
        }

        // Show the debug info
        if (testMode && Khan.query.debug != null) {
            $(document).keypress(function(e) {
                if (e.charCode === 104) {
                    $("#hint").click();
                }
            });
            var debugWrap = $("#debug").empty();
            var debugURL = window.location.protocol + "//" + window.location.host + window.location.pathname +
                "?debug&problem=" + problemID;

            $("<h3>Debug Info</h3>").appendTo(debugWrap);

            var src = exercise.data("src");
            if (src != null) {
                var srcInfo = $("<p>").appendTo(debugWrap);
                srcInfo.append("From ");

                $("<a>")
                    .text(src)
                    .attr("href", src + "?debug")
                    .appendTo(srcInfo);
            }

            var links = $("<p>").appendTo(debugWrap);

            if (!Khan.query.activity) {
                var historyURL = debugURL + "&seed=" + problemSeed + "&activity=";
                $("<a>Problem history</a>").attr("href", "javascript:").click(function(event) {
                    window.location.href = historyURL + encodeURIComponent(JSON.stringify(userActivityLog));
                }).appendTo(links);
            } else {
                $("<a>Random problem</a>")
                    .attr("href", window.location.protocol + "//" + window.location.host + window.location.pathname + "?debug")
                    .appendTo(links);
            }

            links.append("<br><b>Problem types:</b><br>");

            exercises.children(".problems").children().each(function(n, prob) {
                var probID = $(prob).attr("id") || n;
                links.append($("<div>")
                    .css({
                        "width": "200px",
                        "padding-left": "20px",
                        "outline":
                            (problemID === probID || problemID === '' + n) ?
                            "1px dashed gray" : ""
                    })
                    .append($("<span>").text(n + ": "))
                    .append($("<a>")
                        .text(probID)
                        .attr("href", window.location.protocol + "//" +
                            window.location.host + window.location.pathname +
                            "?debug&problem=" + probID)
                    ));
            });


            if (exercise.data("name") != null) {
                links.append("<br>");
                links.append("Original exercise: " + exercise.data("name"));
            }

            if ($.tmpl.DATA_ENSURE_LOOPS > 0) {
                var dataEnsureInfo = $("<p>");
                dataEnsureInfo.append("Data-ensure loops: " + $.tmpl.DATA_ENSURE_LOOPS);
                if ($.tmpl.DATA_ENSURE_LOOPS > 15) {
                    dataEnsureInfo.css("background-color", "yellow");
                }
                if ($.tmpl.DATA_ENSURE_LOOPS > 30) {
                    dataEnsureInfo.css("background-color", "orange");
                }
                if ($.tmpl.DATA_ENSURE_LOOPS > 50) {
                    dataEnsureInfo.css("background-color", "red");
                }
                dataEnsureInfo.appendTo(debugWrap);
            }

            if (typeof $.tmpl.VARS !== "undefined") {
                var varInfo = $("<p>");

                $.each($.tmpl.VARS, function(name, value) {
                    var str;

                    if (typeof value === "function") {
                        str = value.toString();
                    } else {
                        // JSON is prettier (when it works)
                        try {
                            str = JSON.stringify(value);
                        } catch (e) {
                            str = value.toString();
                        }
                    }

                    varInfo.append($("<b>").text(name));
                    varInfo.append(": ");
                    varInfo.append($("<var>").text(str));
                    varInfo.append("<br>");
                });

                varInfo.appendTo(debugWrap);
            }

            // for special style rules

            $("body").addClass("debug");
        }

        hintsUsed = 0;
        attempts = 0;
        lastAction = (new Date).getTime();

        $("#hint").val("I'd like a hint");

        $(Khan).trigger("newProblem");

        // If the textbox is empty disable "Check Answer" button
        // Note: We don't do this for number line etc.
        if (answerType === "text" || answerType === "number") {
            var checkAnswerButton = $("#check-answer-button");
            checkAnswerButton.attr("disabled", "disabled").attr(
                "title", "Type in an answer first.");
            // Enables the check answer button - added so that people who type
            // in a number and hit enter quickly do not have to wait for the
            // button to be enabled by the key up
            $("#solutionarea")
                .keypress(function(e) {
                    if (e.keyCode !== 13) {
                        checkAnswerButton.removeAttr("disabled").removeAttr("title");
                    }
                })
                .keyup(function() {
                    validator();
                    if (checkIfAnswerEmpty()) {
                        checkAnswerButton.attr("disabled", "disabled");
                    } else {
                        checkAnswerButton.removeAttr("disabled");
                    }
                });
        }

        //console.log('Showing solution area for ' + id);
        if (typeof userPSData == "undefined" || 
            typeof userPSData.problems == "undefined" ||
            typeof userPSData.problems[id] == "undefined" ||
            !userPSData.problems[id]["correct"]) {
            $('#solutionarea').css('visibility', 'visible');
        }

        // [C2G] Keep tabs on current problem index
        if (typeof c2gConfig != "undefined") {
            c2gConfig.currentProblemIdx = id;
        }

        return answerType;
    }   // end makeProblem

    function clearExistingProblem() {
        $("#solutionarea").html("");

        enableCheckAnswer();

        $("#happy").hide();
        if (!$("#examples-show").data("show")) {
            $("#examples-show").click();
        }

        // Toggle the navigation buttons
        $("#check-answer-button").show();
        $("#next-question-button").blur().hide();
        $("#positive-reinforcement").hide();

        // Wipe out any previous problem
        $("#workarea, #hintsarea").runModules(problem, "Cleanup").empty();
        $("#hint").attr("disabled", false);

        Khan.scratchpad.clear();
    }

    KhanC2G.clearExistingProblem=clearExistingProblem;
    KhanC2G.makeProblem=makeProblem;
    KhanC2G.makeProblemBag=makeProblemBag;
    KhanC2G.getExercises=function(){return exercises;} ;
    KhanC2G.getProblems=function(){return  exercises.children(".problems").children();};

    function renderNextProblem(nextUserExercise) {
        clearExistingProblem();

        if (testMode && Khan.query.test != null && dataDump.problems.length + dataDump.issues >= problemCount) {
            // Show the dump data
            $("#problemarea").append(
                "<p>Thanks! You're all done testing this exercise.</p>" +
                "<p>Please copy the text below and send it to us.</p>"
            );

            $("<textarea>")
                .val("Khan.testExercise(" + JSON.stringify(dataDump) + ");")
                .css({width: "60%", height: "200px"})
                .prop("readonly", true)
                .click(function() {
                    this.focus();
                    this.select();
                })
                .appendTo("#problemarea");

            $("#sidebar").hide();

        } else {

            if (testMode) {
                // Just generate a new problem from existing exercise
                makeProblem();
            } else {
                loadAndRenderExercise(nextUserExercise);
            }

        }
    }

    function prepareSite() {

        // TODO(david): Don't add homepage elements with "exercise" class
        exercises = exercises.add($("div.exercise").detach());

        // Setup appropriate img URLs
        $("#issue-throbber")
            .attr("src", urlBase + "css/images/throbber.gif");

        // Change form target to the current page so errors do not kick us
        // to the dashboard
        $("#answerform").attr("action", window.location.href);

        // Watch for a solution submission
        $("#check-answer-button").click(handleSubmit);
        $("#answerform").submit(handleSubmit);

        // Grab example answer format container
        examples = $("#examples");

        // Build the data to pass to the server
        function buildAttemptData(pass, attemptNum, attemptContent, curTime) {
            var timeTaken = Math.round((curTime - lastAction) / 1000);

            if (attemptContent !== "hint") {
                userActivityLog.push([pass ? "correct-activity" : "incorrect-activity", attemptContent, timeTaken]);
            } else {
                userActivityLog.push(["hint-activity", "0", timeTaken]);
            }

            return {
                // The user answered correctly
                complete: pass === true ? 1 : 0,

                // The user used a hint
                count_hints: hintsUsed,

                // How long it took them to complete the problem
                time_taken: timeTaken,

                // How many times the problem was attempted
                attempt_number: attemptNum,

                // The answer the user gave
                // TODO: Get the real provided answer
                attempt_content: attemptContent,

                // A hash representing the exercise
                // TODO: Populate this from somewhere
                sha1: typeof userExercise !== "undefined" ? userExercise.exerciseModel.sha1 : exerciseId,

                // The seed that was used for generating the problem
                seed: problemSeed,

                // The seed that was used for generating the problem
                problem_type: problemID,

                // Whether we are currently in review mode
                review_mode: (!testMode && Exercises.reviewMode) ? 1 : 0,

                // Whether we are currently in topic mode
                topic_mode: (!testMode && !Exercises.reviewMode && !Exercises.practiceMode) ? 1 : 0,

                // Request camelCasing in returned response
                casing: "camel",

                // The current card data
                card: !testMode && JSON.stringify(Exercises.currentCard),

                // Unique ID of the cached stack
                stack_uid: !testMode && Exercises.completeStack.getUid(),

                // The current topic, if any
                topic_id: !testMode && Exercises.topic && Exercises.topic.id,

                // How many cards the user has already done
                cards_done: !testMode && Exercises.completeStack.length,

                // How many cards the user has left to do
                cards_left: !testMode && (Exercises.incompleteStack.length - 1)
            };
        }

        function handleSubmit() {
            var pass = validator();
            // Stop if the user didn't enter a response
            // If multiple-answer, join all responses and check if that's empty
            // Remove commas left by joining nested arrays in case multiple-answer is nested

            // [C2G] Don't check for empty if this is a summative exercise
            //console.log(exAssessType);
            if (exAssessType !== "summative" && checkIfAnswerEmpty()) {
                return false;
            } else {
                guessLog.push(validator.guess);
            }
            //console.log("still in handleSubmit");

            // Stop if the form is already disabled and we're waiting for a response.
            if ($("#answercontent input").not("#hint,#next-question-button").is(":disabled")) {
                return false;
            }

            $("#answercontent input").not("#check-answer-button, #hint")
                .attr("disabled", "disabled");
            $("#check-answer-results p").hide();

            var checkAnswerButton = $("#check-answer-button");

            // If incorrect, warn the user and help them in any way we can
            if (pass != true) {
                checkAnswerButton
                    .effect("shake", {times: 3, distance: 5}, 80)
                    .val("Try Again");

                // Is this a message to be shown?
                if (typeof pass === "string") {
                    $("#check-answer-results .check-answer-message").html(pass).tmpl().show();
                }

                // Refocus text field so user can type a new answer
                if (lastFocusedSolutionInput != null) {
                    setTimeout(function() {
                        var focusInput = $(lastFocusedSolutionInput);

                        if (!focusInput.is(":disabled")) {
                            // focus should always work; hopefully select will work for text fields
                            focusInput.focus();
                            if (focusInput.is("input:text")) {
                                focusInput.select();
                            }
                        }
                    }, 1);
                }
            }

            if (pass === true) {
                // Problem has been completed but pending data request being
                // sent to server.
                $(Khan).trigger("problemDone");
            }

            // Save the problem results to the server
            var curTime = new Date().getTime();
            var data = buildAttemptData(pass, ++attempts, JSON.stringify(validator.guess), curTime);
            request("problems/" + problemNum + "/attempt", data, function() {

                // TODO: Save locally if offline
                $(Khan).trigger("attemptSaved");

            }, function(xhr) {

                if (xhr.readyState == 0) {
                    // Ignore errors caused by a broken pipe during page unload
                    // (browser navigating away during ajax request).
                    // See http://stackoverflow.com/questions/1370322/jquery-ajax-fires-error-callback-on-window-unload
                    return;
                }
/* Kelvin here. I commented this warning out because it kept showing up whenever questions was answered
 *
                // Error during submit. Disable the page and ask users to
                // reload in an attempt to get updated data.

                // Alert any listeners of the error before reload
                $(Khan).trigger("attemptError", userExercise);

                // Hide the page so users don't continue
                $("#problem-and-answer").css("visibility", "hidden");

                // Warn user about problem, encourage to reload page
                warn(
                    "This page is out of date. You need to <a href='" + window.location.href +
                    "'>refresh</a>, but don't worry, you haven't lost progress. " +
                    "If you think this is a mistake, " +
                    "<a href='http://www.khanacademy.org/reportissue?type=Defect&issue_labels='>tell us</a>."
                );
*/
            }, "attempt_hint_queue");

            if (pass === true) {
                // Correct answer, so show the next question button.
                $("#check-answer-button").hide();
                if (!testMode || Khan.query.test == null) {
                    $("#next-question-button")
                        .removeAttr("disabled")
                        .removeClass("buttonDisabled")
                        .show()
                        .focus();
                    $("#positive-reinforcement").show();
                }
            } else {
                // Wrong answer. Enable all the input elements
                $("#answercontent input").not("#hint")
                    .removeAttr("disabled");
            }

            // Remember when the last action was
            lastAction = curTime;

            $(Khan).trigger("checkAnswer", {
                pass: pass,
                // Determine if this attempt qualifies as fast completion
                fast: (typeof userExercise !== "undefined" && userExercise.secondsPerFastProblem >= data.time_taken)
            });

            //console.log("pass...");
            //console.log(pass);
            return false;
        }   // end of handleSubmit

        // Watch for when the next button is clicked
        $("#next-question-button").click(function(ev) {
            nextProblem(1);
            $(Khan).trigger("gotoNextProblem");

            // Disable next question button until next time
            $(this)
                .attr("disabled", true)
                .addClass("buttonDisabled");
        });

        // If happy face is clicked, pass click on through.
        $("#positive-reinforcement").click(function() {
            $("#next-question-button").click();
        });

        // [C2G] Add ARIA Live Region info to hintsarea
        $('#hintsarea').attr('role', 'region');
        $('#hintsarea').attr('aria-live', 'polite');
        $('#hintsarea').attr('aria-atomic', true);
        $('#hintsarea').attr('aria-relevant', 'additions text');
        // [C2G] Set up corresponding hint button
        $('#hint').attr('title', 'Click to add a hint to the hint area');
        $('#hint').attr('aria-controls', 'hintsarea');

        // Watch for when the "Get a Hint" button is clicked
        $("#hint").click(function() {

            var hint = hints.shift();

            if (hint) {
                $(Khan).trigger("hintUsed");

                hintsUsed += 1;

                var stepsLeft = hints.length + " hint" + (hints.length === 1 ? "" : "s") + " left";
                $(this).val($(this).data("buttonText") || "I'd like another hint (" + stepsLeft + ")");

                var problem = $(hint).parent();

                // Append first so MathJax can sense the surrounding CSS context properly
                $(hint).appendTo("#hintsarea").runModules(problem);

                // Grow the scratchpad to cover the new hint
                Khan.scratchpad.resize();

                // Disable the get hint button
                if (hints.length === 0) {
                    $(Khan).trigger("allHintsUsed");

                    $(this).attr("disabled", true);
                }
            }

            var fProdReadOnly = !testMode && userExercise.readOnly;
            var fAnsweredCorrectly = $("#next-question-button").is(":visible");
            if (!fProdReadOnly && !fAnsweredCorrectly) {
                // Resets the streak and logs history for exercise viewer
                request(
                    "problems/" + problemNum + "/hint",
                    buildAttemptData(false, attempts, "hint", new Date().getTime()),
                    // Don't do anything on success or failure, silently failing is ok here
                    function() {},
                    function() {},
                    "attempt_hint_queue"
                );
            }

        });

        // On an exercise page, replace the "Report a Problem" link with a button
        // to be more clear that it won't replace the current page.
        $("<a>Report a Problem</a>")
            .attr("id", "report").addClass("simple-button green")
            .replaceAll($(".footer-links #report"));

        $("#report").click(function(e) {

            e.preventDefault();

            var report = $("#issue").css("display") !== "none",
                form = $("#issue form").css("display") !== "none";

            if (report && form) {
                $("#issue").hide();
            } else if (!report || !form) {
                $("#issue-status").removeClass("error").html(issueIntro);
                $("#issue, #issue form").show();
                $("html, body").animate({
                    scrollTop: $("#issue").offset().top
                }, 500, function() {
                    $("#issue-title").focus();
                });
            }
        });


        // Hide issue form.
        $("#issue-cancel").click(function(e) {

            e.preventDefault();

            $("#issue").hide(500);
            $("#issue-title, #issue-email, #issue-body").val("");

        });

        // Submit an issue.
        $("#issue form input:submit").click(function(e) {

            e.preventDefault();

            // don't do anything if the user clicked a second time quickly
            if ($("#issue form").css("display") === "none") return;

            var pretitle = exerciseName,
                type = $("input[name=issue-type]:checked").prop("id"),
                title = $("#issue-title").val(),
                email = $("#issue-email").val(),
                path = exerciseFile + "?seed=" +
                    problemSeed + "&problem=" + problemID,
                pathlink = "[" + path + (exercise.data("name") != null && exercise.data("name") !== exerciseId ? " (" + exercise.data("name") + ")" : "") + "](http://sandcastle.khanacademy.org/media/castles/Khan:master/exercises/" + path + "&debug)",
                historyLink = "[Answer timeline](" + "http://sandcastle.khanacademy.org/media/castles/Khan:master/exercises/" + path + "&debug&activity=" + encodeURIComponent(JSON.stringify(userActivityLog)).replace(/\)/g, "\\)") + ")",
                agent = navigator.userAgent,
                mathjaxInfo = "MathJax is " + (typeof MathJax === "undefined" ? "NOT loaded" :
                    ("loaded, " + (MathJax.isReady ? "" : "NOT ") + "ready, queue length: " + MathJax.Hub.queue.queue.length)),
                sessionStorageInfo = (typeof sessionStorage === "undefined" || typeof sessionStorage.getItem === "undefined" ? "sessionStorage NOT enabled" : null),
                warningInfo = $("#warning-bar-content").text(),
                parts = [email ? "Reporter: " + email : null, $("#issue-body").val() || null, pathlink, historyLink, "    " + JSON.stringify(guessLog), agent, sessionStorageInfo, mathjaxInfo, warningInfo],
                body = $.grep(parts, function(e) { return e != null; }).join("\n\n");

            var mathjaxLoadFailures = $.map(MathJax.Ajax.loading, function(info, script) {
                if (info.status === -1) {
                    return [script + ": error"];
                } else {
                    return [];
                }
            }).join("\n");
            if (mathjaxLoadFailures.length > 0) {
                body += "\n\n" + mathjaxLoadFailures;
            }

            // flagging of browsers/os for issue labels. very primitive, but
            // hopefully sufficient.
            var agent_contains = function(sub) {
                    return agent.indexOf(sub) !== -1;
                },
                flags = {
                    ie8: agent_contains("MSIE 8.0"),
                    ie9: agent_contains("Trident/5.0"),
                    chrome: agent_contains("Chrome/"),
                    safari: !agent_contains("Chrome/") && agent_contains("Safari/"),
                    firefox: agent_contains("Firefox/"),
                    win7: agent_contains("Windows NT 6.1"),
                    vista: agent_contains("Windows NT 6.0"),
                    xp: agent_contains("Windows NT 5.1"),
                    leopard: agent_contains("OS X 10_5") || agent_contains("OS X 10.5"),
                    snowleo: agent_contains("OS X 10_6") || agent_contains("OS X 10.6"),
                    lion: agent_contains("OS X 10_7") || agent_contains("OS X 10.7"),
                    scratchpad: (/scratch\s*pad/i).test(body),
                    ipad: agent_contains("iPad")
                },
                labels = [];
            $.each(flags, function(k, v) {
                if (v) labels.push(k);
            });

            if (!type) {
                $("#issue-status").addClass("error")
                    .html("Please specify the issue type.").show();
                return;
            } else {
                labels.push(type.slice("issue-".length));

                var hintOrVideoMsg = "Please click the hint button above to see our solution, or watch a video for additional help.";
                var refreshOrBrowserMsg = "Please try a hard refresh (press Ctrl + Shift + R)" +
                        " or use Khan Academy from a different browser (such as Chrome or Firefox).";
                var suggestion = {
                    "issue-wrong-or-unclear": hintOrVideoMsg,
                    "issue-hard": hintOrVideoMsg,
                    "issue-not-showing": refreshOrBrowserMsg,
                    "issue-other": ""
                }[type];
            }

            if (title === "") {
                $("#issue-status").addClass("error")
                    .html("Please provide a valid title for the issue.").show();
                return;
            }

            var formElements = $("#issue input").add("#issue textarea");

            // disable the form elements while waiting for a server response
            formElements.attr("disabled", true);

            $("#issue-cancel").hide();
            $("#issue-throbber").show();

            var dataObj = {
                title: pretitle + " - " + title,
                body: body,
                labels: labels
            };

            // we try to post ot github without a cross-domain request, but if we're
            // just running the exercises locally, then we can't help it and need
            // to fall back to jsonp.
            $.ajax({

                url: (testMode ? "http://www.khanacademy.org/" : "/") + "githubpost",
                type: testMode ? "GET" : "POST",
                data: testMode ? {json: JSON.stringify(dataObj)} :
                    JSON.stringify(dataObj),
                contentType: testMode ? "application/x-www-form-urlencoded" : "application/json",
                dataType: testMode ? "jsonp" : "json",
                success: function(json) {

                    var data = json.data || json;

                    // hide the form
                    $("#issue form").hide();

                    // show status message
                    $("#issue-status").removeClass("error")
                        .html(issueSuccess(data.html_url, data.title, suggestion))
                        .show();

                    // reset the form elements
                    formElements.attr("disabled", false)
                        .not("input:submit").val("");

                    // replace throbber with the cancel button
                    $("#issue-cancel").show();
                    $("#issue-throbber").hide();

                },
                // note this won't actually work in local jsonp-mode
                error: function(json) {

                    // show status message
                    $("#issue-status").addClass("error")
                        .html(issueError).show();

                    // enable the inputs
                    formElements.attr("disabled", false);

                    // replace throbber with the cancel button
                    $("#issue-cancel").show();
                    $("#issue-throbber").hide();

                }
            });
        });

        $("#warning-bar-close a").click(function(e) {
            e.preventDefault();
            $("#warning-bar").fadeOut("slow");
        });

        $("#scratchpad-show")
            .attr('title', 'Click to toggle scratchpad area')
            .click(function(e) {
                e.preventDefault();
                Khan.scratchpad.toggle();

                if (user) {
                    window.localStorage["scratchpad:" + user] = Khan.scratchpad.isVisible();
                }
            });

        $("#answer_area").delegate("input.button, select", "keydown", function(e) {
            // Don't want to go back to exercise dashboard; just do nothing on backspace
            if (e.keyCode === 8) {
                return false;
            }
        });

        // Prepare for the tester info if requested
        if (testMode && Khan.query.test != null) {
            $("#answer_area").prepend(
                '<div id="tester-info" class="info-box">' +
                    '<span class="info-box-header">Testing Mode</span>' +
                    '<p><strong>Problem No.</strong> <span class="problem-no"></span></p>' +
                    '<p><strong>Answer:</strong> <span class="answer"></span></p>' +
                    "<p>" +
                        '<input type="button" class="pass simple-button green" value="This problem was generated correctly.">' +
                        '<input type="button" class="fail simple-button orange" value="There is an error in this problem.">' +
                    "</p>" +
                "</div>"
            );

            $("#tester-info .pass").click(function() {
                dataDump.problems[dataDump.problems.length - 1].pass = true;
                nextProblem(1);
                $("#next-question-button").trigger("click");
            });

            $("#tester-info .fail").click(function() {
                var description = prompt("Please provide a short description of the error");

                // Don't do anything on clicking Cancel
                if (description == null) return;

                // we discard the info recorded and record an issue on github instead
                // of testing against the faulty problem's data dump.
                var dump = dataDump.problems.pop(),
                    prettyDump = "```js\n" + JSON.stringify(dump) + "\n```",
                    fileName = window.location.pathname.replace(/^.+\//, ""),
                    path = fileName + "?problem=" + problemID +
                        "&seed=" + problemSeed;

                var title = encodeURIComponent("Issue Found in Testing - " + $("title").html()),
                    body = encodeURIComponent([description, path, prettyDump, navigator.userAgent].join("\n\n")),
                    label = encodeURIComponent("tester bugs");

                var err = function(problems, dump, desc) {
                    problems.push(dump);
                    problems[problems.length - 1].pass = desc;
                };

                var comment = function(id) {
                    // If communication fails with the Sinatra app or Github and a
                    // comment isn't created, then we create a test that will always
                    // fail.
                    $.ajax({
                        url: "http://66.220.0.98:2563/file_exercise_tester_bug_comment?id=" + id + "&body=" + body,
                        dataType: "jsonp",
                        success: function(json) {
                            if (json.meta.status !== 201) {
                                err(dataDump.problems, dump, description);
                            } else {
                                dataDump.issues += 1;
                            }
                        },
                        error: function(json) {
                            err(dataDump.problems, dump, description);
                        }
                    });
                };

                var newIssue = function() {
                    // if communication fails with the Sinatra app or Github and an
                    // issue isn't created, then we create a test that will always
                    // fail.
                    $.ajax({
                        url: "http://66.220.0.98:2563/file_exercise_tester_bug?title=" + title + "&body=" + body + "&label=" + label,
                        dataType: "jsonp",
                        success: function(json) {
                            if (json.meta.status !== 201) {
                                err(dataDump.problems, dump, description);
                            } else {
                                dataDump.issues += 1;
                            }
                        },
                        error: function(json) {
                            err(dataDump.problems, dump, description);
                        }
                    });
                };

                $.ajax({
                    url: "https://api.github.com/repos/Khan/khan-exercises/issues?labels=tester%20bugs",
                    dataType: "jsonp",
                    error: function(json) {
                        err(dataDump.problems, dump, description);
                    },
                    success: function(json) {
                        var copy = false;

                        // see if an automatically generated issue for this file
                        // already exists
                        $.each(json.data, function(i, issue) {
                            if (encodeURIComponent(issue.title) === title) {
                                copy = issue.number;
                            }
                        });

                        if (copy) {
                            comment(copy);
                        } else {
                            newIssue();
                        }
                    }
                });

                $("#next-question-button").trigger("click");
            });

            $(document).keyup(function(e) {
                if (e.keyCode === "H".charCodeAt(0)) {
                    $("#hint").click();
                }
                if (e.keyCode === "Y".charCodeAt(0)) {
                    $("#tester-info .pass").click();
                }
                if (e.keyCode === "N".charCodeAt(0)) {
                    $("#tester-info .fail").click();
                }
            });
        }

        // Prepare for the debug info if requested
        if (testMode && Khan.query.debug != null) {
            $('<div id="debug"></div>').appendTo("#answer_area");
        }

        // Register API ajax callbacks for updating UI
        if (typeof APIActionResults !== "undefined") {
            // Display Messages like "You're Proficient" or "You Seem To Be Struggling"
            // TODO: this functionality is currently hidden from power-mode. Restore it.
            // https://trello.com/card/restore-you-re-ready-to-move-on-and-struggling-in-action-messages/4f3f43cd45533a1b3a065a1d/34
            APIActionResults.register("exercise_state",
                function(userState) {
                    var jel = $("#exercise-message-container");
                    if (userState.template !== null) {
                        jel.empty().append(userState.template);
                        setTimeout(function() {jel.slideDown();}, 50);
                    }
                    else {
                        jel.slideUp();
                    }
                }
            );
        }

        $(Khan)
            .bind("updateUserExercise", function(ev, data) {
                // Any time we update userExercise, check if we're setting/switching usernames
                if (data) {
                    user = data.user || user;
                    userCRC32 = user != null ? crc32(user) : null;
                    randomSeed = userCRC32 || randomSeed;
                }
            });

        // Register testMode-specific event handlers
        if (testMode) {

            // testMode automatically advances to the next problem --
            // integrated mode just listens and waits for renderNextProblem

            /* JASON BAU COMMENTED OUT
            $(Khan).bind("gotoNextProblem", function() {
                renderNextProblem();
            });
            */

        }

        Khan.relatedVideos.hookup();

        if (window.ModalVideo) {
            ModalVideo.hookup();
        }
    }   // end of prepareSite function

    if (!testMode) {
        // testMode automatically prepares itself in loadModules,
        // where it loads jQuery and the rest of its dependencies
        // dynamically.
        //
        // Integrated mode already has jQuery, so we listen
        // and wait for the signal to prepare.
        $(Exercises)
            .bind("problemTemplateRendered", prepareSite)
            .bind("readyForNextProblem", function(ev, data) {
                renderNextProblem(data.userExercise);
            })
            .bind("warning", function(ev, data) {
                warn(data.text, data.showClose);
            })
            .bind("upcomingExercise", function(ev, data) {
                startLoadingExercise(data.exerciseId, data.exerciseName, data.exerciseFile);
            });
    }

    function deslugify(name) {
        name = name.replace(/_/g, " ");
        return name.charAt(0).toUpperCase() + name.slice(1);
    }

    function setProblemNum(num) {
        problemNum = num;
        problemSeed = (seedOffset + jumpNum * (problemNum - 1 + seedsSkipped)) % bins;
        problemBagIndex = (problemNum + problemCount - 1) % problemCount;
    }

    function getSeedsSkippedCacheKey() {
        return "seedsSkipped:" + user + ":" + exerciseName;
    }

    /**
     * Advances the seed (as if the problem number had been advanced) without
     * actually changing the problem number. Caches how many seeds we've skipped
     * so that refreshing does not change the generated problem.
     * @param {number} num Number of times to advance the seed.
     */
    function nextSeed(num) {
        seedsSkipped += num;
        if (typeof LocalStore !== "undefined") {
            LocalStore.set(getSeedsSkippedCacheKey(), seedsSkipped);
        }
        setProblemNum(problemNum);
    }

    function nextProblem(num) {
        setProblemNum(problemNum + num);
    }

    function prevProblem(num) {
        nextProblem(-num);
    }

    function setUserExercise(data) {

        userExercise = data;

        if (data && data.exercise) {
            exerciseId = data.exercise;
        }

        $(Khan).trigger("updateUserExercise", userExercise);

        if (user != null) {
            // How far to jump through the problems
            jumpNum = primes[userCRC32 % primes.length];

            // The starting problem of the user
            seedOffset = userCRC32 % bins;

            // The number of seeds that were skipped due to duplicate problems
            seedsSkipped = (typeof LocalStore !== "undefined" &&
                LocalStore.get(getSeedsSkippedCacheKey()) || 0);

            // Advance to the current problem seed
            setProblemNum(userExercise.totalDone + 1);
        }
    }

    function request(method, data, fn, fnError, queue) {

        /*
        if (testMode) {
            // Pretend we have success
            if ($.isFunction(fn)) {
                fn();
            }

            return;
        }
        */

        var xhrFields = {};
        if (typeof XMLHTTPRequest !== "undefined") {
            // If we have native XMLHTTPRequest support,
            // make sure cookies are passed along.
            xhrFields["withCredentials"] = true;
        }

        //Gets the problem ID which is (problem number)-(variation)
        problem_identifier = $('#workarea').children('div').attr('id');
        exercise_filename = exercise.data('fileName');
        exercise_type = $('#exercise_type').val() || 'problemset';
        video_id = $('#video_id').val();
        // [C2G] pset_id of -1 will cause error, but right now just used for in-video
        // Needs to have a real problem set associated with videos
        pset_id = ($('#pset_id').length) ? $('#pset_id').val() : -1;
        if ($('input#testinput').length) {
            user_selection_val = $('input#testinput').val();
        } else if ($('input:radio[name=solution]').length) {
            user_selection_val = $('input:radio[name=solution]:checked').val();
        }
        user_choices = [];
        $('#solutionarea span.value').each(function () {
            user_choices.push($(this).text());
        });
        
        // [C2G] Correct attempt count for when a user reloads the page
        if ($.isNumeric($('#attempt-count').text())) {
            data['attempt_number'] = parseInt($('#attempt-count').text()) + 1;
        }
        data = $.extend(data, {"problem_identifier": problem_identifier});
        data = $.extend(data, {"exercise_filename": exercise_filename});
        data = $.extend(data, {"exercise_type": exercise_type});
        data = $.extend(data, {"video_id": video_id});
        data = $.extend(data, {"pset_id": pset_id});
        data = $.extend(data, {"user_selection_val": user_selection_val});
        //if (exAssessType == "summative") {
        //    data['attempt_content'] = $('input:radio[name=solution]:checked').next('span.value').text();
        //}
        data = $.extend(data, {"user_choices": escape(JSON.stringify(user_choices))});

        // store user_selection_val
        if (KhanC2G.PSActivityLog.exerciseType == 'problemset' && data.attempt_content != "hint") {
            $('.current-question').data("userEntered", user_selection_val);
            var problemIdx = $('.current-question').data("problemIndex");
            KhanC2G.PSActivityLog.problems[problemIdx].userEntered = user_selection_val;
        }

        //URL starts with problemsets/attempt to direct to a view to collect data.
        //problemId is the id of the problem the information is being created for
        var request = {
            // Do a request to the server API
            //url: server + "/api/v1/user/exercises/" + exerciseId + "/" + method,
            url: "/problemsets/attempt/2",
            type: "POST",
            data: data,
            dataType: "json",
            xhrFields: xhrFields,

            // Backup the response locally, for later use
            success: function(data, txtStatus, jqXHR) {

                // [C2G] Record attempts, right or wrong
                var attCt = $('#attempt-count').text();
                var newAttCt = (data['attempt_num']) ? data['attempt_num'] : parseInt(attCt) + 1;
                $('#attempt-count').text(newAttCt);
                
                var currentProblemIdx = $('.current-question').data("problemIndex");
                var currentProblemLog = KhanC2G.PSActivityLog.problems[currentProblemIdx];
                if (currentProblemLog) {
                    currentProblemLog.alreadyAttempted = newAttCt;
                }

                // [C2G] If user got question correct
                if (data['exercise_status'] == "complete") {
                    $('.current-question').addClass('correctly-answered').append('<i class="icon-ok-sign"></i>');
                    $('.current-question').data("correct", true);
                    if ($('.current-question').is($('#questions-stack li:last'))) {
                        $('#next-question-button').val('Correct! View Summary');
                        $('#next-question-button').unbind('click');
                        $('#next-question-button').click(function () {
                            location.href = c2gConfig.progessUrl;
                        });
                    }
                } else {
                    var maxCredit = 100;
                    var maxAttempts = (typeof c2gConfig != "undefined" && c2gConfig.maxAttempts > 0) ? c2gConfig.maxAttempts : 3;

                    // since page displays last attempt count, the display will be behind by one
                    // (i.e. with max of 3 attempts, by the time "Attempts so far" shows as "3",
                    // the credit should reflect "0%")
                    if (newAttCt > (maxAttempts - 1)) {
                        $('#max-credit').text(0);
                    } else {
                        var penaltyPct = (typeof c2gConfig != "undefined" && typeof c2gConfig.penaltyPct != "undefined") ? parseInt(c2gConfig.penaltyPct) : 0;
                        $('#max-credit').text(maxCredit - (penaltyPct * newAttCt));
                    }
                }

                // find current card and stash localUserAnswer in it ("data" is what user submits)
                $('.current-question').data('localUserAnswer', data);

                // Tell any listeners that khan-exercises has new
                // userExercise data
                $(Khan).trigger("updateUserExercise", data);

                if ($.isFunction(fn)) {
                    fn(data);
                }
            },

            complete: function() {
                $(Khan).trigger("apiRequestEnded");
            },

            // Handle error edge case
            error: function(xhr) {

                //console.log(xhr);
                // Clear the queue so we don't spit out a bunch of
                // queued up requests after the error
                if (queue && requestQueue[queue]) {
                    requestQueue[queue].clearQueue();
                }

                if ($.isFunction(fnError)) {
                    fnError(xhr);
                }
            }
        };

        // Send request and return a jqXHR (which implements the Promise interface)
        function sendRequest() {
            // Do request using OAuth, if available
            if (typeof oauth !== "undefined" && $.oauth) {
                return $.oauth($.extend({}, oauth, request));
            }

            return $.ajax(request);
        }

        // We may want to queue up the requests so that they're sent serially.
        //
        // We currently do this for problem attempts and hints to avoid a race
        // condition:
        // 1) request A fetches UserExercise X
        // 2) request B also fetches X
        // 3) A finishes updating X and saves as A(X)
        // 4) now B finishes updating X and overwrites A(X) with B(X)
        // ...when what we actually wanted saved is B(A(X)). We should really fix it
        // on the server by running the hint and attempt requests in transactions.
        if (queue != null) {
            // Create an empty jQuery object to use as a queue holder, if needed.
            requestQueue[queue] = requestQueue[queue] || jQuery({});

            // Queue up sending the request to run when old requests have completed.
            requestQueue[queue].queue(function(next) {
                sendRequest().always(next);
            });
        } else {
            sendRequest();
        }

        // Trigger an apiRequestStarted event here, and not in the inner sendRequest()
        // function, because listeners should know an API request is waiting as
        // soon as it gets queued up.
        $(Khan).trigger("apiRequestStarted");
    }

    function loadExercise(callback) {

        var self = $(this).detach();
        var id = self.data("name");
        var weight = self.data("weight");
        var rootName = self.data("rootName");
        var fileName = self.data("fileName");
        // TODO(eater): remove this once all of the exercises in the datastore have filename properties
        if (fileName == null || fileName == "") {
            fileName = id + ".html";
        }

        if (!loadingExercises[rootName]) {
            loadingExercises[rootName] = 0;
        }

        loadingExercises[rootName]++;

        // Packing occurs on the server but at the same "exercises/" URL
        //
        // C2G: we use a different place for the exercises (originally was with the rest of the static files)
        // since we need to get from S3
        var dfd = $.Deferred();

        $.ajaxSetup({timeout:10000});
        $.get(urlBaseExercise + "exercises/" + fileName, function(data, status, xhr) {
            var match, newContents;

            if (!(/success|notmodified/).test(status)) {
                // Maybe loading from a file:// URL?
                Khan.error("Error loading exercise from file " + fileName + xhr.status + " " + xhr.statusText);
                return;
            }

            // Get rid of any external scripts in data before we shove data
            // into a jQuery object. IE8 will attempt to fetch these external
            // scripts otherwise.
            // See https://github.com/Khan/khan-exercises/issues/10957
            data = data.replace(/<script(\s)+src=([^<])*<\/script>/, "");

            newContents = $(data);

            // Name of the top-most ancestor exercise
            newContents.data("rootName", rootName);

            // Maybe the exercise we just loaded loads some others
            newContents.filter("[data-name]").each(function() {
                loadExercise.call(this, callback);
            });
            // Throw out divs that just load other exercises
            newContents = newContents.not("[data-name]");

            // Save the id, fileName and weights
            // TODO(david): Make sure weights work for recursively-loaded exercises.
            newContents.data("name", id).data("fileName", fileName).data("weight", weight);

            // [C2G] Add to our global object
            KhanC2G.remoteExercises.push(newContents);

            // Add the new exercise elements to the exercises DOM set
            exercises = exercises.add(newContents);

            // Extract data-require
            var requires = data.match(/<html(?:[^>]+)data-require=(['"])((?:(?!\1).)*)\1/);

            if (requires != null) {
                requires = requires[2];
            }

            Khan.require(requires);

            // Extract contents from various tags and save them up for parsing when
            // actually showing this particular exercise.
            var tagsToExtract = {
                title: /<title>([^<]*(?:(?!<\/title>)<[^<]*)*)<\/title>/gi,

                // Scripts with no src
                script: /<(?:)script\b[^s>]*(?:(?!src=)s[^s>]*)*>([^<]*(?:(?!<\/script>)<[^<]*)*)<\/script>/gi,

                style: /<style[^>]*>([\s\S]*?)<\/style>/gi
            };

            $.each(tagsToExtract, function(tag, regex) {
                var result = [];
                while ((match = regex.exec(data)) != null) {
                    result.push(match[1]);
                }

                newContents.data(tag, result);
            });

            loadingExercises[rootName]--;

            if (loadingExercises[rootName] === 0) {

                if (!modulesLoaded) {
                    modulesDeferred = $.Deferred();
                    loadModules();
                }

                if (callback) {
                    modulesDeferred.done(callback);
                }

            }

        // [C2G] setTimeout below is to allow enough time for last exercise to be properly loaded
        }).done(setTimeout(function () { dfd.resolve(); }, 5000));

        return dfd.promise();
    }

    function loadModules() {

        modulesLoaded = true;

        // Load module dependencies
        Khan.loadScripts($.map(Khan.modules, function(mod, name) {
            return mod;
        }), function() {

            $(function() {
                // Inject the site markup, if it doesn't exist
                if ($("#answer_area").length === 0) {
                    /*
                    $.ajax({
                        url: urlBase + "exercises/khan-site.html",
                        dataType: "html",
                        success: function(html) {
                     */

                            $.ajax({
                                url: urlBase + "exercises/khan-exercise.html",
                                dataType: "text",
                                success: function(htmlExercise) {
                                    //injectTestModeSite(html, htmlExercise);
                                   injectExerciseFrameMarkup(htmlExercise);
                                   finishSitePrep();

                                }
                            });
                     /*
                        }
                    });
                      */
                } else {
                    if (modulesDeferred) {
                        modulesDeferred.resolve();
                    }
                  finishSitePrep();
                }
            });
        });

        function injectExerciseFrameMarkup(htmlExercise) {

            // [C2G] Need prepend, as slow connection causes video div to be overwritten
            // for in-video exercises
            //$("#container .exercises-body .current-card-contents").html(htmlExercise);
            $("#container .exercises-body .current-card-contents").prepend(htmlExercise);

        }

        function injectTestModeSite(html, htmlExercise) {
            $("body").prepend(html);

            $("#container .exercises-header h2").append($('<span>').html(document.title));
            injectExerciseFrameMarkup(htmlExercise);

            if (Khan.query.layout === "lite") {
                $("html").addClass("lite");
            }

            finishSitePrep();

        }

        function finishSitePrep() {

            prepareSite();

            initC2GActivityLog();

            initC2GStacks(exercises);

            var problems = exercises.children(".problems").children();
            globalProblems=problems;
            globalExercises=exercises;
            // Don't make the problem bag when a specific problem is specified
            // because it messes up problem permalinks (because makeProblemBag
            // calls KhanUtil.random() and changes the seed)

            // [C2G] Removing problem bag as we don't want randomized problems now
            /*
            if (Khan.query.problem == null) {
              weighExercises(problems);
              problemBag = makeProblemBag(problems, 10);
            }
            */

            // Generate the initial problem when dependencies are done being loaded
            //var answerType = makeProblem();

            // [C2G] moves to viewed list, as it's currently being viewed
            var first = $('#questions-viewed li:first-child');

            // [C2G] Set up cards so the first one not done is the "current card"
            function configureCards () {
                var cardArr = $('#questions-stack li').toArray();
                //console.log($('li.current-question'));
                $('li.current-question').removeClass('current-question');
                for (var c = 0; c <= cardArr.length; c += 1) {
                    if ($(cardArr[c]).hasClass('correctly-answered')) {
                        $('#questions-viewed ol').append($(cardArr[c]));
                    } else {
                        $(cardArr[c]).addClass('current-question');
                        break;
                    }
                }

                // [C2G] Handle case where user returns to problemset page
                // after answering all questions correctly; make first question
                // current
                if ($('.current-question').length == 0) {
                    $(cardArr[0]).addClass('current-question');
                }

                KhanC2G.remoteExPollCount = 0;
                var pollForRemoteEx = function() {

                    // [C2G] Another safeguard for no current-question cards
                    var pID = $('.current-question').data("problemIndex") || 0;
                    var pSeed = 0;  // Fallback
                    if ($('.current-question') && $('.current-question').data("problemSeed")) {
                        pSeed = parseInt($('.current-question').data("problemSeed"));
                    }
                    //console.log(pID);
                    if (KhanC2G.remoteExPollCount > 50) {
                        $('#workarea .loading').text("Exercise " + (parseInt(pID) + 1) + " could not be loaded.");
                        KhanC2G.remoteExPollCount = 0;
                        return;
                    }

                    if (KhanC2G.remoteExercises[pID]) {
                        $('#workarea').remove('.loading');
                        KhanC2G.remoteExPollCount = 0;
                        if ($('.current-question').data('problemSeed')) {
                            makeProblem(pID, pSeed);
                        } else {
                            makeProblem(pID);
                        }
                    } else {
                        if ($('#workarea .loading').length == 0) {
                            $('#workarea').append('<p class="loading">Loading Exercise ' + (parseInt(pID) + 1) + '...</p>');
                        }
                        $('#workarea .loading').append('.');
                        setTimeout(function () { KhanC2G.remoteExPollCount++; pollForRemoteEx(); }, 500);
                    }
                };
                pollForRemoteEx();
            }
            
            if ($('#exercise_type').val() != "video") {
                configureCards();
            }

        }

    }

    //var c2gProblemBag;

    function initC2GActivityLog () {
        KhanC2G.PSActivityLog = {};
        KhanC2G.PSActivityLog.exerciseType = ($('#exercise_type').length) ? ($('#exercise_type').val()) : "problemset";
        if (typeof exAssessType != "undefined") {
            KhanC2G.PSActivityLog.assessType = exAssessType;
        } else {
            KhanC2G.PSActivityLog.assessType = "formative";
        }

        if (typeof c2gConfig != "undefined" && c2gConfig.user) {
            KhanC2G.PSActivityLog.user = c2gConfig.user;
        } else {
            KhanC2G.PSActivityLog.user = "anon";
        }

        KhanC2G.PSActivityLog.problems = [];

        KhanC2G.PSActivityLog.addProblem = function (obj) {
            var _self = this;
            if (obj) {
                _self.problems.push(obj);
            } else {
                var problemIdx = _self.problems.length;
                var emptyProblem = {
                    problemIndex: problemIdx,
                    problemSeed: null,
                    exerciseFile: "",
                    viewed: false,
                    attempts: 0,
                    userEntered: "",
                    correct: false
                };
                _self.problems.push(emptyProblem);
            }
        }


    }

    function initC2GStacks(exercises) {
        //Setup 2 stack structures: questions-to-do and questions-done, as children
        //of <div id="problem-and-answer">
        $('#problem-and-answer').css('position', 'relative');

        $('#problem-and-answer').append($('<div id="questions-stack"></div>'));
        $('#questions-stack').append($('<div id="questions-viewed"><ol></ol></div>'));
        $('#questions-stack').append($('<div id="questions-unviewed"><ol></ol></div>'));
        $('#questions-stack').click(stackClickHandler);

        //populate 1 questions-to-do for each exercise
        var curNumProbs = 0;
        KhanC2G.PSActivityLog.totalProblems = 0;

        if (KhanC2G.PSActivityLog.exerciseType == 'problemset') { 
            // turn userPSData.problems into a local associative array 
            var attemptedProblems = {};
            var userPSProblemsLen = userPSData.problems.length;
            for (var p = 0; p < userPSProblemsLen; p += 1) {
                attemptedProblems[userPSData.problems[p].problem_index] = userPSData.problems[p];
            }

            $(exercises).filter(".exercise").each(function(idx, elem) {

                //debugger;
                if (typeof userPSData != "undefined" && 
                    typeof userPSData.problems != "undefined" && 
                    userPSData.problems[idx.toString()]) {
                }

                //Figure out how many problems there are in this exercise
                var probsInExercise=$(elem).children('.problems').children().length;

                $(elem).data('problemsStartAtIndex',curNumProbs);
                $(elem).data('numberOfProblems',probsInExercise);
                var li = $("<li>");

                li.text("Q" + (idx + 1));
                //this data 'problem' will be used to index into the problems array
                //the problems array is a flat array containing all problems from all exercises
                //we do the counting above to get a problem index in the right range for this exercise

                // [C2G] We don't want to randomize anymore, so changing problem to evaluate
                // to the index
                //li.data('problem',curNumProbs+Math.floor(Math.random()*probsInExercise));
                li.data('problemIndex',idx);
                //li.data('randseed',Math.floor(Math.random()*100000));
                if (typeof attemptedProblems != "undefined" && attemptedProblems[idx.toString()]) {
                    var userQDataObj = attemptedProblems[idx.toString()];
                    li.data('problemSeed', parseInt(userQDataObj.problem_seed));
                    li.data('userEntered', userQDataObj.user_selection_val);
                    li.data('correct', userQDataObj.correct);
                    li.data('userChoices', userQDataObj.user_choices);
                    li.data('alreadyAttempted', userQDataObj.already_attempted);
                }
                if (li.data('correct')) {
                    li.addClass("correctly-answered").append('<i class="icon-ok-sign"></i>');
                }

                // Merge list item data into KhanC2G.PSActivityLog so they're synched
                KhanC2G.PSActivityLog.addProblem(li.data());            

                $.extend(li.data(), $(elem).data());
                if (idx == 0) {
                    $('#questions-viewed ol').append(li);
                } else {
                    $('#questions-unviewed ol').append(li);
                }

                KhanC2G.PSActivityLog.totalProblems += 1;

                curNumProbs+=probsInExercise;

            });

            // [C2G] Add keyboard nav to questions
            $(document).keydown(function (ev) {
                var allCards = $('#questions-stack li');
                var currentIdx = parseInt(allCards.index($('.current-question')));
                var moveToCard = function (idx) {
                    idx = parseInt(idx);
                    if (idx < 0) idx = allCards.length - 1;
                    if (idx >= allCards.length) idx = 0;
                    $(allCards[idx]).trigger("click");
                };

                if (ev.keyCode == "37" || ev.keyCode == "38") {
                    moveToCard(currentIdx - 1);
                } else if (ev.keyCode == "39" || ev.keyCode == "40") {
                    moveToCard(currentIdx + 1);
                }
            });

            // [C2G] Add "View Progress" button to all problem sets
            $('#answer_area').append('<div class="info-box"><input type="button" class="simple-button green full-width" id="view-progress-button" value="View Problem Set Progress"/></div>');
            $('#view-progress-button').click(function () {
                location.href = (c2gConfig.PSProgressUrl) ? c2gConfig.PSProgressUrl : 'problemsets';
            });

        }
        // This will be important when a user returns to the page after 
        // having attempted at least one problem
        /*
        if (typeof userPSData != "undefined" && userPSData.problems) {
            for (var p = 0; p < userPSData.problems.length; p += 1) {
                var problemObj = KhanC2G.PSActivityLog.problems[userPSData.problems[p].problem_index];
                problemObj.problemIndex = userPSData.problems[p].problem_index;
                problemObj.problemSeed = userPSData.problems[p].problem_seed;
                problemObj.viewed = true;
                problemObj.attempts = userPSData.problems[p].already_attempted;
                problemObj.userChoices = userPSData.problems[p].user_choices;
                problemObj.userEntered = userPSData.problems[p].user_selection_val;
                problemObj.correct = userPSData.problems[p].correct;
            }
        }
        */

        // [C2G] It takes some time for the answer_area inputs to show up with page, exercise,
        // et al loading, then makeProblem() being called
        var checkForInputs = function() {

            var dfd = $.Deferred();

            var counter = 0;
            setTimeout(function checkInputs() {
                if (($('#testinput').length > 0) || ($('#solutionarea input:radio').length > 0)) {
                    dfd.resolve(true);  // [C2G] Resolve with a value of "true" to pass on
                } else {
                    if (dfd.state() === "pending") {
                        dfd.notify("Still checking...");
                        setTimeout(checkInputs, 1000)
                    } else {
                        dfd.reject("Sorry, answer input not available");
                    }
                };
            }, 1000);

            return dfd.promise();

        };

        // [C2G] When the inputs are available, pre-populate current one with the current question's
        // value, if the user has already answered it
        $.when(checkForInputs()).then(function () {
            //console.log("initC2GStacks, makeProblem about to be called...");
            var pID = $('.current-question').data('problemIndex') || 0;
            var pSeed = 0;  // Fallback
            if ($('.current-question') && $('.current-question').data('problemSeed')) {
                pSeed = parseInt($('.current-question').data('problemSeed'));
            }

            // [C2G] What did user enter last?
            var userSelectionVal = null;
            if (typeof KhanC2G.PSActivityLog != "undefined" && 
                typeof KhanC2G.PSActivityLog.problems != "undefined" && 
                KhanC2G.PSActivityLog.problems[pID] && 
                KhanC2G.PSActivityLog.problems[pID]['userEntered']) {
                userSelectionVal = KhanC2G.PSActivityLog.problems[pID]['userEntered'];
            } else if ($('.current-question').data("userEntered")) {
                userSelectionVal = $('.current-question').data("userEntered");
            } 

            // [C2G] If user entered something previously...
            if (userSelectionVal) {
                if ($('#testinput').length) {
                    $('#testinput').val(userSelectionVal);
                    if ($('.current-question').data('correct')) {
                        $('#testinput').attr('disabled','disabled');
                    }
                } else if ($('#solutionarea input:radio').length) {
                    $('#solutionarea input')[userSelectionVal].checked = true;
                    if ($('.current-question').data('correct')) {
                        $('#solutionarea input').attr('disabled','disabled');
                    }
                }
            // [C2G] Otherwise, clear value so other problem answers don't bleed over
            } else {
                if ($('#testinput').length) {
                    $('#testinput').val("");
                } else if ($('#solutionarea input:radio:checked').length) {
                    $('#solutionarea input:radio:checked').attr('checked', false);
                }
            }

            $('#solutionarea').css('visibility', 'visible');
        });

        // set class on last question to show it is the current one
        $('#questions-viewed li:first-child').addClass('current-question');

        $('#next-question-button').click(function () {

            var currentQCard = $('.current-question');

            var userAnswer = readOnlyChoices = null;
            if ($('input#testinput').length) {
                userAnswer = $('input#testinput').val();
            } else if ($('input:radio[name=solution]').length) {
                userAnswer = $('input:radio[name=solution]:checked').val();
                readOnlyChoices = [];
                $('#solutionarea span.value').each(function () {
                    readOnlyChoices.push($(this).text());
                });
            }

            currentQCard.data('userAnswer', userAnswer);
            currentQCard.data('readOnlyChoices', readOnlyChoices);
            currentQCard.removeClass('current-question');

            $('#questions-unviewed li:first-child').trigger('mouseout');
            $('#questions-unviewed li:first-child').appendTo($('#questions-viewed').children('ol'));

            //var next = (currentQCard.next().length) ? currentQCard.next() : $('#questions-viewed li:last-child');
            //var next = (currentQCard.next().length) ? currentQCard.next() : $('#questions-viewed li:first-child');

            var currentCardIdx = currentQCard.data("problemIndex");
            var totalCards = $('#questions-stack li');
            var totalCardsLen = totalCards.length;
            var next = null;
            if (currentCardIdx >= totalCardsLen) {
                next = $(totalCards[0]);
            } else {
                next = $(totalCards[currentCardIdx + 1]);
            }

            next.addClass('current-question');

            clearExistingProblem();

            if (next.length) {
                makeProblem(next.data('problemIndex'), next.data('problemSeed'));
            }


            // [C2G] if this is a summative problem set and all questions have been viewed
            if ((exAssessType == "summative" || KhanC2G.PSActivityLog.assessType == "summative") && 
                $('.current-question').is($('#questions-stack li:last'))) {
                if ($('#submit-problemset-button').length) {
                    $('#submit-problemset-button').parent().show();
                } else {
                    $('#answer_area').append('<div class="info-box"><input type="button" class="simple-button green full-width" id="submit-problemset-button" value="Submit Problem Set"/></div>');
                    $('#submit-problemset-button').click(function () {
                        location.href = (c2gConfig.PSProgressUrl) ? c2gConfig.PSProgressUrl : 'problemsets';
                    });
                }
            } else if ($('#submit-problemset-button').length) {
                $('#submit-problemset-button').parent().hide();
            }

        });

        $('#questions-unviewed').fadeIn('slow');
        $('#questions-viewed').fadeIn('slow');

        // [C2G] Make use of event delegation by setting click handler on the common
        // questions-stack parent
        function stackClickHandler(ev) {

            ev.stopPropagation();
            var clickTarget = ev.target;
            // if user clicks on green checkmark icon, find parent card upon which to trigger click
            var thisCard = (clickTarget.tagName == 'li') ? $(clickTarget) : $(clickTarget).closest('li');
            if (thisCard.length == 0) {
                return;
            }

            // whichever is the current card, make it not the current card
            thisCard.trigger('mouseout');
            if (!thisCard.hasClass('current-question')) {

                $('.current-question').removeClass('current-question');
                clearExistingProblem();

                thisCard.addClass('current-question');

            }

            var pollForRemoteEx = function() {

                if (KhanC2G.remoteExPollCount > 50) {
                    $('#workarea .loading').text("Exercise " + (parseInt(thisCard.data("problemIndex")) + 1) + " could not be loaded.");
                    KhanC2G.remoteExPollCount = 0;
                    return;
                }

                if (KhanC2G.remoteExercises[thisCard.data('problemIndex')]) {
                    $('#workarea').remove('.loading');
                    KhanC2G.remoteExPollCount = 0;
                    makeProblem(thisCard.data('problemIndex'), thisCard.data('problemSeed'));
                    // [C2G] Make solutionarea visible again
                    $('#solutionarea').css('visibility', 'visible');
                } else {
                    if ($('#workarea .loading').length == 0) {
                        $('#workarea').append('<p class="loading">Loading Exercise ' + (parseInt(thisCard.data("problemIndex")) + 1) + '...</p>');
                    }
                    $('#workarea .loading').append('.');
                    setTimeout(function () { KhanC2G.remoteExPollCount++; pollForRemoteEx(); }, 500);
                }
            };

            pollForRemoteEx();

            // load previous answers into the solution area
            $.when(checkForInputs()).then(function () {
                var userPrevSel = thisCard.data("userEntered");
                var validUserChoices = thisCard.data("userChoices");
                var userChoicesLen = (typeof validUserChoices != "undefined") ? $.parseJSON(thisCard.data("userChoices")).length : 0;
                // [C2G] Just having something in "user_choices" doesn't mean it's valid, it could be an
                // empty array within a string, which is a non-empty string; have to convert to a real array and
                // check its length
                if (userChoicesLen > 0 && thisCard.data("correct")) {
                    var choicesArr = $.parseJSON(thisCard.data("userChoices"));
                    var userSel = userPrevSel;
                    if ($('#solutionarea input:radio').length) {
                        $('#solutionarea input:radio')[userSel].checked = true;
                    }
                    $('#check-answer-button').attr('disabled', 'disabled');
                } else if (userPrevSel && $(ev.target).data("correct")) {
                    $('input#testinput').val(userPrevSel).attr('disabled', 'disabled');
                    $('#check-answer-button').attr('disabled', 'disabled');
                    $('#solutionarea').css('visibility', 'visible');
                } else {
                    if ($('input#testinput').length) {
                        if (userPrevSel) {
                            $('input#testinput').val(userPrevSel); 
                        } else {
                            $('input#testinput').val("");   // explicitly clear 
                        }
                        $('input#testinput').removeAttr('disabled');
                    } else if ($('input:radio').length) {
                        if (userPrevSel) {
                            $('#solutionarea input:radio')[userPrevSel].checked = true; 
                        } else {
                            // explicitly clear 
                            $('#solutionarea input:radio:checked').attr('checked', false); 
                        }
                        $('input:radio').removeAttr('disabled');
                    }
                    $('#check-answer-button').removeAttr('disabled');
                }
            });

        }

        // [C2G] Still within initC2GStacks()

    }

    // [C2G] Called for in-video exercises
    KhanC2G.initVideoExercises = function () {
        $('.current-card-contents').append($('div.content'));
        $('.current-card-contents').css('min-height', '600px');
        $('div.content').css('position', 'absolute').css('top', '10px').css('left','10px');

        $('#container').css('padding-top',0);
        $('#examples-show').hide();

        var skipBtn = document.createElement('input');
        $(skipBtn).attr('id', 'skip-button');
        $(skipBtn).attr('type', 'button');
        $(skipBtn).attr('value', 'Skip Question');
        $(skipBtn).attr('title', 'Skip this question and return to the video');
        $(skipBtn).addClass('simple-button').addClass('green').addClass('full-width');
        $('#check-answer-button').after($(skipBtn));
        $(skipBtn).click(function () { $('#next-question-button').trigger('click'); })
        $('#next-question-button').val("Correct! Resume Video");

        $('#next-question-button').unbind('click');
        $('#next-question-button').click(function () {

            $('#questionBG').remove();
            $('#questionPane').remove();
            $('#problemarea').css('z-index', 0);

            $('#playerdiv').fadeTo('slow', 1.0);
            $('.video-overlay-question').hide();
            $('.video-overlay-hint').hide();
            $('#answer_area').fadeOut('slow');
            $("#slideIndex").show();

            player.playVideo();
        });
    };

    return Khan;

})();

var globalProblems, globalExercises;
// Make this publicly accessible
var KhanUtil = Khan.Util;
