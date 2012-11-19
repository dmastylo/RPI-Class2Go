var c2gXMLParse = (function() {
   
    var c2gXMLParse = {
       
    renderHTML: function(xmlSourceEl, htmlOutputEl) {
        $(htmlOutputEl).empty();

        try {
            var myDOM = $.parseXML(xmlSourceEl.val());
        } catch (e) {
            alert('Your XML is invalid');
            console.log(e.message);
            return;
        
    },

    renderPreview: function(inputType) {
    
        if (inputType.toLowerCase() == "xml") {
            editor.setValue('');
            // Set up XML DOM
            var sourceXML = $('#xml-entry'); 
            try {
                var myDOM = $.parseXML(sourceXML);
            } catch (e) {
                alert('Your XML is invalid');
                console.log(e.message);
                return;
            }
        } else {
            $('#staging-area').empty();

            // Set up XML DOM
            var sourceXML = editor.getValue();
            try {
                var myDOM = $.parseXML(sourceXML);
            } catch (e) {
                alert('Your XML is invalid');
                console.log(e.message);
                return;
            }
        }

        var problemNodes = $(myDOM).find('problem');

        problemNodes.each(function () {

            questionIdx += 1;

            var tmpProbDiv = document.createElement('div');
            $(tmpProbDiv).addClass('question');
            
            $('#staging-area').append($(tmpProbDiv));
            
            var allChildren = $(this).children();
            
            var renderResponseNode = function (node, arg2, idx_suffix) {
            
                var nodeName = $(node)[0].nodeName;
                var nodeParent = arguments[1] || $(tmpProbDiv);
                
                switch (nodeName) {
                    case 'multiplechoiceresponse':

                        var choices = $($(node)).find('choice');
                        var correctchoices = $(choices).filter(function() {
                                                                  if (!$(this).attr('correct'))
                                                                     return false;
                                                                  return $(this).attr('correct').toLowerCase()==='true';
                                                               });
                        console.log(correctchoices.length + " correct choice");
                        var inputtype = (correctchoices.length == 1)?'radio':'checkbox';
                
                        $(choices).each(function (idx, el) {
                            var tmpInput = document.createElement('input');
                            var tmpLabel = document.createElement('label');
                            $(tmpLabel).attr('for', 'q' + questionIdx + '_' + idx);
                                
                            $(tmpInput).attr('type', inputtype);
                            $(tmpInput).attr('id', 'q' + questionIdx + '_' + idx);
                            $(tmpInput).attr('name', 'q' + questionIdx);
                            $(tmpInput).attr('value', $(this).attr('name'));
                                
                            $(tmpLabel).text($(this).text());
                            
                            $(nodeParent).append($(tmpLabel));
                            $(tmpLabel).append($(tmpInput));
                        });

                        break;

                    case 'stringresponse':
                    case 'numericalresponse':
                        
                        var textBoxData = $(node).children();   // only goes down one-level
                
                        var tmpInput = document.createElement('input');
                        $(tmpInput).attr('type', 'text');
                        $(tmpInput).attr('id', 'q' + questionIdx + idx_suffix);
                        $(tmpInput).attr('name', 'q' + questionIdx + idx_suffix);
                
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

                  }
                
                if ($(nodeParent)[0] != $(tmpProbDiv)[0]) {
                    $(tmpProbDiv).append($(nodeParent));
                }

            };

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
            });
                        
        }); // end each problem
      
        var dataToTransmit = {};
        dataToTransmit.xmlContent = $('textarea').val();
        dataToTransmit.htmlContent = $('#staging-area').html();
        console.log(JSON.stringify(dataToTransmit));
      } // end renderpreview()
    } // end c2gXMLParse object

    return c2gXMLParse;
   
})();
