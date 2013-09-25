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

            last_mongo_book = Db.books.find_one({'uuid': last_book_metadata['uuid']})
            
            if last_mongo_book and last_mongo_book['lsb_updated'] == lsb_updated and last_mongo_book['tunnel'] == self.tunnel:
                print("all the same.")
                break

            elif last_mongo_book and last_mongo_book['lsb_updated'] == lsb_updated:
                print("all in mongo. different tunnel")
                for book in Db.books.find({'lsb_updated': lsb_updated}):
                    book['tunnel'] = self.tunnel
                    Db.books.save(book)
                break

            book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=book_id)).json()
            mongo_book = Db.books.find_one({'uuid': book_metadata['uuid']})

            if mongo_book and mongo_book['last_modified'] == book_metadata['last_modified'] and mongo_book['tunnel'] == self.tunnel:
                print("one book is good.")
                self.go = False
                continue

            elif mongo_book and mongo_book['last_modified'] == book_metadata['last_modified']:
                print("one book in mongo. but different tunnel")
                self.go = False
                mongo_book['tunnel'] = self.tunnel
                Db.books.save(mongo_book)
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
                Db.books.insert(book)
        return
 

class JSONBooks:
    def __init__(self, domain = "web.dokr"):
        self.domain = domain

    def get_tunnel_ports(self, login="tunnel"):
        uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
        return subprocess.check_output(["/usr/local/bin/get_tunnel_ports.sh", uid]).split()

    def get_total_num(self, base_url):
        total_num_url = 'ajax/search?query='
        try:
            total_num_request = requests.get("{base_url}{total_num_url}".format(base_url=base_url, total_num_url=total_num_url))
            if total_num_request.ok:
                return total_num_request.json()['total_num']
            else:
                return False

        except requests.exceptions.RequestException as e:
            return False

    def get_books_ids(self, base_url, total_num=1000000):
        books_ids_url = 'ajax/search?query=&num={total_num}&sort=last_modified'.format(total_num=total_num)
        try:
            books_ids_request = requests.get("{base_url}{books_ids_url}".format(base_url=base_url, books_ids_url=books_ids_url))
            if books_ids_request.ok:
                return books_ids_request.json()['book_ids']
            else:
                return False

        except requests.exceptions.RequestException as e:
            return False

    def get_metadata(self, start, offset, query):
        processing_status = ""
        end = start + offset
        all_books = []
        active_tunnels = []

        for tunnel in self.get_tunnel_ports():
            base_url = '{prefix_url}{tunnel}.{domain}/'.format(prefix_url=Prefix_url, tunnel=tunnel, domain=self.domain)
            #total_num = get_total_num(base_url) 
            books_ids = self.get_books_ids(base_url)
            book_metadata_url = 'ajax/book/' 

            if books_ids:
                active_tunnels.append(tunnel)
                thrd = UrlLibThread(books_ids, book_metadata_url, self.domain, tunnel, base_url)
                thrd.start()

        result = []
        mongo_result = Db.books.find({'tunnel': {"$in" : active_tunnels}})
        total_num = mongo_result.count()
        toolbar_authors = sorted(mongo_result.distinct('authors'))
        toolbar_titles = sorted(mongo_result.distinct('title_sort'))
        if total_num == 0:
            processing_status = " No shared library at the moment. Share your own :)" 

        toolbar_data = {"total_num": total_num, "authors": toolbar_authors, "titles": toolbar_titles, "query": query, "processing": processing_status}

        if query != "":
            if query.startswith("authors:"):
                pattern = query.upper()[8:]
                result =  [simplejson.loads(bjson.dumps(book, default=bjson.default)) for book in Db.books.find({"authors":{"$regex": pattern, "$options": 'i'}})]
                toolbar_data['total_num'] = len(result)
                result = result[start:end]
                result.append(toolbar_data)
                return result
            elif query.startswith("title:"):
                pattern = query.upper()[6:]
                result = [simplejson.loads(bjson.dumps(book, default=bjson.default)) for book in Db.books.find({"title":{"$regex": pattern, "$options": 'i'}})]
                toolbar_data['total_num'] = len(result)
                result = result[start:end]
                result.append(toolbar_data)
                return result
            else:
                pattern = query.upper()
                result = [simplejson.loads(bjson.dumps(book, default=bjson.default)) for book in Db.books.find({"$or": [{"title": {"$regex": ".*{}.*".format(pattern), "$options": 'i'}}, {"authors":{"$regex":".*{}.*".format(pattern), "$options": 'i'}}, {"comments":{"$regex":".*{}.*".format(pattern), "$options": 'i'}}, {"tags":{"$regex":".*{}.*".format(pattern), "$options": 'i'}}, {"publisher":{"$regex":".*{}.*".format(pattern), "$options": 'i'}}, {"identifiers":{"$regex":".*{}.*".format(pattern), "$options": 'i'}}]})]
                toolbar_data['total_num'] = len(result)
                result = result[start:end]
                result.append(toolbar_data)
                return result

        result = [simplejson.loads(bjson.dumps(book, default=bjson.default)) for book in mongo_result.sort("title_sort", 1).skip(start).limit(offset)]
        result.append(toolbar_data)
        return result

class Root(object):
 
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def render_page(self):
        json_books = JSONBooks()
        json_request = cherrypy.request.json
        return json_books.get_metadata(json_request['start'], json_request['offset'], json_request['query'].encode('utf-8'))

    @cherrypy.expose
    def index(self):
        tmpl = Env.get_template('index.html')
        return tmpl.render()

Mongo_client = MongoClient('172.17.42.1', 49153)
Db = Mongo_client.letssharebooks

Env = Environment(loader=FileSystemLoader('templates'))
Prefix_url = "http://www"
Current_dir = os.path.dirname(os.path.abspath(__file__))
Conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(Current_dir, 'static'),
                    'tools.staticdir.content_types': {'js': 'application/javascript',
                                                      'css': 'text/css',
                                                      'gif': 'image/gif'
                                                       }}}
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 4321
cherrypy.quickstart(Root(), '/', config=Conf)
