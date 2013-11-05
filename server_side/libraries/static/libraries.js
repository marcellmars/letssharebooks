/* ----------------------------------------------------------------------------
 * Global configuration and state
 * ----------------------------------------------------------------------------
 */

var PREFIX_URL = 'https://www';
var ITEMS_PER_PAGE = 16;
var STATE = {
    page: 1,
};

/* ----------------------------------------------------------------------------
 * Renders single book
 * ----------------------------------------------------------------------------
 */
var render_book = function(i, book) {
    var formats = '';
    var base_url = [
        PREFIX_URL,
        book.tunnel,
        '.',
        book.domain].join('');
    var authors = '<div id="authorz">';
    
    book.formats.map(function (format) {
        var string_parts = [
            '<a href="', base_url, '/get/', format, '/', book.id,
            '.', format, '">', format.toUpperCase(), '</a>'].join('');
        formats = formats + string_parts;
    });
    book.authors.map(function (author) {
        var author_s = author.replace("'", " ");
        var author_param = 'search_author("' + author_s + '")';
        var string_parts = [
            "<a id='author' href='#' title='show only books by ", author_s,
            "' onClick='", author_param, "'>", author, ", </a>&nbsp;"].join('');
        authors = authors + string_parts;
    });

    var last_comma = authors.lastIndexOf(',');
    authors = authors.substr(0, last_comma) + authors.substr(last_comma + 1) + '</div>';
    var book_content = [
        '<div class="cover"><a href="', base_url, '/browse/book/', book.id,
        '" target="_blank" id="more_about" title="about this book"><img src="',
        base_url, '/get/cover/', book.id, '.jpg"></img></a><h2><a href="', base_url,
        '/browse/book/', book.id, '" target="_blank" id="more_about" title="about this book">',
        book.title, '</a><br/>', authors, '</h2><span class="download">Metadata: <a href="',
        base_url, '/get/opf/', book.id, ' ', book.title.replace(/\?/g, ""),
        '.opf" title="import metadata directly to calibre">.opf</a><br/>Download: ',
        formats, ' </span></div>'].join('');
    $('#content').append(book_content);  
};

/* ----------------------------------------------------------------------------
 * Main ajax entry point
 * ----------------------------------------------------------------------------
 */

var render_page = function () {
    $.ajax({
        type: 'POST',
        url: 'get_books',
        contentType: 'application/json',
        processData: false,
        data: JSON.stringify(STATE),
        dataType: 'json',
        success: function (data) {
            parse_response(data);
        }
    });
};

/* --------------------------------------------------------------------------*/

var parse_response = function (data) {
    update_pagination_info(data['on_page'], data['total']);
    if (data['next_page'] === null) {
        modify_button('#next_page', 'not-active');
    };
    $('#content').empty();
    $.each(data['books'], render_book);
};

/* --------------------------------------------------------------------------*/

var update_pagination_info = function (items_on_page, total_num_of_items) {
    if (total_num_of_items == 0) {
        $('#page-msg').attr('value', '0 books');
        return;
    }
    var offset = (STATE.page-1) * ITEMS_PER_PAGE + 1;
    var total = 100;
    var msg = ['(',
               offset,
               '-',
               offset + items_on_page - 1,
               'out of',
               total_num_of_items,
               'books )'].join(' ');
    $('#page-msg').attr('value', msg);
};

/* --------------------------------------------------------------------------*/

var next_page = function () {
    STATE.page += 1;
    modify_button('#prev_page', 'active');
    render_page();
};

/* --------------------------------------------------------------------------*/

var prev_page = function () {
    STATE.page -= 1;
    modify_button('#next_page', 'active');
    $('#next_page').show();
    if (STATE.page <= 1) {
        modify_button('#prev_page', 'not-active');
    }
    render_page();
};

/* ----------------------------------------------------------------------------
 * Adds complete toolbar to the top of the page
 * ----------------------------------------------------------------------------
 */

var init_toolbar = function () {
    $('#prev_page').click(function () {prev_page(); });
    $('#next_page').click(function () {next_page(); });
    $('#search').click(function() {
        search_query();
    });
    modify_button('#prev_page', 'not-active');
};

/* ----------------------------------------------------------------------------
 * Changes state of the prev/next page buttons
 * ----------------------------------------------------------------------------
 */

var modify_button = function (button, state) {
    var elem = $(button);
    if (state == 'active') {
        elem.attr('disabled', false);
        elem.removeClass('not-active');
        elem.addClass('active');
    } else if (state == 'not-active') {
        elem.attr('disabled', true);
        elem.removeClass('active');
        elem.addClass('not-active');
    }
};

/* --------------------------------------------------------------------------*/

var init_page = function () {
    init_toolbar();
    render_page();
};

/* --------------------------------------------------------------------------*/

var search_query = function () {
    if ($('#authors').val()) {
        LSB.query = 'authors:' + $('#authors').val();
        LSB.carry = " OR ";
    } else {
        LSB.query = '';
        LSB.carry = '';
    }
    if ($('#titles').val()) {
        LSB.query += LSB.carry + 'title:' + $('#titles').val();
        LSB.carry = " OR ";
    } else if (LSB.carry != " OR ") {
        LSB.query = '';
        LSB.carry = '';
    }

    if ($('#search_all').val()) {
        LSB.query += LSB.carry + $('#search_all').val();
    } else if (LSB.carry != " OR ") {
        LSB.query = '';
        LSB.carry = '';
    }
    
    LSB.start = 0;
    render_page();
    LSB.query = '';
    LSB.carry = '';
};

/* --------------------------------------------------------------------------*/

var search_author = function (author) {
    LSB.query = "authors:" + author;
    console.log(LSB.query);
    LSB.start = 0;
    render_page();
    LSB.query = "";
};

/* --------------------------------------------------------------------------*/

$(document).ajaxStart(function () { 
    $('body').addClass("loading"); 
});

/* --------------------------------------------------------------------------*/

$(document).ajaxStop(function () { 
    $('body').removeClass("loading"); 
});

/* --------------------------------------------------------------------------*/

$(function () {
    $(document).tooltip({track:true});
});

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    init_page();
});