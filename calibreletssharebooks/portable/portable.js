/******************************************************************************
 * portable.js: pure javascript mock of server side library.motw
 *****************************************************************************/

$(document).ready(function () {

    var BOOKS = LIBRARY.books.add
    var LIBRARIANS = [];

    var ITEMS_PER_PAGE = 16;

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
            'authors': [],
            'titles': [],
            'librarians': LIBRARIANS,
            'total': 0,
            'last_id': null,
        };

        var books = BOOKS;
        // if (params.query.text !== '' || params.query.librarian !== '') {
        //     books = search(params.query, books);
        // };
        var offset = 0;
        if (params.last_id !== null) {
            // find index of first book that has id greater than last_id
            for(var i=0;i<books.length;i++) {
                if(books[i].uuid > params.last_id) {
                    break;
                };
                offset += 1;
            };
        };
        ret.books = books.slice(offset, offset + ITEMS_PER_PAGE);
        ret.last_id = null;
        if (offset < books.length && ret.books.length == ITEMS_PER_PAGE) {
            ret.last_id = _.last(ret.books).uuid;
        };
        ret.total = books.length;
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
