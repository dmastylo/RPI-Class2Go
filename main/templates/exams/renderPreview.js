var c2gXMLParse = (function() {
   
    var c2gXMLParse = {
         alphastring : "abcdefghijklmnopqrstuvwxyz",
        
         numToID: function(pos_int) {
            if (pos_int===0)
                   return "a";
            outstring="";
            while (pos_int > 0) {
                outstring = c2gXMLParse.alphastring[pos_int % 26] + outstring;
                pos_int = Math.floor(pos_int/26);
            }
            return outstring;
         },
                   
        specialNodes: "multiplechoiceresponse,numericalresponse,stringresponse,regexresponse,optionresponse,solution",
        
        renderPreview: function() {
            $('#staging-area').empty();
            $('#staging-area').append(editor.getValue());
        },

        renderMarkup: function(sourceEl, targetEl) {

            if (typeof targetEl == "undefined" || targetEl == "") {
                targetEl = $('#ace_proxy');
                editor.setValue(""); 
            }

            //$('#staging-area').empty();
            $(targetEl).empty();

            // Set up XML DOM
            //var sourceXML = editor.getValue();
            var sourceXML = $(sourceEl).val();
            try {
                var myDOM = $.parseXML(sourceXML);
            } catch (e) {
                alert('Your XML is invalid');
                console.log(e.message);
                return;
            }

            var problemNodes = $(myDOM).find('problem');

            //Helper function
            var isChoiceCorrect = function(choiceElem) {
                if (!$(choiceElem).attr('correct')) {
                    return false;
                }
                return $(choiceElem).attr('correct').toLowerCase()==='true';
            }
              
            var questionIdx = 0;
                   
            var outerMetadataObj = document.createElement('metadata'); //outermost metadata--won't actually be displayed since we use $.html()
            var metadataObj = document.createElement('exam_metadata');
            $(outerMetadataObj).append($(metadataObj));
            //Build up a DOM object corresponding to the answer key
            var answerkeyObj = document.createElement('answerkey');
            problemNodes.each(function () {

                questionIdx += 1;
                var questionMeta=document.createElement('question_metadata');
                $(questionMeta).attr('id', 'problem_'+questionIdx);
                $(questionMeta).attr('data-tag4humans', $(this).attr('tag4humans'));
                $(metadataObj).append($(questionMeta));
                
                              
                            
                //Grab question level solutions
                var solnObj = document.createElement('solution');
                $(this).find('solution').find('p').each(function() {
                    var tempP = document.createElement('p');
                    $(tempP).text($(this).text());
                    $(solnObj).append($(tempP));
                });
                $(questionMeta).append($(solnObj));
                              
                var tmpProbDiv = document.createElement('div');
                $(tmpProbDiv).addClass('question');
                $(tmpProbDiv).attr('id', 'problem_'+questionIdx);
                $(tmpProbDiv).attr('data-tag4humans', $(this).attr('tag4humans'));
                              
                //$('#staging-area').append($(tmpProbDiv));
                $(targetEl).append($(tmpProbDiv));
                
                var allChildren = $(this).children();
                
                var renderResponseNode = function (node, arg2, idx_suffix) {
            
                    var nodeName = $(node)[0].nodeName;
                    var nodeParent = arguments[1] || $(tmpProbDiv);
                                              
                    switch (nodeName) {
                        case 'multiplechoiceresponse':
                            
                            var choices = $($(node)).find('choice');
                            var correctchoices = $(choices).filter(function() {
                                                                     return isChoiceCorrect(this)
                                                                   });
                            console.log(correctchoices.length + " correct choice");
                            var inputtype = (correctchoices.length == 1) ? 'radio' : 'checkbox';
                            var probName = 'q' + questionIdx + idx_suffix;
                             

                            //make question object
                            var questionObj = document.createElement('response');
                            $(questionObj).attr('name', probName);
                            $(questionObj).attr('answertype',nodeName);
                            $(questionObj).attr('data-tag4humans',$(node).attr('tag4humans'));

                            if ($(node).attr('correct-points') != undefined) {
                              $(questionObj).attr('correct-points',$(node).attr('correct-points'));
                            }
                            if ($(node).attr('wrong-points') != undefined) {
                              $(questionObj).attr('wrong-points',$(node).attr('wrong-points'));
                            }
                            $(questionMeta).append($(questionObj));
                              
                            var fieldsetObj = document.createElement('fieldset');
                            $(fieldsetObj).attr('data-tag4humans',$(node).attr('tag4humans'));

                            $(nodeParent).append($(fieldsetObj));
                              
                            $(choices).each(function (idx, el) {
                                           
                                var choiceID = probName + '_' + idx;

                                //make choice object
                                var choiceObj = document.createElement('choice');
                                //$(choiceObj).attr('id',choiceID);
                                $(choiceObj).attr('value',$(this).attr('name'));
                                $(choiceObj).attr('data-tag4humans', $(this).attr('tag4humans'));
                                $(questionObj).append($(choiceObj));
                                var explanationObj = document.createElement('explanation');
                                $(explanationObj).append($(this).find('explanation').text());
                                $(choiceObj).append($(explanationObj));
                                //Add to Answer object
                                if (isChoiceCorrect(this)) {
                                    $(choiceObj).attr('correct','true');
                                } else {
                                    $(choiceObj).attr('correct','false');
                                }
                                        
                                        
                                //Add to preview.
                                var tmpInput = document.createElement('input');
                                var tmpLabel = document.createElement('label');
                                            
                                $(tmpLabel).attr('for', choiceID);
                                $(tmpInput).attr('data-tag4humans', $(this).attr('tag4humans'));
                                $(tmpInput).attr('type', inputtype);
                                $(tmpInput).attr('id', choiceID);

                                $(tmpInput).attr('name', probName);
                                $(tmpInput).attr('value', $(this).attr('name'));
                                $(tmpLabel).append($(tmpInput));
                                $(tmpLabel).append($(this).find('text').text());


                                $(fieldsetObj).append($(tmpLabel));
                            });

                            break;

                        case 'regexresponse':
                        case 'stringresponse':
                        case 'numericalresponse':
                              
                            var probName =  'q' + questionIdx + idx_suffix;
                              
                            if ($(node).attr('answer')) {
                              var questionObj = document.createElement('response');
                              $(questionObj).attr('name', probName);
                              $(questionObj).attr('answertype', nodeName);
                              $(questionObj).attr('answer',$(node).attr('answer'));
                              $(questionObj).attr('data-tag4humans', $(node).attr('tag4humans'));
                              
                              if ($(node).attr('correct-points') != undefined) {
                                  $(questionObj).attr('correct-points',$(node).attr('correct-points'));
                              }
                              if ($(node).attr('wrong-points') != undefined) {
                                  $(questionObj).attr('wrong-points',$(node).attr('wrong-points'));
                              }

                              $(questionObj).append($(node).find('responseparam'));
                              $(questionMeta).append($(questionObj));
                            }
                            
                            var textBoxData = $(node).children();   // only goes down one-level
                    
                            var tmpInput = document.createElement('input');
                            $(tmpInput).attr('type', 'text');
                            $(tmpInput).attr('id', probName);
                            $(tmpInput).attr('name', probName);
                            $(tmpInput).attr('data-tag4humans', $(node).attr('tag4humans'));
                    
                            var textInputSize = (false) ? '' : 20;
                            $(tmpInput).attr('size', textInputSize);
                    
                            $(nodeParent).append($(tmpInput));

                            break;

                        case 'optionresponse':

                            var optionData = $(node).find('optioninput');
                            var optionItemStr = $(optionData).attr('options');
                            var optionItemArr = optionItemStr.split(',');

                            var tmpSelect = document.createElement('select');
                            for (var i = 0; i < optionItemArr.length; i += 1) {
                                var tmpOptionItem = document.createElement('option');
                                $(tmpOptionItem).text(optionItemArr[i]);
                                $(tmpSelect).append($(tmpOptionItem));
                            }

                            $(nodeParent).append($(tmpSelect));

                            break;

                        default:

                            break;

                    } // End Switch
                
                    if ($(nodeParent)[0] != $(tmpProbDiv)[0]) {
                        $(tmpProbDiv).append($(nodeParent));
                    }

                };  //End renderResponseNode

                suffix_idx = -1;

                $(allChildren).each(function () {
                    suffix_idx += 1;
                    var nodeName = $(this)[0].nodeName;
                                    
                    if (nodeName == 'p') {
                        var previewP = document.createElement('p');
                        var thisclone = $(this).clone()[0];
                        $(thisclone).find(c2gXMLParse.specialNodes).remove();
                        previewP=thisclone;
                                    //$(thisclone).html();
                                    //$(previewP).html($(thisclone).html());
                                    //$(previewP).text($(this).text());
                        $(previewP).appendTo($(tmpProbDiv));
                            
                        var responseNodes = $(this).children();
                        if (responseNodes.length > 0) {
                            responseNodes.each(function () {
                                renderResponseNode($(this), previewP, c2gXMLParse.numToID(suffix_idx));
                            });
                        }
                    } else {
                        renderResponseNode($(this), $(tmpProbDiv), c2gXMLParse.numToID(suffix_idx));
                    }
                });  //end $(allChildren)
        
            }); // end each problem
      
            editor.setValue($(targetEl).html());

            metadata_editor.setValue($(outerMetadataObj).html());
                   console.log(outerMetadataObj);
            var dataToTransmit = {};
            //dataToTransmit.xmlContent = $('textarea').val();
            dataToTransmit.xmlContent = $(sourceEl).val();
            //dataToTransmit.htmlContent = $('#staging-area').html();
            dataToTransmit.htmlContent = $(targetEl).html();
            console.log(JSON.stringify(dataToTransmit));
            console.log(questionIdx);
            console.log(answerkeyObj);
            console.log($(answerkeyObj).html());

        } // end renderMarkup()

    } // end c2gXMLParse object

    return c2gXMLParse;
   
})();
