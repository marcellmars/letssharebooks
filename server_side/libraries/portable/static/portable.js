/******************************************************************************
 * portable.js: pure javascript mock of server side library.motw
 *****************************************************************************/

$(document).ready(function () {

    /* This file is using LIBRARY variable from data.js and ITEMS_PER_PAGE
     *  from library.js
     */

    var BOOKS = LIBRARY.books.add;
    var AUTHORS = [];
    var TITLES = [];
    var LIBRARIANS = [];
    
    /**************************************************************************
    * helper function; add value v to set s
    **************************************************************************/
    var sadd = function(s, v) {
        if ($.inArray(v, s) == -1) {
            s.push(v);
        };
    };

    /**************************************************************************
    * generate distinct list of authors, titles and librarians
    **************************************************************************/
    var generate_metadata = function() {
        $.each(BOOKS, function(i, book) {
            /* add authors */
            var authors = book.authors;
            $.each(authors, function(j, author) {
                sadd(AUTHORS, author);
            });
            /* add titles */
            var title = book.title;
            sadd(TITLES, title);
            /* add librarians */
            var librarian = book.librarian;
            sadd(LIBRARIANS, librarian);
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
    * mock getJSON
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
            'authors': AUTHORS,
            'titles': TITLES,
            'librarians': LIBRARIANS,
            'books': [],
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
        var ret = null;
        $.each(BOOKS, function(i, book) {
            if (book.uuid == uuid) {
                ret = book;
            }
        });
        return ret;
    };

    /**************************************************************************
    * this mocks search functionality
    **************************************************************************/
    var search = function(q, books) {
        if (q.authors !== '') {
            var regex = new RegExp(q.authors, 'gim');
            books = books.filter(function(book, i) {
                return regex.test(book.authors.join(' '));
            });
        }
        if (q.title !== '') {
            var regex = new RegExp(q.title, 'gim');
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

    /**************************************************************************
    * these are portable-specific overrides
    **************************************************************************/

    var get_directory_path = function (book) {
        var format = book.formats[0]
        var file_path = book.format_metadata[format].path
        var directory_path = ""
        var directory = file_path.split("/").slice(-3,-1)
        directory.forEach(function(el){directory_path += el + "/"});
        return [directory_path, file_path];
    };

    window.gen_book_string_parts = function (base_url, format, book) {
        book.application_id = '';
        var df_path = get_directory_path(book);
        var file_name = df_path[1].split("/").slice(-1);
        return {
            'base_url': '',
            'format': '',
            'book': book,
            'portable_book': df_path[0] + file_name,
            'portable_format': format
        }
    };

    window.gen_book_content = function (base_url, book, authors, formats) {
        book.application_id = '';
        var df_path = get_directory_path(book);
        return {
            'base_url': '',
            'book': book,
            'book_title_stripped': '',
            'authors': authors,
            'formats': formats,
            'get_cover': '',
            'get_opf' : '',
            'portable_cover': df_path[0] + 'cover.jpg',
            'portable_opf': df_path[0] + 'metadata'
        }
    };

    window.gen_book_modal = function (base_url, book, formats) {
        book.application_id = '';
        var df_path = get_directory_path(book);
        return { 
            'base_url': '',
            'book': book,
            'book_title_stripped': '',
            'formats': formats,
            'get_cover': '',
            'get_opf': '',
            'portable_cover': df_path[0] + 'cover.jpg',
            'portable_opf': df_path[0] + 'metadata',
        }
    };

});