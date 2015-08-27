/* ----------------------------------------------------------------------------
 * Loads and displays book data
 * ----------------------------------------------------------------------------
 */

var load_book = function () {
    var uuid = location.pathname.match(/\/b\/(.*)/)[1];
    $.getJSON('/book', {uuid: uuid}).done(function( book ) {
        var bdata = common.gen_book_data(book, 'book-permalink');
        $('#content').append(
            common.templates.book_permalink(bdata));
    });
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    load_book();
});