import subprocess
import os
import cherrypy
import requests
import md5
import glob
import simplejson

class JSONBooks:
    def __init__(self, domain = "web.dokr"):
        self.domain = domain

    def get_tunnel_ports(self, login="tunnel"):
        uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
        return subprocess.check_output(["/usr/local/bin/get_tunnel_ports.sh", uid]).split()

    def get_metadata(self):
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
                    book['authors'] = book_metadata['authors']
                    book['domain'] = self.domain
                    all_books.append(book)

            open(hash_filename, "w").write(simplejson.dumps(all_books))
        return all_books[100:116]

class Root(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def initpage(self):
        json_books = JSONBooks()
        cl = cherrypy.request.headers['Content-Length']
        body = cherrypy.request.body.read(int(cl))
        #body = simplejson.loads(rawbody)
        # do_something_with(body)
        return json_books.get_metadata()

    @cherrypy.expose
    def index(self):
        return """
<html>
<head><title>Libraries</title>
<script type="application/javascript" src="static/jquery-1.10.2.min.js"></script>
<script type="application/javascript" src="static/jquery-1.10.2.min.map"></script>
<link rel="stylesheet" type="text/css" href="static/style.css" />
<script type='text/javascript'>
function initpage() {
    $.ajax({
      type: 'POST',
      url: "initpage",
      contentType: "application/json",
      processData: false,
      data: $('#updatebox').val(),
      success: function(books) {
                    window.foobar = books;
                    $.each(books, function(n, book) {
                        $('#content').append('<div class="cover"><img src="http://www'+ book.tunnel + '.' + book.domain + '/get/cover/' + book.id + '.jpg"></img><h2>' + book.title + '<br/><span>' + book.authors.join(", ")  + '</span></h2><span class="download">Download: <a href="http://www' + book.tunnel + '.' + book.domain + '/get/opf/' + book.id  + book.title + '.opf">.opf</a></span></div>'); 
                    })
      },
      dataType: "json"
    });
}

$(document).ready(initpage);

</script>
</title>
<body>
<input type='textbox' id='updatebox' value='{}' size='20' />
<input type='submit' value='Update' onClick='initpage(); return false' />
<div id="content"></div>
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
