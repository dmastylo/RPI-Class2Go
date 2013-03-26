$(window).load(function() {
    $('#chat-pane #chat-tabs').prepend('<a href="#" onclick="event.preventDefault();" id="chat-expand-arrow"><em class="icon-chevron-right"></em></a>');
    var candyWidth = $('#candy').css('width');
    
    $('#chat-expand-arrow').toggle(function() {
        $('#candy').animate({width: '227px'}, 'slow', function() {
            $('#chat-expand-arrow em').toggleClass('icon-chevron-left').toggleClass('icon-chevron-right');
            $('#chat-pane').toggleClass('collapsed-message-pane');
        });
        $('#chat-pane .roster-pane').animate({top: '0px'}, 'slow');
        $('#chat-rooms .message-pane-wrapper, #chat-rooms .message-form-wrapper, form.message-form').fadeOut('slow');
    }, function() {
        $('#candy').animate({width: candyWidth}, 'slow', function() {
            $('#chat-expand-arrow em').toggleClass('icon-chevron-left').toggleClass('icon-chevron-right');
            $('#chat-pane').toggleClass('collapsed-message-pane');
        });
        $('#chat-pane .roster-pane').animate({top: '30px'}, 'slow');
        $('#chat-rooms .message-pane-wrapper, #chat-rooms .message-form-wrapper, form.message-form').fadeIn('slow');
    });
});