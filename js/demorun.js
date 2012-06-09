/***
 * @requires c2gSections.js
 */

var updateVideoContent = function (event) {

    event.preventDefault();
    var thisLink = event.currentTarget;

    $('#importer').attr('src', $(thisLink).attr('href'));

    $('.video-title').text(': ' + $(thisLink).text());

};

// Page load
$(function() {

    if (sections) {

        $('#import-container').prepend('<div id="toc"></div>');
        $('#toc').append('<h4>Syllabus</h4><div class="scrollable"></div>');

        for (var s = 0; s < sections.length; s += 1) {
            $('#toc').find('div.scrollable').append('<h5 class="collapsed head"><span></span>' + sections[s]["heading"] + '</h5><ul id="list-' + s + '" class="toc-list"></ul>');
            var secMembers = sections[s]["members"];
            for (var m = 0; m < secMembers.length; m += 1) {
                $('#list-' + s).append('<li><a href="' + secMembers[m]["contentUrl"] + '" id="wk0_' + s + '_' + m + '" class="' + secMembers[m]["type"] + '">' + secMembers[m]["title"] + '</a></li>');
            }
        }

        $('.toc-list').children('li').mouseover(function () {$(this).addClass('hover');});
        $('.toc-list').children('li').mouseout(function () {$(this).removeClass('hover');});
        $('.toc-list').children('li').click(function () {
            $('.toc-list').children('li.watching').removeClass('watching');
            $(this).addClass('watching');
        });    

        $('h5.head').click(function () {
            if ($(this).hasClass('collapsed')) {
                $(this).removeClass('collapsed').addClass('expanded');
            } else {
                $(this).removeClass('expanded').addClass('collapsed');
            }
            $(this).next().toggle();
            return false;
        }).next().hide();
        $('h5.head').first().click();

        $('#toc').append('<div class="addendum"><h4>Offline Versions</h4></div>');
        $('div.addendum').append('<ul id="offline-downloads"></ul>');
        $('#offline-downloads').hide();
        for (var s = 0; s < sections.length; s += 1) {
            $('#toc').find('div.addendum').children('ul').append('<li><a href="">' + sections[s]["heading"] + '</a></li>');
        }
        $('div.addendum').click(function () { $('#offline-downloads').toggle(); });
        $('#offline-downloads').find('a').click(
            function (event) {
                event.preventDefault();
                alert('Placeholder for download of ' + $(this).text());
            }
        );

        $('.header-text').append('<span class="video-title">: Course Introduction</span>');
        window.setTimeout(function() {$('#toc').show('slide', {direction:'right'}); }, 2000);
        
    } else {
        alert("Sections structure missing");
    }

});

$(document).ready(function () {
    $('#importer').attr('src', 'http://class2go.stanford.edu/NLP/week1/Course-Introduction/');
    $('#toc').find('a').click(updateVideoContent);
});
