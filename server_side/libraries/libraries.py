import subprocess
import os
import cherrypy
import requests
import md5
import glob
import simplejson
import operator

class JSONBooks:
    def __init__(self, domain = "web.dokr"):
        self.domain = domain

    def get_tunnel_ports(self, login="tunnel"):
        uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
        return subprocess.check_output(["/usr/local/bin/get_tunnel_ports.sh", uid]).split()

    def get_metadata(self, start, offset):
        end = start + offset
        all_books = []
        for tunnel in self.get_tunnel_ports():
            base_url = 'http://www{tunnel}.{domain}/'.format(tunnel=tunnel, domain=self.domain)
            total_num_url = 'ajax/search?query='
            total_num = requests.get("{base_url}{total_num_url}".format(base_url=base_url, total_num_url=total_num_url)).json()['total_num']
            books_ids_url = 'ajax/search?query=&num={total_num}&sort=title'.format(total_num=total_num)
            books_ids = requests.get("{base_url}{books_ids_url}".format(base_url=base_url, books_ids_url=books_ids_url)).json()['book_ids']
            books_ids_hash = md5.new("".join((str(book_id) for book_id in books_ids))).hexdigest()
            hash_files = glob.glob("{books_ids_hash}_*".format(books_ids_hash=books_ids_hash))
            hash_filename = "{books_ids_hash}_{tunnel}".format(books_ids_hash=books_ids_hash, tunnel=tunnel)
            if hash_files:
                if hash_filename in hash_files:
                    books = simplejson.loads(open(hash_filename, "r").read())
                    all_books = books
                else:
                    books = simplejson.loads(open(glob.glob("{books_ids_hash}_*".format(books_ids_hash=books_ids_hash))[0, "r"]).read())
                    for book in books:
                        book['tunnel'] = tunnel
                    all_books = books
            else:
                book_metadata_url = 'ajax/book/'
                for book_id in books_ids:
                    book = {}
                    book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=base_url, book_metadata_url=book_metadata_url, book_id=book_id)).json()
                    book['id'] = book_id
                    book['tunnel'] = tunnel
                    book['title'] = book_metadata['title']
                    book['title_sort'] = book_metadata['title_sort']
                    book['authors'] = book_metadata['authors']
                    book['domain'] = self.domain
                    book['formats'] = book_metadata['formats']
                    all_books.append(book)

            open(hash_filename, "w").write(simplejson.dumps(all_books))
        all_books.sort(key=operator.itemgetter('title_sort'))
        return all_books[start:end]

class Root(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def flip_page(self):
        #cl = cherrypy.request.headers['Content-Length']
        #body = cherrypy.request.body.read(int(cl))
        print(cherrypy.request.json)
        return cherrypy.request.json
        #return body

 
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def render_page(self):
        json_books = JSONBooks()
        start_offset = cherrypy.request.json
        print(start_offset['start'])
        #cl = cherrypy.request.headers['Content-Length']
        #body = cherrypy.request.body.read(int(cl))
        return json_books.get_metadata(start_offset['start'], start_offset['offset'])

    @cherrypy.expose
    def index(self):
        return """
<html>
<head><title>Libraries</title>
<script type="application/javascript" src="static/jquery-1.10.2.min.js"></script>
<script type="application/javascript" src="static/jquery-1.10.2.min.map"></script>
<script type="application/javascript" src="static/jquery-ui.js"></script>
<link rel="stylesheet" type="text/css" href="static/style.css" />
<link rel="stylesheet" type="text/css" href="static/jquery-ui.css" />
<script type='text/javascript'>
var LSB = {}
LSB.start = 0;
LSB.offset = 8;

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
                    $.each(books, function(n, book) {
                        var base_url = 'http://www' + book.tunnel + '.' + book.domain
                        var formats = ""
                        book.formats.map(function(format) { 
                            formats = formats + '<a href="' + base_url + '/get/' + format + '/' + book.id +'.' + format + '">' + format.toUpperCase() + '</a> '});
                        
                        $('#content').append('<div class="cover"><a href="'+ base_url +'/browse/book/'+ book.id +'" target="_blank"><img src="' + base_url + '/get/cover/' + book.id + '.jpg"></img></a><h2>' + book.title + '<br/><span>' + book.authors.join(", ")  + '</span></h2><span class="download">Metadata: <a href="'+ base_url + '/get/opf/' + book.id  + book.title.replace(/\?/g, "") + '.opf">.opf</a><br/>Download: ' + formats + ' </span></div>')
                })
      },
      dataType: "json"
    });
}

add_toolbar = function() {
    $('#content').append('<div id="toolbar"><div id="prev_page"></div><div id="next_page"></div></div>');
    $('#toolbar').append($('#prev_page').button({label: 'prev'}))
    $('#prev_page').click(function() {prev_page()});
    $('#toolbar').append($('#next_page').button({label: 'next'})).click(function() {next_page()});
    $('#next_page').click(function() {next_page()});
}

next_page = function() {
    LSB.start = LSB.start + LSB.offset;
    $('#content').empty();
    add_toolbar();
    render_page();
}

prev_page = function() {
    LSB.start = LSB.start - LSB.offset;
    $('#content').empty();
    add_toolbar();
    render_page();
}


$(document).ready(init_page);

</script>
</title>
<body>
<div id="content">
</div>
</body>
</html>
"""

current_dir = os.path.dirname(os.path.abspath(__file__))
conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(current_dir, 'static'),
                    'tools.staticdir.content_types': {'javascript': 'application/javascript',
                                                      'css': 'text/css'}}}
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.quickstart(Root(), '/', config=conf)
