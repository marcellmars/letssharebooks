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
    var TOTAL = BOOKS.length;
    var AUTHORS = [];
    var TITLES = [];
    var LIBRARIANS = [];

    var generate_metadata = function() {
        for(var i=0;i<BOOKS.length;i++) {
            /* add authors */
            var authors = BOOKS[i].authors;
            for(var j=0;j<authors.length;j++) {
                sadd(AUTHORS, authors[j]);
            };
            /* add titles */
            var title = BOOKS[i].title_sort;
            sadd(TITLES, title);
            /* add librarians */
            var librarian = BOOKS[i].librarian;
            sadd(LIBRARIANS, librarian);
        };
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
            'total': TOTAL,
        };

        var books = BOOKS;
        var offset = (params.page-1)*ITEMS_PER_PAGE;
        ret.books = books.slice(offset,
                                offset + ITEMS_PER_PAGE);

        ret.on_page = ret.books.length;
        if (offset + ITEMS_PER_PAGE >= TOTAL) {
            ret.next_page = null;
        }
        return ret;
    };

    var mock_book = function(uuid) {
        for(var i=0;i<BOOKS.length;i++) {
            if (BOOKS[i].uuid = uuid) {
                return BOOKS[i];
            }
        };
        return null;
    };
});