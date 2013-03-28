$(window).load(function() {
    var isInIframe = (window.location != window.parent.location) ? true : false;
    
    if (isInIframe) {
        $('#chat-pane #chat-tabs').prepend('<a href="#" id="chat-expand-arrow"><em class="icon-chevron-right"></em></a>');
    }
    
    var collapseMessageForm = function() {
        $('#candy').animate({width: '227px'}, 'slow', function() {
            $('#chat-expand-arrow em').toggleClass('icon-chevron-left').toggleClass('icon-chevron-right');
            $('#chat-pane').toggleClass('collapsed-message-pane');
        });
        $('#chat-pane .roster-pane').animate({top: '0px'}, 'slow');
        $('#chat-rooms .message-pane-wrapper, #chat-rooms .message-form-wrapper, form.message-form').fadeOut('slow');
    }
    
    var expandMessageForm = function() {
        $('#chat-pane').toggleClass('collapsed-message-pane');
        $('#candy').animate({width: '100%'}, 'slow', function() {
            $('#chat-expand-arrow em').toggleClass('icon-chevron-left').toggleClass('icon-chevron-right');
        });
        $('#chat-pane .roster-pane').animate({top: '30px'}, 'slow');
        $('#chat-rooms .message-pane-wrapper, #chat-rooms .message-form-wrapper, form.message-form').fadeIn('slow');
    }

    $('#chat-expand-arrow').toggle(function() {
        collapseMessageForm();
    }, function() {
        expandMessageForm();
    });
});