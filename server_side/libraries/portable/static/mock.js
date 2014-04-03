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
        if (params.query.authors !== '' || params.query.titles !== '' || params.query.librarian !== '' || params.query.search_all !== '') {
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
            var regex = new RegExp(q.authors, 'gim');
            books = books.filter(function(book, i) {
                return regex.test(book.authors.join(' '));
            });
        }
        if (q.titles !== '') {
            var regex = new RegExp(q.titles, 'gim');
            books = books.filter(function(book, i) {
                return regex.test(book.title_sort);
            });
        }
        if (q.librarian !== '') {
            books = books.filter(function(book, i) {
                return q.librarian == book.librarian;
            });
        }
        if (q.search_all !== '') {
            var regex = new RegExp(q.search_all, 'gim');
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