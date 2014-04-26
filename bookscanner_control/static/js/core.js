/*****************************************************************************/

var SEL = {'left':null,
                'right': null};

/*****************************************************************************/

var display_image = function(elem, src) {
    $(elem).empty().append(
        window.image_pair_tmpl({'src': src}));
};

/*****************************************************************************
* Renders single pair of pages
*****************************************************************************/

var display_pair = function(dirname, left, right) {
    display_image('.image-left', dirname + left);
    display_image('.image-right', dirname + right);
    $('.page-img').anythingZoomer();
    $('.pages-pair').removeClass('selected');
    var pair_content = window.pages_pair_tmpl({
        'dirname': dirname,
        'left': left,
        'right': right
    });
    $('.pages').append(pair_content);
    $('.pages-pair').click(function() {
        $('.pages-pair').removeClass('selected');
        $(this).addClass('selected');
        $('.image-left').empty();
        $('.image-right').empty();
        var l = $(this).find('.left');
        var full_left_filename = dirname + l.text();
        if (l.length) {
            display_image('.image-left', full_left_filename);
        };
        var r = $(this).find('.right');
        var full_right_filename = dirname + r.text();
        if (r.length) {
            display_image('.image-right', full_right_filename);
        };
        SEL.left = full_left_filename;
        SEL.right = full_right_filename;
    });
};

/*****************************************************************************
* Sends req to server and refreshes the client
* num: number of pairs of pages to fetch; 0 - all pages
*****************************************************************************/

var refresh = function(num) {
    $('.pages').empty();
    $('.image-left').empty();
    $('.image-right').empty();
    SEL.left = null;
    SEL.right = null;
    $.getJSON('stat', {num:num}).done(function(data) {
        if (data.files.length) {
            for(var i=0;i<data.files.length;i++) {
                display_pair(
                    data.dirname, data.files[i][0], data.files[i][1])
                SEL.left = data.dirname + data.files[i][0];
                SEL.right = data.dirname + data.files[i][1];
            };
        };
    });
};

/*****************************************************************************/

$(document).ready(function () {
    window.pages_pair_tmpl = _.template($('#pages-pair-tmpl').text().trim());
    window.image_pair_tmpl = _.template($('#image-pair-tmpl').text().trim());
    refresh(0);
    $('.refresh').click(function() {
        refresh(0);
    });
    /* remove just the last pair */
    $('.remove').click(function() {
        if (confirm('Remove selected pages?')) {
          $.getJSON('del', {left:SEL.left, right:SEL.right}).done(
            function(data) {
                refresh(0);
            });
        };
    });
    /* remove all pages */
    $('.trash').click(function() {
        if (confirm('Remove all pages?')) {
          $.getJSON('del', {left:'', right:''}).done(
            function(data) {
                refresh(0);
            });
        };
    });
    /* capture and insert at specific position */
    $('.insert').click(function() {
        $.getJSON('ins', {left:SEL.left, right:SEL.right}).done(
            function(data) {
                refresh(0);
        });
    });
    /* switch left and right page */
    $('.switch').click(function() {
        if (confirm('Switch pages?')) {
            $.getJSON('conf', {action:'switch'}).done(
            function(data) {
                refresh(0);
            });
        };
    });
    /* change book name */
    $('#bookname').keydown(function(e) {
        if ( e.which == 13 ) {
            $.getJSON('conf', {action:'bookname', name:$(this).val()}).done(
                function(data) {
                    refresh(0);
            });
        };
    });
    /* upload to remote server */
    $('.upload').click(function() {
        if (confirm('Upload?')) {
            $.getJSON('conf', {action:'upload', remote:$('#remote').val()}).done(
            function(data) {
            });
        };
    });
});

/*****************************************************************************/