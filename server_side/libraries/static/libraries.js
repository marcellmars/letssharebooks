var LSB = {}
LSB.start = 0;
LSB.total_num = 1;
LSB.offset = 16;
LSB.query = "";
LSB.carry = "";
LSB.processing = "";
LSB.prefix_url = "http://www";


init_page = function() {
    add_toolbar();
    render_page();
};

render_page = function() {

    $.ajax({
      type: 'POST',
      url: "render_page",
      contentType: "application/json",
      processData: false,
      data: JSON.stringify(LSB),
      success: function(books) {
                    $('#content').empty();
                    window.foobar = books;
                    add_toolbar();
                    toolbar_data = books.pop()
                    LSB.total_num = toolbar_data['total_num']
                    LSB.query = toolbar_data['query']
                    LSB.processing = toolbar_data['processing']
                    refresh_pagination()
                    $(function () {
                            $('#authors').autocomplete({source: toolbar_data['authors'], minLength:2});
                            $('#titles').autocomplete({source: toolbar_data['titles'], minLength:2});
                        });
                    $.each(books, function(n, book) {
                        window.barfoo = book;
                        var base_url = LSB.prefix_url + book.tunnel + '.' + book.domain
                        var formats = ""
                        var authors = '<div id="authorz">'

                        book.formats.map(function(format) { 
                            formats = formats + '<a href="' + base_url + '/get/' + format + '/' + book.id +'.' + format + '">' + format.toUpperCase() + '</a> '});

                         book.authors.map(function(author) {
                                author_s = author.replace("'", " ")
                                author_param = 'search_author("' + author_s + '")'
                                authors = authors + "<a id='author' href='#' title='show only books by " + author_s  + "' onClick='" + author_param + "'>" + author + ", </a>&nbsp;"});

                        last_comma = authors.lastIndexOf(",");
                        authors = authors.substr(0, last_comma) + authors.substr(last_comma + 1) + '</div>'
                        $('#content').append('<div class="cover"><a href="'+ base_url +'/browse/book/'+ book.id +'" target="_blank" id="more_about" title="about this book"><img src="' + base_url + '/get/cover/' + book.id + '.jpg"></img></a><h2><a href="' + base_url + '/browse/book/' + book.id + '" target="_blank" id="more_about" title="about this book">' + book.title + '</a><br/>' + authors  + '</h2><span class="download">Metadata: <a href="'+ base_url + '/get/opf/' + book.id  + ' ' + book.title.replace(/\?/g, "") + '.opf" title="import metadata directly to calibre">.opf</a><br/>Download: ' + formats + ' </span></div>')
                });

    },
      dataType: "json"
    });
};

refresh_pagination = function () {
    //$('.pagination').button({label: ' ' + (+LSB.start + 1)+ ' - ' + (+LSB.start + +LSB.offset) + ' out of ' + LSB.total_num + ' books ' + LSB.processing, disabled: true})
    $('.pagination').button({label: 'HOME (' + (+LSB.start + 1)+ ' - ' + (+LSB.start + +LSB.offset) + ' out of ' + LSB.total_num + ' books)' + LSB.processing}).click(function() {search_query()})
};

add_toolbar = function() {
    $('#content').append('<div id="toolbar"><div id="prev_page"></div><div id="next_page"></div></div>');
    $('#content').append('<div id="searchbar"></div>')

    $('#toolbar').append($('#prev_page').button({label: '<<<'}));
    $('#prev_page').click(function() {prev_page()});
    $('#toolbar').append($('#next_page').button({label: '>>>'}));
    $('#next_page').click(function() {next_page()});
    $('#toolbar').append('<div class="pagination"></div>');

    $('#searchbar').append('<div class="ui-widget"><input id="authors" placeholder="authors"/><input id="titles" placeholder="titles"/><input id="search_all" placeholder="search all metadata"/><div id="search"></div></div>')
    $('#search').button({label: 'SEARCH'}).click(search_query)

};

search_query = function () {
    if ($('#authors').val()) {
        LSB.query = 'authors:' + $('#authors').val()
        LSB.carry = " OR "
    } else {
        LSB.query = '';
        LSB.carry = '';
    }
    if ($('#titles').val()) {
        LSB.query += LSB.carry + 'title:' + $('#titles').val()
        LSB.carry = " OR "
    } else if (LSB.carry != " OR ") {
        LSB.query = '';
        LSB.carry = '';
    }

    if ($('#search_all').val()) {
        LSB.query += LSB.carry + $('#search_all').val()
    } else if (LSB.carry != " OR ") {
        LSB.query = '';
        LSB.carry = '';
    }
    
    LSB.start = 0;
    render_page()
    LSB.query = '';
    LSB.carry = '';
};

search_author = function(author) {
    LSB.query = "authors:" + author;
    console.log(LSB.query);
    LSB.start = 0;
    render_page();
    LSB.query = "";
};

next_page = function() {
    LSB.start = LSB.start + LSB.offset;
    if (LSB.start+LSB.offset >= LSB.total_num) {
        LSB.start = LSB.total_num - LSB.offset;
    }
    render_page();
};

prev_page = function() {
    LSB.start = LSB.start - LSB.offset;
    if (LSB.start <= 0) {
        LSB.start = 0;
    }
    render_page();
};

$(document).ajaxStart(function() { 
    $('body').addClass("loading"); 
});

$(document).ajaxStop(function() { 
    $('body').removeClass("loading"); 
});

$(function() {
    $(document).tooltip({track:true});
});

$(document).ready(function() {
    init_page();
});
