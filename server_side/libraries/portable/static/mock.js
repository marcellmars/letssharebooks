$(document).ready(function () {

    /* helper functions */

    /* add value v to set s */
    var sadd = function(s, v) {
        if ($.inArray(v, s) == -1) {
            s.push(v);
        };
    };

    /* mock ajax calls */
    $.ajax = function(params) {
        if (params.url == 'get_books') {
            params.success(mock_get_books(JSON.parse(params.data)));
        };
    };

    $.getJSON = function(url, params) {
        var book = mock_book(params.uuid);
        return {done: function(f){f(book);}};
    };

    /* This file is using LIBRARY variable from data.js and ITEMS_PER_PAGE from library.js  */

    var BOOKS = LIBRARY.books.add;
    var AUTHORS = [];
    var TITLES = [];
    var LIBRARIANS = [];

    var generate_metadata = function() {
        $.each(BOOKS, function(i, book){
            /* add authors */
            var authors = book.authors;
            $.each(authors, function(j, author) {
                sadd(AUTHORS, author);
            });
            /* add titles */
            var title = book.title_sort;
            sadd(TITLES, title);
            /* add librarians */
            var librarian = book.librarian;
            sadd(LIBRARIANS, librarian);
        });
    }();

    var mock_get_books = function(params) {
        ret = {
            'books': [],
            'authors': AUTHORS,
            'titles': TITLES,
            'librarians': LIBRARIANS,
            'books': [],
            'next_page': params.page + 1, 
            'on_page': -1,
            'total': 0,
        };

        var books = BOOKS;
        if (params.query.authors !== '' || params.query.titles !== '' || params.query.librarian !== '') {
            books = search(params.query, books);
        }
        var offset = (params.page-1)*ITEMS_PER_PAGE;
        ret.books = books.slice(offset,
                                offset + ITEMS_PER_PAGE);

        ret.on_page = ret.books.length;
        ret.total = books.length;
        if (offset + ITEMS_PER_PAGE >= ret.total) {
            ret.next_page = null;
        }
        return ret;
    };

    var mock_book = function(uuid) {
        var ret = null;
        $.each(BOOKS, function(i, book) {
            if (book.uuid == uuid) {
                ret = book;
            }
        });
        return ret;
    };

    var search = function(q, books) {
        if (q.authors !== '') {
            books = books.filter(function(elem, pos) {
                return $.inArray(q.authors, elem.authors) > -1;
            });
        }
        if (q.titles !== '') {
            books = books.filter(function(elem, pos) {
                return q.titles == elem.title_sort;
            });
        }
        if (q.librarian !== '') {
            books = books.filter(function(elem, pos) {
                return q.librarian == elem.librarian;
            });
        }
        return books;
    };
});