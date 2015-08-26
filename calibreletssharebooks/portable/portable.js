//
// portable.js: js mock of server side library.motw
//

$(document).ready(function () {

    // external dependency: var LIBRARY (data.js)
    var BOOKS = LIBRARY.books.add;

    // how many books to show on single page
    var ITEMS_PER_PAGE = 16;

    //
    // mock ajax call (get_books)
    //
    $.ajax = function(params) {
        if (params.url == 'get_books') {
            params.success(mock_get_books(JSON.parse(params.data)));
        };
    };

    //
    // mock all getJSON calls
    //
    $.getJSON = function(url, params) {
        if (url === 'get_catalogs') {
            var catalogs = [{librarian: LIBRARY.librarian,
                             library_uuid: LIBRARY.library_uuid}];
            return {done: function(f){f(catalogs);}};
        } else if (url === 'book') {
            var book = mock_book(params.uuid);
            return {done: function(f){f(book);}};
        } else if (url === 'status?callback=?') {
            var data = {num_of_books: BOOKS.length};
            return {done: function(f){f(data);}};
        } else if (url === 'autocomplete') {
            var metadata = generate_metadata(BOOKS);
            return {done: function(f){f(metadata);}};
        };
    };

    //
    // this is mock for main get_books api call
    //
    var mock_get_books = function(params) {
        ret = {
            // these will be populated here
            'books': [],
            'total': 0,
            'last_id': null,
            'librarians': [LIBRARY.librarian]
        };
        var books = BOOKS;
        if (params.query.text !== '' || params.query.librarian !== '') {
            books = search(params.query, books);
        };
        // calculate page to show depending on the params.last_id
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

    //
    // this mocks single book info api call
    //
    var mock_book = function(uuid) {
        return _.findWhere(BOOKS, {uuid: uuid});
    };

    //
    // this mocks search functionality
    //
    var search = function(q, books) {
        // select books by given librarian
        if (q.librarian !== '') {
            books = books.filter(function(book, i) {
                return q.librarian == book.librarian;
            });
        };
        // set default property to 'all', if not specified
        if (!_.contains(['authors', 'title', 'tags', 'all'], q.property)) {
            q.property = 'all';
        };
        // perform search
        if (q.text !== '') {
            var regex = new RegExp(q.text, 'im');
            // search by title
            if (q.property == 'title') {
                books = books.filter(function(book, i) {
                    return regex.test(book.title);
                });
            // search by author
            } else if (q.property == 'authors') {
                books = books.filter(function(book, i) {
                    return regex.test(book.authors.join(' '));
                });
            // search tags
            } else if (q.property == 'tags') {
                books = books.filter(function(book, i) {
                    return regex.test(book.tags.join(' '));
                });
            // search all metadata
            } else {
                books = books.filter(function(book, i) {
                    var str = [book.title,
                               book.authors.join(' '),
                               book.comments,
                               book.tags,
                               book.publisher,
                               book.identifiers].join(' ');
                    return regex.test(str);
            }); 
            };
        };
        return books;
    };

    //
    // generate distinct list of authors, titles and librarians
    //
    var generate_metadata = function(books) {
        var sadd = function(s, v) {
            if ($.inArray(v, s) == -1) {
                s.push(v);
            };
        };
        var metadata = {
            'authors': [],
            'titles': [],
            'tags': [],
        };
        $.each(books, function(i, book) {
            var authors = book.authors;
            $.each(authors, function(j, author) {
                sadd(metadata['authors'], author);
            });
            var tags = book.tags;
            $.each(tags, function(j, tag) {
                sadd(metadata['tags'], tag);
            });
            sadd(metadata['titles'], book.title);
        });
        return metadata;
    };
});
