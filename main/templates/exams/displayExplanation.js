{% load i18n %}
{% trans "Show Explanation" as show_explanation_trans %}
{% trans "Hide Explanation" as hide_explanation_trans %}

window.displayQuestionExplanation = function(questionMD){
    //This function takes a DOM object of the metadata and displays the question explanation after the
    //question with the corresponding id
    var mySolution = $(questionMD).find('solution');
    var assocQID = $(questionMD).attr('id');
    var explArea = $('#' + assocQID + '-expl');
    if (explArea.length == 0) {
        explArea = document.createElement('div');
        $(explArea).attr('id', assocQID + '-expl');
        $(explArea).addClass('explanation');
    }
    $(explArea).empty();
    if ($('#' + assocQID + ' .toggle-explanation').length == 0) {
        var toggleExplBtn = document.createElement('input');
        $(toggleExplBtn).attr('type','button');
        //$(toggleExplBtn).attr('id','toggleExplanation_' + idx);
        $(toggleExplBtn).addClass('btn').addClass('toggle-explanation');
        $(toggleExplBtn).attr('data-status', 'Show');
        $(toggleExplBtn).attr('value', '{{ show_explanation_trans }}');
        $(toggleExplBtn).click(toggleExplanation);
    }
    $(explArea).hide();
    $('#' + assocQID + ' .toggle-explanation').attr('data-status', 'Show');
    $('#' + assocQID + ' .toggle-explanation').val('{{ show_explanation_trans }}');
    //$(explArea).append("<h4>Explanation</h4>");
    $(mySolution).contents().each(function(){
        //nodeName according to DOM spec:  http://www.w3.org/TR/REC-DOM-Level-1/level-one-core.html
        if (this.nodeName=="#cdata-section" || this.nodeName=="#text") {
            $(explArea).append($(this).text());
        }
        else { //for DOM nodes that are elements
            $(explArea).append($(this).clone());
        }
    });
    $('div.question#' + assocQID ).append($(explArea));
    $(explArea).before('<div class="clearing-div"></div>').before($(toggleExplBtn));
};

window.displayChoiceExplanations = function(questionMD, showAll) {
    
    if (typeof showAll == "undefined" || showAll == "") {
        showAll = false;
    }
    
    //This function takes a DOM object of the metadata and displays the choice explanations
    //for question with the corresponding id, if that question is multiple choice
    
    var createInlineExp = function (targetEl) {
        var tmpInlineExpl = document.createElement('span');
        $(tmpInlineExpl).addClass('inline-explanation');
        $(tmpInlineExpl).attr('id', $(targetEl).find('input:first').attr('id') + '-expl');
        $(targetEl).append($(tmpInlineExpl));
        
        return $(tmpInlineExpl);
    };
    
    var responses = $(questionMD).find('response');
    responses.each(function () {
        var responseType = $(this).attr('answertype');
        if (responseType == "multiplechoiceresponse") {
            var choices = $(this).find('choice');
            var response = this;
            choices.each(function () {
                var choiceInput = $('input[name|="' + $(response).attr('name') + '"]')
                                  .filter('input[value|="' + $(this).attr('value') + '"]');
                if (showAll || choiceInput.attr('checked')){
                    var choiceLabel = $(choiceInput).closest('label');
                    //console.log(choiceLabel.length);
                    //console.log($(choiceLabel).find('.inline-explanation').length);
                    var inlineExpl = $(choiceLabel).find('.inline-explanation');
                    if (inlineExpl.length == 0) {
                        inlineExpl = createInlineExp($(choiceLabel));
                    }
                    //console.log(inlineExpl);
                    if ($(this).attr('correct') && $(this).attr('correct') == 'true') {
                        $(inlineExpl).addClass('correct');
                    }
                    $(inlineExpl).empty();
                    $(inlineExpl).append($(this).find('explanation').text());
                }
            });
        }
    });
};

// Need toggleExplanation in single question format and when summative exams are submitted
// i.e. submission summary/record page needs to have toggle-able explanation
window.toggleExplanation = function () {
    var assocQ = $(this).closest('.question');
    
    $(assocQ).find('.explanation').toggle();
    
    if ($(this).attr('data-status') == 'Show' && $(assocQ).find('.explanation').css('display') == 'block') {
        $(this).attr('data-status', 'Hide');
        $(this).val('{{ hide_explanation_trans }}');
    } else {
        $(this).attr('data-status', 'Show');
        $(this).val('{{ show_explanation_trans }}');
    }
    
};