/******************************************************************************
 * portable.js: pure javascript mock of server side library.motw
 *****************************************************************************/

$(document).ready(function () {

    /* This file is using LIBRARY variable from data.js and ITEMS_PER_PAGE
     *  from library.js */

    var BOOKS = LIBRARY.books.add;
    var LIBRARIANS = [];

    /**************************************************************************
    * generate distinct list of authors, titles and librarians
    **************************************************************************/
    var generate_metadata = function() {
        
        /* helper function; add value v to set s */
        var sadd = function(s, v) {
            if ($.inArray(v, s) == -1) {
                s.push(v);
            };
        };
        
        $.each(BOOKS, function(i, book) {
            /* add librarians */
            sadd(LIBRARIANS, book.librarian);
            /* setup portable */
            book.portable = true;
            book.portable_url = '';
        });
    }();

    /**************************************************************************
    * mock ajax call for get_books
    **************************************************************************/
    $.ajax = function(params) {
        if (params.url == 'get_books') {
            params.success(mock_get_books(JSON.parse(params.data)));
        };
    };

    /**************************************************************************
    * mock getJSON for get_book
    **************************************************************************/
    $.getJSON = function(url, params) {
        var book = mock_book(params.uuid);
        return {done: function(f){f(book);}};
    };

    /**************************************************************************
    * this is mock for main get_books api call
    **************************************************************************/
    var mock_get_books = function(params) {
        ret = {
            'books': [],
            'librarians': LIBRARIANS,
            'next_page': params.page + 1, 
            'on_page': -1,
            'total': 0,
        };

        var books = BOOKS;
        if (params.query.authors !== '' || params.query.title !== '' ||
            params.query.librarian !== '' || params.query.search_all !== '') {
            books = search(params.query, books);
        }
        var offset = (params.page-1)*ITEMS_PER_PAGE;
        ret.books = books.slice(offset, offset + ITEMS_PER_PAGE);
        ret.on_page = ret.books.length;
        ret.total = books.length;
        if (offset + ITEMS_PER_PAGE >= ret.total) {
            ret.next_page = null;
        }
        return ret;
    };

    /**************************************************************************
    * this mocks single book info api call
    **************************************************************************/
    var mock_book = function(uuid) {
        return _.findWhere(BOOKS, {uuid: uuid});
    };

    /**************************************************************************
    * this mocks search functionality
    **************************************************************************/
    var search = function(q, books) {
        if (q.authors !== '') {
            var regex = new RegExp(q.authors, 'im');
            books = books.filter(function(book, i) {
                return regex.test(book.authors.join(' '));
            });
        }
        if (q.title !== '') {
            var regex = new RegExp(q.title, 'im');
            books = books.filter(function(book, i) {
                return regex.test(book.title);
            });
        }
        if (q.librarian !== '') {
            books = books.filter(function(book, i) {
                return q.librarian == book.librarian;
            });
        }
        if (q.search_all !== '') {
            var regex = new RegExp(q.search_all, 'im');
            books = books.filter(function(book, i) {
                var str = [book.title,
                           book.authors.join(' '),
                           book.comments,
                           book.tags,
                           book.publisher,
                           book.identifiers].join(' ');
                return regex.test(str);
            });
        }
        return books;
    };
});