var c2gXMLParse = (function() {
   
    var c2gXMLParse = {
       
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
                   
            //Build up a DOM object corresponding to the answer key
            var answerkeyObj = document.createElement('answerkey');

            problemNodes.each(function () {

                questionIdx += 1;

                var tmpProbDiv = document.createElement('div');
                $(tmpProbDiv).addClass('question');
                
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
                            var probName = 'q' + questionIdx;
                             
                            //make answer object
                            var answerObj = document.createElement('answer');
                            $(answerObj).attr('name', probName);
                            $(answerObj).attr('answertype',nodeName);
                            $(answerkeyObj).append($(answerObj));

                            $(choices).each(function (idx, el) {
                                
                                var choiceID = 'q' + questionIdx + '_' + idx;
                                
                                //Add to Answer object
                                if (isChoiceCorrect(this)) {
                                    var correctObj = document.createElement('correct');
                                    $(correctObj).text(choiceID);
                                    $(answerObj).append($(correctObj));
                                }
                                        
                                //Add to preview.
                                var tmpInput = document.createElement('input');
                                var tmpLabel = document.createElement('label');
                                $(tmpLabel).attr('for', choiceID);
                                    
                                $(tmpInput).attr('type', inputtype);
                                $(tmpInput).attr('id', choiceID);

                                $(tmpInput).attr('name', probName);
                                $(tmpInput).attr('value', $(this).attr('name'));
                                    
                                $(tmpLabel).text($(this).text());
                                
                                $(nodeParent).append($(tmpLabel));
                                $(tmpLabel).append($(tmpInput));
                            });

                            break;

                        case 'stringresponse':
                        case 'numericalresponse':
                              
                            var probName =  'q' + questionIdx + idx_suffix;
                              
                            if ($(node).attr('answer')) {
                              var answerObj = document.createElement('answer');
                              $(answerObj).attr('name', probName);
                              $(answerObj).attr('ansewrtype', nodeName);
                              $(answerObj).text($(node).attr('answer'));
                              $(answerkeyObj).append($(answerObj));
                            }
                            
                            var textBoxData = $(node).children();   // only goes down one-level
                    
                            var tmpInput = document.createElement('input');
                            $(tmpInput).attr('type', 'text');
                            $(tmpInput).attr('id', probName);
                            $(tmpInput).attr('name', probName);
                    
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

                suffix_idx = 64

                $(allChildren).each(function () {
                    suffix_idx += 1;
                    var nodeName = $(this)[0].nodeName;
                                    
                    if (nodeName == 'p') {
                        var previewP = document.createElement('p');
                        $(previewP).text($(this).text());
                        $(previewP).appendTo($(tmpProbDiv));
                            
                        var responseNodes = $(this).children();
                        if (responseNodes.length > 0) {
                            responseNodes.each(function () {
                                renderResponseNode($(this), previewP, String.fromCharCode(suffix_idx));
                            });
                        }
                    } else {
                        renderResponseNode($(this), $(tmpProbDiv), String.fromCharCode(suffix_idx));
                    }
                });  //end $(allChildren)
        
            }); // end each problem
      
            editor.setValue($(targetEl).html());

            var dataToTransmit = {};
            //dataToTransmit.xmlContent = $('textarea').val();
            dataToTransmit.xmlContent = $(sourceEl).val();
            //dataToTransmit.htmlContent = $('#staging-area').html();
            dataToTransmit.htmlContent = $(targetEl).html();
            console.log(JSON.stringify(dataToTransmit));
            console.log(questionIdx);
            console.log(answerkeyObj);

        } // end renderMarkup()

    } // end c2gXMLParse object

    return c2gXMLParse;
   
})();
