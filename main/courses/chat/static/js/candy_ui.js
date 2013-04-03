$(window).load(function() {
    var isInIframe = (window.location != window.parent.location) ? true : false;
    
    if (isInIframe) {
        $('#chat-pane #chat-tabs').prepend('<div id="chat-expand-arrow"><em class="icon-chevron-right"></em></div>');
    } else {
        $('#candy').addClass('poppedOut').append('<a href="#" onclick="event.preventDefault();" title="Pop-In Chat Window" class="icon-signin" id="chatPopin"></a>');
    }
    
    var collapseMessageForm = function() {
        $('#candy').animate({width: '227px'}, 'slow', function() {
            $('#chat-expand-arrow em').toggleClass('icon-chevron-left').toggleClass('icon-chevron-right');
            $('#chat-pane').toggleClass('collapsed-message-pane');
            $('#chat-tabs li').removeClass('active');
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

    $('#chat-expand-arrow').click(function() {
        if ($('#chat-pane').hasClass('collapsed-message-pane')) {
            expandMessageForm();
            $('#chat-tabs li:first').addClass('active');
        } else {
            collapseMessageForm();
        }
    });
    
    $('#chat-tabs').click(function() {
        if ($('#chat-pane').hasClass('collapsed-message-pane')) {
            expandMessageForm();
        }
    });
    
    $('#chatPopin').click(function() {
       window.close(); 
    });
});