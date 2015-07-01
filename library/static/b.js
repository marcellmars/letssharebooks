var load_book = function () {
    var uuid = location.pathname.match(/\/b\/(.*)/)[1];
    $.getJSON('/book', {uuid: uuid}).done(function( book ) {
        console.log(book);
        $('<p>', {text: book.title}).appendTo($('#book'));
    });
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    load_book();
});