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
                   
        specialNodes: "dbinteractiveresponse,multiplechoiceresponse,numericalresponse,stringresponse,regexresponse,optionresponse,solution",
        
        clearInputs: function(formID) {
            form = $(formID); 
            var inputs = form.find('input'); 
            for(var i = 0; i < inputs.length; i++)
            {
                var input = inputs[i]; 
                if(input.type == 'checkbox')
                {
                    input.checked = false; 
                } else {
                    if(input.getAttribute('default'))
                    {
                        input.value = input.getAttribute('default'); 
                    } else {
                        input.value = "";                         
                    }
                }
            }
            var textareas = form.find('textarea'); 
            for(var i = 0; i < textareas.length; i++)
            {
                var textarea = textareas[i]; 
                if(!textarea.hidden && textarea.value)
                {
                    textarea.value = ""; 
                }
            }
        }, 
        
        assignCorrectIds : function(mDOM, isXML) { 
            if(isXML) { 
                var questionMD = $(mDOM).find('question_metadata');
                if(questionMD) {
                    for(i = 0; i < questionMD.length; i++) { 
                        $(questionMD[i]).attr('id', 'question_' + (i+1));
                    }
                }
            } else { 
                v = 1; 
                allHTML = ""; 
                for(i = 0; i < mDOM.length; i++) { 
                    if(mDOM[i].tagName == "DIV") {
                        $(mDOM[i]).attr('id', 'question_' + v);
                        $(mDOM[i]).attr('number', v);
                        fieldset = $(mDOM[i]).find('fieldset'); 
                        var inputs = $(mDOM[i]).find('input'); 
                        if(inputs)
                        {
                            for(var m = 0; m < inputs.length; m++)
                            {
                                if(fieldset.length > 0) {
                                    $(inputs[m]).attr('name', 'question_' + v);                                     
                                } else {
                                    $(inputs[m]).attr('name', 'question_' + v + '_name' + m);  
                                }
                                $(inputs[m]).attr('id', 'question_' + v + '_name' + m); 
                            } 
                        }

                        v = v+1; 
                        allHTML = allHTML + mDOM[i].outerHTML; 
                    }
                }
                return allHTML;  
            }
            
        },
        
        assignCorrectNames : function(mDOM) {
            var questionMD = $(mDOM).find('question_metadata');
            if(questionMD) {
                for(var i = 0; i < questionMD.length; i++) { 
                    responses = $(questionMD[i]).find('response');
                    if(responses.length > 0 && responses[0].getAttribute('answertype') != 'multiplechoiceresponse') {
                        for(var m = 0; m < responses.length; m++)
                        {
                            responses[m].setAttribute('name', questionMD[i].getAttribute('id') + '_name' + m); 
                        }
                    } else {
                        responses[0].setAttribute('name', questionMD[i].getAttribute('id'));                          
                    }
                } 
            }
        },
        
        createBaseXML: function(mDOM) {
            return $.parseXML('<exam_metadata></exam_metadata>');
        }, 
        
        addRegexResponseQuestion: function(html, xml)
        {
            if(!c2gXMLParse.inputQuestionsValidation("regex-response-question")) {
                return false; 
            }
            editHtml = $(html); 
            var editID = $( "#regex-response-question-edit" )[0].value; 
            
            c2gXMLParse.addHTMLForInputQuestions(editHtml, "regex-response-question", editID); 
            
            mDOM=$.parseXML(metadata_editor.getValue());
            if(!mDOM) {
                mDOM = c2gXMLParse.createBaseXML();
            }
            var exam_metadata = $(mDOM).find('exam_metadata'); 
            exam_metadata = exam_metadata[0];
            questionMeta= $(xml);
            
            //Sub-questions
            for(i = 1; i < 4; i++) {  
                  //Add to the XML if and only if you have text for your question
                  var subquestionText = $('#regex-response-question-text' + i)[0].value; 
                  if(subquestionText) {
                    var response = document.createElement('response'); 
                    response.setAttribute('answertype', 'regexresponse'); 
                    answer = $('#regex-response-question-actual-answer' + i).val(); 
                    response.setAttribute('answer', answer); 
                    var correct = $('#regex-response-question-correct-points' + i).val(); 
                    var wrong = $('#regex-response-question-wrong-points' + i).val();
                    response.setAttribute('correct-points', correct); 
                    response.setAttribute('wrong-points', wrong);
                    var multilineChecked = $('#regex-response-question-multiline' + i)[0].checked; 
                    var ignorecaseChecked = $('#regex-response-question-ignorecase' + i)[0].checked; 
                    if(multilineChecked)
                    {
                        var responseparam = document.createElement('responseparam'); 
                        responseparam.setAttribute('flag', 'MULTILINE'); 
                        response.appendChild(responseparam); 
                    }
                    if(ignorecaseChecked)
                    {
                        var responseparam2 = document.createElement('responseparam'); 
                        responseparam2.setAttribute('flag', 'IGNORECASE'); 
                        response.appendChild(responseparam2); 
                    }
                    questionMeta[0].appendChild(response);                    
                  }       
              }
              
            //Detailed Explanation
            var detailed_explanation = $('#regex-response-question-explanation').val(); 
            var solution = $(questionMeta.find('solution')[0])[0]; 
            var div = $(solution).find('div')[0];
            var textElement = document.createElement('p'); 
            textElement.innerHTML = detailed_explanation; 
            div.appendChild(textElement);
            
            //Add to XML
            if(editID != "") {
                assocXML = $(exam_metadata).find('#' + editID)[0]; 
                assocXML.innerHTML = questionMeta[0].innerHTML; 
            } else {
                $(exam_metadata).append(questionMeta);                  
            }
                        
            //Finish up
            c2gXMLParse.assignCorrectIds(mDOM, true); 
            c2gXMLParse.assignCorrectNames(mDOM); 
              
            metadata_value = (new XMLSerializer()).serializeToString(mDOM);
            metadata_editor.setValue(style_html(metadata_value, {'max_char':80}));
            metadata_editor.onChangeMode(); 

            this.renderPreview();
            return true;
        }, 
        
        addHTMLForInputQuestions: function(baseHTML, baseID, editID) {
            var editor_value = editor.getValue(); 
            
            //Text of Question
            var providedText = $('#' + baseID + '-text').val(); 
            var questionText = $(baseHTML.find('div.question_text')[0]); 
            var questionTextParagraph = $(document.createElement('p')); 
            questionTextParagraph.text(providedText); 
            questionText.empty(); 
            questionText.append(questionTextParagraph);
            
            //Sub-questions
            for(i = 1; i < 4; i++) {  
                  //Add to the HTMl
                var subquestionText = $('#' + baseID + '-text' + i)[0].value; 
                if(subquestionText) {
                    p_element = document.createElement('p'); 
                    var input = document.createElement('input'); 
                    var span = document.createElement('span'); 
                    input.setAttribute('type', 'text'); 
                    input.setAttribute('data-report', subquestionText); 
                    input.setAttribute('size', '20'); 
                    span.innerText = subquestionText; 
                    p_element.appendChild(span); 
                    p_element.appendChild(input); 
                    baseHTML[0].appendChild(p_element); 
                }                
              }
              
            if(editID != "") {
              var container = document.createElement('div');
              container.innerHTML = editor_value;
              var assocHTML = $(container).find('#' + editID)[0]; 
              assocHTML.innerHTML = baseHTML[0].innerHTML; 
              editor_value = container.innerHTML;
            } else {
              editor_value = editor_value + baseHTML[0].outerHTML;                   
            }
                
            //Add HTML 
            var mDOM = $(editor_value); 
            editor_value = c2gXMLParse.assignCorrectIds(mDOM, false); 
            editor.setValue(style_html(editor_value, {'max_char':80}));
            editor.onChangeMode();
        },
        
        inputQuestionsValidation: function(baseID)
        {
            var hasOneSubQuestion = false; 
            for(var i = 1; i < 4; i++)
            {
                var subquestionText = $('#' + baseID + '-text' + i)[0].value; 
                var subquestionActualAnswer = $('#' + baseID + '-actual-answer' + i)[0].value; 
                if(subquestionText && subquestionActualAnswer)
                {
                    hasOneSubQuestion = true; 
                    break; 
                }
            }
            
            if(!hasOneSubQuestion)
            {
                alert("Please include text and an answer value for at least one subquestion."); 
                return false; 
            }
            return true; 
        },
        
        addNumericalResponseQuestion: function(html, xml)
        {
            if(!c2gXMLParse.inputQuestionsValidation("numerical-response-question")) {
                return false; 
            }
            editHtml = $(html); 
            var editID = $( "#numerical-response-question-edit" )[0].value; 
            
            c2gXMLParse.addHTMLForInputQuestions(editHtml, "numerical-response-question", editID); 
            
            mDOM=$.parseXML(metadata_editor.getValue());
            if(!mDOM) {
                mDOM = c2gXMLParse.createBaseXML();
            }
            var exam_metadata = $(mDOM).find('exam_metadata'); 
            exam_metadata = exam_metadata[0];
            questionMeta= $(xml);
            
            //Sub-questions
            for(i = 1; i < 4; i++) {  
                  //Add to the XML
                  var subquestionText = $('#numerical-response-question-text' + i)[0].value; 
                  if(subquestionText) {
                    var response = document.createElement('response'); 
                    response.setAttribute('answertype', 'numericalresponse'); 
                    answer = $('#numerical-response-question-actual-answer' + i).val(); 
                    response.setAttribute('answer', answer); 
                    var correct = $('#numerical-response-question-correct-points' + i).val(); 
                    var wrong = $('#numerical-response-question-wrong-points' + i).val();
                    response.setAttribute('correct-points', correct); 
                    response.setAttribute('wrong-points', wrong);
                    var responseparam = document.createElement('responseparam'); 
                    responseparam.setAttribute('type', 'tolerance'); 
                    var defaulttolerance = $('#numerical-response-question-tolerance-answer' + i).val(); 
                    if(defaulttolerance != "")
                    {
                        defaulttolerance = defaulttolerance;
                    } else {
                        defaulttolerance = '0%'; 
                    }
                    responseparam.setAttribute('default', defaulttolerance); 
                    response.appendChild(responseparam); 
                    questionMeta[0].appendChild(response);                    
                  }       
              }
              
            //Detailed Explanation
            var detailed_explanation = $('#numerical-response-question-explanation').val(); 
            var solution = $(questionMeta.find('solution')[0])[0]; 
            var div = $(solution).find('div')[0];
            var textElement = document.createElement('p'); 
            textElement.innerHTML = detailed_explanation; 
            div.appendChild(textElement);
            
            //Add to XML
            if(editID != "") {
                assocXML = $(exam_metadata).find('#' + editID)[0]; 
                assocXML.innerHTML = questionMeta[0].innerHTML; 
            } else {
                $(exam_metadata).append(questionMeta);                  
            }
                        
            //Finish up
            c2gXMLParse.assignCorrectIds(mDOM, true); 
            c2gXMLParse.assignCorrectNames(mDOM); 
              
            metadata_value = (new XMLSerializer()).serializeToString(mDOM);
            metadata_editor.setValue(style_html(metadata_value, {'max_char':80}));

            this.renderPreview();
            metadata_editor.renderer.updateText(); 
            
            return true;
        }, 
        
        radioButtonValidation: function()
        {
            //This function makes sure that all the required fields are filled out. If there are not, it alerts the user. 
            var providedText = $('#single-choice-entry-question-text').val(); 
            var hasOneAnswerChoice = false; 
            for(var i = 1; i<7; i++)
            {
                var soldisplay = $('#single-choice-entry-answer' + i).val(); 
                var solsubmit = $('#single-choice-entry-value-answer' + i).val();
                if(soldisplay && solsubmit)
                {
                    hasOneAnswerChoice = true; 
                    break;
                }
            }
            if(!providedText)
            {
                alert("Please fill out the text for the question."); 
                return false; 
            } else {
                if(!hasOneAnswerChoice)
                {
                    alert("Please fill out a submit and display value for at least one answer choice.");
                    return false;  
                }
            }
            return true; 
        },
            
        addRadioButtonQuestion: function(html, xml, type) {
            //This function adds a radio button or checkbox question to the XML and HTML editors. 
            //Return value: whether the dialog should be closed. 
              if(!c2gXMLParse.radioButtonValidation()) {
                  return false; 
              }
              if(!type) {
                  type = 0; 
              }
              var editID = $( "#single-choice-entry-edit" )[0].value; 
              var editor_value = editor.getValue(); 
              var editHtml = $(html); 
              
              //Text of question
              var providedText = $('#single-choice-entry-question-text').val(); 
              var questionText = $(editHtml.find('div.question_text')[0]); 
              var questionTextParagraph = $(document.createElement('p')); 
              questionTextParagraph.text(providedText); 
              questionText.empty(); 
              questionText.append(questionTextParagraph); 
              
              var fieldset = $(editHtml.find('fieldset')[0])[0]; 

              //Answer Choices
              for(i = 1; i < 7; i++) {  
                  //Add to the HTMl                             
                sol1display = $('#single-choice-entry-answer' + i).val(); 
                sol1submit = $('#single-choice-entry-value-answer' + i).val(); 
                if(sol1display && sol1submit) {
                    sol1label = document.createElement('label'); 
                    sol1input = document.createElement('input'); 
                    if(type == 0) {
                        sol1input.setAttribute('type', 'radio'); 
                    } else {
                        sol1input.setAttribute('type', 'checkbox'); 
                    }
                    sol1input.setAttribute('value', sol1submit);
                    sol1label.appendChild(sol1input); 
                    sol1displaycontainer = document.createElement('span'); 
                    sol1displaycontainer.innerText = sol1display; 
                    sol1label.appendChild(sol1displaycontainer); 
                    fieldset.appendChild(sol1label); 
                }                
              }
              
              if(editID != "") {
                  var container = document.createElement('div');
                  container.innerHTML = editor_value;
                  var assocHTML = $(container).find('#' + editID)[0]; 
                  assocHTML.innerHTML = editHtml[0].innerHTML; 
                  editor_value = container.innerHTML;
              } else {
                  editor_value = editor_value + editHtml[0].outerHTML;                   
              }
              
              mDOM = $(editor_value); 
              editor_value = c2gXMLParse.assignCorrectIds(mDOM, false); 
              editor.setValue(style_html(editor_value, {'max_char':80}));
              editor.onChangeMode(); 

              radio_button_xml = xml;
              mDOM=$.parseXML(metadata_editor.getValue());
              if(!mDOM) {
                  mDOM = c2gXMLParse.createBaseXML();
              }
              var exam_metadata = $(mDOM).find('exam_metadata'); 
              exam_metadata = exam_metadata[0];
              questionMeta= $(xml);
              response = $(questionMeta.find('response')[0])[0]; 
              
              //Points
              correct_points = $('#single-choice-entry-correct-points')[0]; 
              wrong_points = $('#single-choice-entry-wrong-points')[0];
              response.setAttribute('correct-points', correct_points.value); 
              response.setAttribute('wrong-points', wrong_points.value) 
              
              //Answer Choices
              for(i = 1; i < 7; i++) {  
                  //Add to the XML                             
                sol1display = $('#single-choice-entry-answer' + i).val(); 
                sol1submit = $('#single-choice-entry-value-answer' + i).val(); 
                sol1explanation = $('#single-choice-entry-explanation-answer' + i).val(); 
                sol1correctness = $('#single-choice-entry-correctness-answer' + i)[0].checked; 
                if(sol1display && sol1submit) {
                    sol1choice = document.createElement('choice'); 
                    sol1expl = document.createElement('explanation'); 
                    sol1expl.innerText = sol1explanation; 
                    sol1choice.setAttribute('value', sol1submit);
                    sol1choice.setAttribute('correct', sol1correctness); 
                    sol1choice.setAttribute('data-report', sol1display);
                    sol1choice.appendChild(sol1expl); 
                    response.appendChild(sol1choice); 
                }                
              }
              
              //Detailed Explanation
              detailed_explanation = $('#single-choice-entry-question-explanation').val(); 
              solution = $(questionMeta.find('solution')[0])[0]; 
              div = $(solution).find('div')[0];
              textElement = document.createElement('p'); 
              textElement.innerHTML = detailed_explanation; 
              div.appendChild(textElement); 
              
              if(editID != "") {
                  assocXML = $(exam_metadata).find('#' + editID)[0]; 
                  assocXML.innerHTML = questionMeta[0].innerHTML; 
              } else {
                  $(exam_metadata).append(questionMeta);                  
              }
              c2gXMLParse.assignCorrectIds(mDOM, true); 
              c2gXMLParse.assignCorrectNames(mDOM); 
              
              metadata_value = (new XMLSerializer()).serializeToString(mDOM);
              metadata_editor.setValue(style_html(metadata_value, {'max_char':80}));
              metadata_editor.onChangeMode(); 

              this.renderPreview(); 
              return true; 
          },
              
        renderPreview: function() {
            $('#staging-area').empty();
            $('#staging-area').append(editor.getValue());
            psetQuestions = $('#staging-area div.question');
            if (psetQuestions.length > 0) {
                var qQumx = 1;
                $(psetQuestions).each(function () {
                    c2gXMLParse.addNumberToQuestionDiv(this,qQumx);
                    qQumx = qQumx + 1;}
                );
            }
            var mDOM=$.parseXML(metadata_editor.getValue());
            var questionMD = $(mDOM).find('question_metadata');
            $(questionMD).each(function(){displayQuestionExplanation(this);
                              displayChoiceExplanations(this, true);});
            var container = document.createElement('div');
            container.innerHTML = editor.getValue();
            var mDOMHTML = $(container); 
            questionMD = mDOMHTML.find('div.question'); 
            $(questionMD).each(function(){displayEditQuestion(this);});
            $(questionMD).each(function(){displayDeleteQuestion(this);});
            $(questionMD).each(function(){displayMoveQuestion(this);});
            MathJax.Hub.Queue(["Typeset",MathJax.Hub,"staging-area"]);

        },
                   
        addNumberToQuestionDiv: function(elem, num) {
            numberingDiv = $(elem).find('h3.questionNumber');
            if (numberingDiv.length == 0){
                $(elem).prepend('<h3 class="questionNumber">Question ' + num +'</h3>');
            } else { 
                h3Tag = $(numberingDiv[0]); 
                parentDiv = h3Tag.parent(); 
                if(parentDiv.attr('number')) {
                    h3Tag.text("Question " + parentDiv.attr('number'));                     
                } else { 
                    h3Tag.text("Question " + num); 
                }
            }
        },
                   
        copyContentsToEl: function(fromEl, toEl) {
            $(fromEl).contents().each(function() {
                //nodeName according to DOM spec:  http://www.w3.org/TR/REC-DOM-Level-1/level-one-core.html
                if (this.nodeName=="#cdata-section" || this.nodeName=="#text") {
                    $(toEl).append($(this).text());
                }
                else { //for DOM nodes that are elements
                    $(toEl).append($(this).clone());
                }
            });
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
                alert('Your XML has invalid syntax.  You should be able to resolve this by copy-and-pasting your XML into a validator such as http://www.w3schools.com/xml/xml_validator.asp ');
                console.log(e.message);
                return;
            }
             
            var setValIfDef = function (elem, val) {
                if (typeof val !== "undefined")
                   $(elem).val(val);
            };
                
            //This parses the "metadata" for the problem set.  title, description, etc.
            var parsePsetFields = function() {
                var psetDOM = $(myDOM).find('problemset');
                 
                if (psetDOM.length) {
                   if ($(psetDOM).attr('invideo') != undefined) {
                       $('input#invideo_id')[0].checked=true;
                   } else {
                       $('input#invideo_id')[0].checked=false;
                   }
                   
                   setValIfDef($('input#exam_title'), $(psetDOM).attr('title'));
                   setValIfDef($('input#exam_slug'), $(psetDOM).attr('url-identifier'));
                   setValIfDef($('select#assessment_type'), $(psetDOM).attr('type'));
                   
                   var descDOM = $(psetDOM).find('description');
                   var datesDOM = $(psetDOM).find('dates');
                   var gradingDOM = $(psetDOM).find('grading');
                   var sectionDOM = $(psetDOM).find('section');
                   
                   if (descDOM.length) {
                       $('textarea#description').val($(descDOM).text());
                   }
                   
                   if (datesDOM.length) {
                       setValIfDef($('input#due_date'), $(datesDOM).attr('due-date'));
                       setValIfDef($('input#grace_period'), $(datesDOM).attr('grace-period'));
                       setValIfDef($('input#hard_deadline'), $(datesDOM).attr('hard-deadline'));
                   }
                   
                   if (gradingDOM.length) {
                       setValIfDef($('input#late_penalty'), $(gradingDOM).attr('late-penalty'));
                       setValIfDef($('input#daily_late_penalty'), $(gradingDOM).attr('daily-late-penalty'));
                       setValIfDef($('input#num_subs_permitted'), $(gradingDOM).attr('num-submissions'));
                       setValIfDef($('input#resubmission_penalty'), $(gradingDOM).attr('resubmission-penalty'));
    
                   }
                   if (sectionDOM.length) {
                       $('select#id_section option').each(function() {
                          //Go through each option to see if any of their text is the same as the XML
                          //select if that's the case
                           if ($(this).text() && $(sectionDOM).attr('section') &&  $(this).text().trim() == $(sectionDOM).attr('section').trim()) {
                              setValIfDef($('select#id_section'), $(this).val());
                              prefill_children().success(prepop_children);
                           }
                       });

                   }
                }
            };
                   
            var prepop_children = function () {
                var psetDOM = $(myDOM).find('problemset');
                if (psetDOM.length) {
                    var sectionDOM = $(psetDOM).find('section');
                    if (sectionDOM.length) {
                        $('select#parent_id option').each(function() {
                              //Go through each option to see if any of their text is the same as the XML
                              //select if that's the case
                              if ($(this).text() && $(sectionDOM).attr('parent') && $(this).text().trim() == $(sectionDOM).attr('parent').trim())
                                    setValIfDef($('select#parent_id'), $(this).val());
                        });
                    }
                }
            };
                   
            parsePsetFields();

            var problemNodes = $(myDOM).find('problem');

            var videoNodes = $(myDOM).find('video');

            //Helper function
            var isChoiceCorrect = function(choiceElem) {
                if (!$(choiceElem).attr('correct')) {
                    return false;
                }
                return $(choiceElem).attr('correct').toLowerCase()==='true';
            }
            var psetDOM = $(myDOM).find('problemset');

            var questionIdx = 0;
            var ordinalNumbers = true;
            if (psetDOM.length && $(psetDOM).attr('do-not-autonumber') != undefined) {
                ordinalNumbers = false;
            }
            if (problemNodes.length <= 1) { //special case if only 1 problem
                ordinalNumbers = false;
            }
                   
            var outerMetadataObj = document.createElement('metadata'); //outermost metadata--won't actually be displayed since we use $.html()
            var metadataObj = document.createElement('exam_metadata');
            $(outerMetadataObj).append($(metadataObj));
            
            // Add video metadata (problem:time mappings for in-video exams)
            $(metadataObj).append($(videoNodes));

            // Add preamble nodes
            $(myDOM).find('preamble').each(function(){
                var preambleDiv = document.createElement('div');
                $(preambleDiv).addClass("preamble");
                $(preambleDiv).attr('id','problemSetPreamble');
                c2gXMLParse.copyContentsToEl($(this),$(preambleDiv));
                $(targetEl).append($(preambleDiv));
            });
                   
            //Build up a DOM object corresponding to the answer key
            var answerkeyObj = document.createElement('answerkey');
            problemNodes.each(function () {

                questionIdx += 1;
                var questionMeta=document.createElement('question_metadata');
                var question_id = "";
                if ($(this).attr('id') != undefined) {
                    question_id = $(this).attr('id');
                }
                else {
                    question_id = 'problem_'+questionIdx;
                }
                $(questionMeta).attr('id', question_id);
                $(questionMeta).attr('data-report', $(this).attr('data-report'));
                $(metadataObj).append($(questionMeta));
                
                              
                            
                //Grab question level solutions
                $(this).find('solution').each(function() {
                    $(questionMeta).append($(this));
                });
                              
                var tmpProbDiv = document.createElement('div');
                $(tmpProbDiv).addClass('question');
                $(tmpProbDiv).attr('id', question_id);
                $(tmpProbDiv).attr('data-report', $(this).attr('data-report'));
                if (ordinalNumbers) {
                    $(tmpProbDiv).prepend('<h3 class="questionNumber">Question ' + questionIdx +'</h3>');
                } else {
                    $(tmpProbDiv).prepend('<h3 class="questionNumber"></h3>');
                }
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
                            var inputtype = (correctchoices.length == 1) ? 'radio' : 'checkbox';
                            var probName = 'q' + questionIdx + idx_suffix;
                             

                            //make question object
                            var questionObj = document.createElement('response');
                            $(questionObj).attr('name', probName);
                            $(questionObj).attr('answertype',nodeName);
                            $(questionObj).attr('data-report',$(node).attr('data-report'));

                            if ($(node).attr('correct-points') != undefined) {
                              $(questionObj).attr('correct-points',$(node).attr('correct-points'));
                            }
                            if ($(node).attr('wrong-points') != undefined) {
                              $(questionObj).attr('wrong-points',$(node).attr('wrong-points'));
                            }
                            $(questionMeta).append($(questionObj));
                              
                            var fieldsetObj = document.createElement('fieldset');
                            $(fieldsetObj).attr('data-report',$(node).attr('data-report'));

                            $(nodeParent).append($(fieldsetObj));
                              
                            $(choices).each(function (idx, el) {
                                           
                                var choiceID = probName + '_' + idx;

                                //make choice object
                                var choiceObj = document.createElement('choice');
                                //$(choiceObj).attr('id',choiceID);
                                $(choiceObj).attr('value',$(this).attr('name'));
                                $(choiceObj).attr('data-report', $(this).attr('data-report'));
                                $(questionObj).append($(choiceObj));
                                $(this).find('explanation').each(function(){
                                                                   $(choiceObj).append($(this).clone());
                                                                });
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
                                $(tmpInput).attr('data-report', $(this).attr('data-report'));
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
                              $(questionObj).attr('data-report', $(node).attr('data-report'));
                              
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
                            $(tmpInput).attr('data-report', $(node).attr('data-report'));
                    
                            var textInputSize = (false) ? '' : 20;
                            $(tmpInput).attr('size', textInputSize);
                    
                            $(nodeParent).append($(tmpInput));

                            break;
                              
                        case 'dbinteractiveresponse':
                              
                              var probName =  'q' + questionIdx + idx_suffix;
                              
                              var questionObj = document.createElement('response');
                              $(questionObj).attr('name', probName);
                              $(questionObj).attr('answertype', nodeName);
                              $(questionObj).attr('answer',$(node).attr('answer'));
                              $(questionObj).attr('data-report', $(node).attr('data-report'));
                              
                              $(node).children().each(function(){ //copy over all children
                                                      $(questionObj).append($(this).clone());
                                                      });
                              $(questionMeta).append($(questionObj));
                              
                              var answerTextNode = $(node).find('answer-text');
                              var placeholderText = "Enter your query here...";
                              if ($(answerTextNode).length) {
                                  placeholderText = $(answerTextNode).text();
                              }
                              var tmpInput = document.createElement('textarea');
                              $(tmpInput).attr('id', probName);
                              $(tmpInput).attr('name', probName);
                              $(tmpInput).attr('placeholder', placeholderText);
                              $(tmpInput).attr('data-report', $(node).attr('data-report'));
                            
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
      
            // Add 'postamble' nodes
            $(myDOM).find('postamble').each(function(){
                var postambleDiv = document.createElement('div');
                $(postambleDiv).addClass("postamble");
                $(postambleDiv).attr('id','problemSetPostamble');
                c2gXMLParse.copyContentsToEl($(this),$(postambleDiv));
                $(targetEl).append($(postambleDiv));
            });
                   
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
