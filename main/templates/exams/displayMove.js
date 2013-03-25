window.displayMoveQuestion = function(questionMD){
    var mySolution = $(questionMD).find('solution');
    var assocQID = $(questionMD).attr('id');
    var div = $('div.question#' + assocQID ); 
    var questionNumber = div.find('.questionNumber')
    var upMove = document.createElement('em');
    $(upMove).attr('type','button');
    $(upMove).addClass('btn').addClass('icon-arrow-up').addClass('move-button'); 
    $(upMove).attr('data-status', 'Show');
    $(upMove).attr('value', 'Up');
    $(upMove).click(function() { move(questionMD, true); });
    if((assocQID != 'question_1') && (assocQID != 'problem_1'))
    {
        questionNumber.append(upMove); 
    }
    var downMove = document.createElement('em');
    $(downMove).attr('type','button');
    $(downMove).addClass('btn').addClass('icon-arrow-down').addClass('move-button'); 
    $(downMove).attr('data-status', 'Show');
    $(downMove).attr('value', 'Up');
    $(downMove).click(function() { move(questionMD, false); });
    var container = document.createElement('div');
    container.innerHTML = editor.getValue();
    var mDOMHTML = $(container); 
    var numberOfQuestions = mDOMHTML.find('div.question').length; 
    if((assocQID != ('question_' + numberOfQuestions)) && (assocQID != ('problem_' + numberOfQuestions))) {
        questionNumber.append($(downMove));        
    }
}

window.move = function(questionMD, movingUp) { 
    //This function finds the XML and HTML representing the question and removes it. 
    var assocQID = $(questionMD).attr('id'); 
    //Find HTML 
    var editor_value = editor.getValue(); 
    var container = document.createElement('div');
    container.innerHTML = editor_value; 
    var assocHTML = $(container).find('#' + assocQID)[0]; 
    if(assocHTML)
    {
        var referencePointHTML = $(assocHTML).prev();  
        var referencePointHTMLNext = $(assocHTML).next()               
        assocHTML.remove();
        if(movingUp) {
            $(referencePointHTML).before(assocHTML);  
        } else {
            if(referencePointHTMLNext) { 
                $(referencePointHTMLNext).after(assocHTML);  
            } else { 
                $(container).append(assocHTML); 
            }
        }
    }
    
    var mDOM = $(container.innerHTML);
    editor_value = c2gXMLParse.assignCorrectIds(mDOM, false); 
    editor.setValue(style_html(editor_value, {'max_char':80}));
    editor.onChangeMode();
    
    //Find XML 
    mDOM=$.parseXML(metadata_editor.getValue());
    var assocXML = $(mDOM).find('#' + assocQID)[0]; 
    if(assocXML)
    {
        var referencePointXML = $(assocXML).prev(); 
        var referencePointXMLNext = $(assocXML).next()        
        assocXML.remove();
        if(movingUp) {
            $(referencePointXML).before(assocXML);  
        } else {
            if(referencePointXMLNext) { 
                $(referencePointXMLNext).after(assocXML);  
            } else { 
                $(mDOM).append(assocXML); 
            }
        }   
    }
    c2gXMLParse.assignCorrectIds(mDOM, true); 
    c2gXMLParse.assignCorrectNames(mDOM);
    metadata_value = (new XMLSerializer()).serializeToString(mDOM);
    metadata_editor.setValue(style_html(metadata_value, {'max_char':80}));
    metadata_editor.onChangeMode(); 

    c2gXMLParse.renderPreview(); 
}