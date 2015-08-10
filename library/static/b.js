/* ----------------------------------------------------------------------------
 * Loads and displays book data
 * ----------------------------------------------------------------------------
 */

var load_book = function () {
    var uuid = location.pathname.match(/\/b\/(.*)/)[1];
    $.getJSON('/book', {uuid: uuid}).done(function( book ) {
        var bdata = common.gen_book_data(book);
        $('#content').append(
            common.templates.book_permalink(bdata));
        $('.navbar-text').append(
            common.templates.book_permalink_navbar_text(bdata));
    });
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    load_book();
});