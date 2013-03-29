window.displayDeleteQuestion = function(questionMD){
    //This function takes a DOM object of the metadata and displays the delete after the
    //question with the corresponding id
    var mySolution = $(questionMD).find('solution');
    var assocQID = $(questionMD).attr('id');
    var toggleExplBtn = document.createElement('input');
    $(toggleExplBtn).attr('type','button');
    $(toggleExplBtn).addClass('btn').addClass('delete-button'); 
    $(toggleExplBtn).attr('data-status', 'Show');
    $(toggleExplBtn).attr('value', 'Delete');
    $(toggleExplBtn).click(function() { askDelete(questionMD); });
    $('div.question#' + assocQID ).append($(toggleExplBtn));
};

window.askDelete = function(questionMD) {
    //This function pops up a confirmation for the delete and calls the actual delete function on success. 
    var confirmDelete = confirm('Are you sure you want to delete this question?'); 
    if(confirmDelete)
    {
        window.delete(questionMD); 
    }
}

window.delete = function(questionMD) { 
    //This function finds the XML and HTML representing the question and removes it. 
    var assocQID = $(questionMD).attr('id'); 
    //Find HTML 
    var editor_value = editor.getValue(); 
    var container = document.createElement('div');
    container.innerHTML = editor_value; 
    var assocHTML = $(container).find('#' + assocQID)[0]; 
    if(assocHTML) {
        assocHTML.remove();         
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
        assocXML.remove();         
    }
    c2gXMLParse.assignCorrectIds(mDOM, true); 
    c2gXMLParse.assignCorrectNames(mDOM);
    metadata_value = (new XMLSerializer()).serializeToString(mDOM);
    metadata_editor.setValue(style_html(metadata_value, {'max_char':80}));
    metadata_editor.onChangeMode(); 

    c2gXMLParse.renderPreview(); 
}