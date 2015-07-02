/* ----------------------------------------------------------------------------
 * Loads and displays book data
 * ----------------------------------------------------------------------------
 */

var load_book = function () {
    var uuid = location.pathname.match(/\/b\/(.*)/)[1];
    $.getJSON('/book', {uuid: uuid}).done(function( book ) {
        $('#book').append(
            common.templates.book_permalink(
                common.gen_book_data(book)));
    });
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    load_book();
});