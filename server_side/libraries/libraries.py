import subprocess
import os
import cherrypy
import requests
import md5
import glob
import simplejson
import bson.json_util as bjson
import operator
import itertools
import threading
import time
from pymongo import MongoClient
import pymongo

class UrlLibThread(threading.Thread):
    def __init__(self, books_ids, book_metadata_url, domain, tunnel, base_url):
        threading.Thread.__init__(self)
        self.mongo_client = MongoClient('172.17.42.1', 49153)
        self.db = self.mongo_client.letssharebooks
        self.books_ids = books_ids
        self.base_url = base_url
        self.book_metadata_url = book_metadata_url
        self.domain = domain
        self.tunnel = tunnel

    def run(self):

            for book_id in self.books_ids:
                lsb_updated = "".join(map(str, self.books_ids))
                book = {}

                book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=book_id)).json()
                last_book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=self.books_ids[-1])).json()
                mongo_book = self.db.books.find_one({'uuid': book_metadata['uuid']})
                last_mongo_book = self.db.books.find_one({'uuid': last_book_metadata['uuid']})
                
                if last_mongo_book and last_mongo_book['lsb_updated'] == lsb_updated:
                    break

                if mongo_book and mongo_book['last_modified'] == book_metadata['last_modified'] and mongo_book['tunnel'] == self.tunnel:
                    continue
                elif mongo_book and mongo_book['last_modified'] == book_metadata['last_modified']:
                    mongo_book['tunnel'] = self.tunnel
                    self.db.books.save(mongo_book)
                else:
                    book['id'] = book_id
                    book['uuid'] = book_metadata['uuid']
                    book['last_modified'] = book_metadata['last_modified']
                    book['tunnel'] = self.tunnel
                    book['title'] = book_metadata['title']
                    book['title_sort'] = book_metadata['title_sort']
                    book['authors'] = book_metadata['authors']
                    book['domain'] = self.domain
                    book['formats'] = book_metadata['formats']
                    book['lsb_updated'] = lsb_updated
                    self.db.books.insert(book)
            return
 

class JSONBooks:
    def __init__(self, domain = "web.dokr"):
        self.mongo_client = MongoClient('172.17.42.1', 49153)
        self.db = self.mongo_client.letssharebooks
        self.domain = domain

    def get_tunnel_ports(self, login="tunnel"):
        uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
        return subprocess.check_output(["/usr/local/bin/get_tunnel_ports.sh", uid]).split()

    def get_metadata(self, start, offset, query):
        processing_status = ""
        self.tunnel = False
        self.query = query.encode('utf-8')
        self.start = start
        self.offset = offset
        self.end = self.start + self.offset
        self.all_books = []
        for tunnel in self.get_tunnel_ports():
            self.tunnel = tunnel
            self.base_url = '{prefix_url}{tunnel}.{domain}/'.format(prefix_url=prefix_url, tunnel=self.tunnel, domain=self.domain)
            self.total_num_url = 'ajax/search?query='
            self.total_num = requests.get("{base_url}{total_num_url}".format(base_url=self.base_url, total_num_url=self.total_num_url)).json()['total_num']
            if self.total_num == 0:
                continue
            self.books_ids_url = 'ajax/search?query=&num={total_num}&sort=last_modified'.format(total_num=self.total_num)
            self.books_ids = requests.get("{base_url}{books_ids_url}".format(base_url=self.base_url, books_ids_url=self.books_ids_url)).json()['book_ids']
            self.book_metadata_url = 'ajax/book/'
            thrd = UrlLibThread(self.books_ids, self.book_metadata_url, self.domain, self.tunnel, self.base_url)
            thrd.start()
            for book in self.db.books.find({'tunnel':self.tunnel}):
                self.all_books.append(simplejson.loads(bjson.dumps(book, default=bjson.default)))
        
        self.all_books.sort(key=operator.itemgetter('title_sort'))
        authors_key = operator.itemgetter("authors")
        toolbar_authors = sorted(list(set(list(itertools.chain.from_iterable(map(authors_key, self.all_books))))))
        titles_key = operator.itemgetter("title")
        toolbar_titles = sorted(list(set(map(titles_key, self.all_books))))
        toolbar_data = {"total_num": len(self.all_books), "authors": toolbar_authors, "titles": toolbar_titles, "query": self.query, "processing": processing_status}
        toolbar_data = {"total_num": len(self.all_books), "authors": "", "titles": "", "query": self.query, "processing": processing_status}
        all_books_return = self.all_books[self.start:self.end]
        all_books_return.append(toolbar_data)
        return all_books_return

class Root(object):
 
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def render_page(self):
        json_books = JSONBooks()
        json_request = cherrypy.request.json
        return json_books.get_metadata(json_request['start'], json_request['offset'], json_request['query'])

    @cherrypy.expose
    def index(self):
        return """
<html>
<head><title>Libraries</title>
<script type="application/javascript" src="static/jquery-1.9.1.js"></script>
<script type="application/javascript" src="static/jquery-ui-1.10.3.custom.min.js"></script>
<link rel="stylesheet" type="text/css" href="static/style.css" />
<link rel="stylesheet" type="text/css" href="static/jquery-ui-1.10.3.custom.min.css" />
<script type='text/javascript' charset='utf-8'>
var LSB = {}
LSB.start = 0;
LSB.total_num = 1;
LSB.offset = 8;
LSB.query = "";
LSB.carry = "";
LSB.processing = "";
LSB.prefix_url = "http://www"


init_page = function() {
                add_toolbar();
                render_page();
}

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
                            $('#authors').autocomplete({source: toolbar_data['authors']});
                            $('#titles').autocomplete({source: toolbar_data['titles']});
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
                        $('#content').append('<div class="cover"><a href="'+ base_url +'/browse/book/'+ book.id +'" target="_blank" id="more_about" title="about this book"><img src="' + base_url + '/get/cover/' + book.id + '.jpg"></img></a><h2><a href="' + base_url + '/browse/book/' + book.id + '" target="_blank" id="more_about" title="about this book">' + book.title + '</a><br/>' + authors  + '</h2><span class="download">Metadata: <a href="'+ base_url + '/get/opf/' + book.id  + book.title.replace(/\?/g, "") + '.opf" title="import metadata directly to calibre">.opf</a><br/>Download: ' + formats + ' </span></div>')
                });

    },
      dataType: "json"
    });
}

refresh_pagination = function () {
    //$('.pagination').button({label: ' ' + (+LSB.start + 1)+ ' - ' + (+LSB.start + +LSB.offset) + ' out of ' + LSB.total_num + ' books ' + LSB.processing, disabled: true})
    $('.pagination').button({label: 'HOME (' + (+LSB.start + 1)+ ' - ' + (+LSB.start + +LSB.offset) + ' out of ' + LSB.total_num + ' books)' + LSB.processing}).click(function() {search_query()})
}

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

}

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
}

search_author = function(author) {
        LSB.query = "authors:" + author;
        console.log(LSB.query);
        LSB.start = 0;
        render_page();
        LSB.query = "";
}

next_page = function() {
    LSB.start = LSB.start + LSB.offset;
    if (LSB.start+LSB.offset >= LSB.total_num) {
        LSB.start = LSB.total_num - LSB.offset;
    }
    render_page();
}

prev_page = function() {
    LSB.start = LSB.start - LSB.offset;
    if (LSB.start <= 0) {
        LSB.start = 0;
    }
    render_page();
}

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

</script>
</title>
<body>
<div id="content">
</div>
<div class="modal"></div>
</body>
</html>
"""

base_dir = "/var/www/libraries/"
prefix_url = "http://www"
current_dir = os.path.dirname(os.path.abspath(__file__))
conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(current_dir, 'static'),
                    'tools.staticdir.content_types': {'javascript': 'application/javascript',
                                                      'css': 'text/css',
                                                      'gif': 'image/gif'
                                                       }}}
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 4321
cherrypy.quickstart(Root(), '/', config=conf)
