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
from jinja2 import Environment, FileSystemLoader

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
        self.go = True
        for book_id in self.books_ids: 
            try:
                first_uuid = requests.get("{base_url}{book_metadata_url}1".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url)).json()['uuid']
                if not first.uuid.ok:
                    pass
            except:
                pass
            lsb_updated = "{},{}".format(first_uuid, ",".join(map(str, self.books_ids)))
            book = {}

            if self.go:
                last_book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=self.books_ids[-1])).json()

            last_mongo_book = self.db.books.find_one({'uuid': last_book_metadata['uuid']})
            
            if last_mongo_book and last_mongo_book['lsb_updated'] == lsb_updated and last_mongo_book['tunnel'] == self.tunnel:
                print("all the same.")
                break

            elif last_mongo_book and last_mongo_book['lsb_updated'] == lsb_updated:
                print("all in mongo. different tunnel")
                for book in self.db.books.find({'lsb_updated': lsb_updated}):
                    book['tunnel'] = self.tunnel
                    self.db.books.save(book)
                break

            book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=book_id)).json()
            mongo_book = self.db.books.find_one({'uuid': book_metadata['uuid']})

            if mongo_book and mongo_book['last_modified'] == book_metadata['last_modified'] and mongo_book['tunnel'] == self.tunnel:
                print("one book is good.")
                self.go = False
                continue

            elif mongo_book and mongo_book['last_modified'] == book_metadata['last_modified']:
                print("one book in mongo. but different tunnel")
                self.go = False
                mongo_book['tunnel'] = self.tunnel
                self.db.books.save(mongo_book)
            else:
                print("new book: {}".format(book_metadata['title'].encode('utf-8')))
                self.go = False
                book['id'] = book_id
                book['lsb_updated'] = lsb_updated
                book['domain'] = self.domain
                book['tunnel'] = self.tunnel
                book['uuid'] = book_metadata['uuid']
                book['last_modified'] = book_metadata['last_modified']
                book['title'] = book_metadata['title']
                book['title_sort'] = book_metadata['title_sort']
                book['authors'] = book_metadata['authors']
                book['formats'] = book_metadata['formats']
                book['pubdate'] = book_metadata['pubdate']
                book['publisher'] = book_metadata['publisher']
                book['format_metadata'] = book_metadata['format_metadata']
                book['identifiers'] = book_metadata['identifiers']
                book['comments'] = book_metadata['comments']
                book['tags'] = book_metadata['tags']
                book['user_metadata'] = book_metadata['user_metadata']
                book['languages'] = book_metadata['languages']
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
            
            try:
                self.total_num = requests.get("{base_url}{total_num_url}".format(base_url=self.base_url, total_num_url=self.total_num_url)).json()['total_num']
                if not self.total_num.ok:
                    continue
            except:
                continue

            self.books_ids_url = 'ajax/search?query=&num={total_num}&sort=last_modified'.format(total_num=self.total_num)
            
            try:
                self.books_ids = requests.get("{base_url}{books_ids_url}".format(base_url=self.base_url, books_ids_url=self.books_ids_url)).json()['book_ids']
                if not self.books_ids:
                    continue
            except:
                continue

            self.book_metadata_url = 'ajax/book/'
            thrd = UrlLibThread(self.books_ids, self.book_metadata_url, self.domain, self.tunnel, self.base_url)
            thrd.start()
            for book in self.db.books.find({'tunnel':self.tunnel}):
                self.all_books.append(simplejson.loads(bjson.dumps(book, default=bjson.default)))

        self.all_search_books = []
        if self.query != "":
            for book in self.all_books:
                if self.query.startswith("authors:"):
                    for boo in book['authors']:
                        pattern_q = self.query.upper()[8:]
                        pattern_b = boo.encode('utf-8').upper()
                        if pattern_b.find(pattern_q) != -1:
                            self.all_search_books.append(simplejson.loads(bjson.dumps(book, default=bjson.default)))

                if self.query.startswith("title:"):
                    pattern_q = self.query.upper()[6:]
                    pattern_b = book['title'].encode('utf-8').upper()
                    if pattern_b.find(pattern_q) != -1:
                        self.all_search_books.append(simplejson.loads(bjson.dumps(book, default=bjson.default)))
 

            self.all_books = self.all_search_books
 
        self.all_books.sort(key=operator.itemgetter('title_sort'))
        authors_key = operator.itemgetter("authors")
        toolbar_authors = sorted(list(set(list(itertools.chain.from_iterable(map(authors_key, self.all_books))))))
        titles_key = operator.itemgetter("title")
        toolbar_titles = sorted(list(set(map(titles_key, self.all_books))))
        
        if self.all_books == []:
            processing_status = " No shared library at the moment. Share your own :)" 
        toolbar_data = {"total_num": len(self.all_books), "authors": toolbar_authors, "titles": toolbar_titles, "query": self.query, "processing": processing_status}
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
        tmpl = ENV.get_template('index.html')
        return tmpl.render()

ENV = Environment(loader=FileSystemLoader('templates'))
base_dir = "/var/www/libraries/"
prefix_url = "http://www"
current_dir = os.path.dirname(os.path.abspath(__file__))
conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(current_dir, 'static'),
                    'tools.staticdir.content_types': {'js': 'application/javascript',
                                                      'css': 'text/css',
                                                      'gif': 'image/gif'
                                                       }}}
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 4321
cherrypy.quickstart(Root(), '/', config=conf)
