/* ----------------------------------------------------------------------------
 * Precompile templates
 * ----------------------------------------------------------------------------
 */

var book_permalink_tmpl = _.template($('#book-permalink-tmpl').text().trim());

/* ----------------------------------------------------------------------------
 * Loads and displays book data
 * ----------------------------------------------------------------------------
 */

var load_book = function () {
    var uuid = location.pathname.match(/\/b\/(.*)/)[1];
    $.getJSON('/book', {uuid: uuid}).done(function( book ) {
        $('#book').append(book_permalink_tmpl({'book': book}));
    });
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    load_book();
});