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
import uuid
import random
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
        self.seqs = []
    
    def compare_lists(self, a, b):
        def loop_it(a, b):
            if len(a) <= 0 or len(b) <=0:
                return
            self.rez = [i for i,j in zip(a,b) if i == j]
            self.seqs.append(self.rez)
            loop_it(a[len(self.rez)+1:], b[len(self.rez):])
        #a.reverse()
        #b.reverse()
        loop_it(a,b)
        #self.seqs.reverse()
        return self.seqs

    def get_book_metadata(self, book_id):
        try:
            book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=book_id))
            if book_metadata.ok:
                return book_metadata.json()
            else:
                return False

        except requests.exceptions.RequestException as e:
            return False

    def insert_new_book(self, book_id, library_uuid):
        book = {}
        book_metadata = self.get_book_metadata(book_id)
        
        if not book_metadata:
            print("lock: {}".format(Db.lock.find_one({'library_uuid': self.tunnel + self.books_ids})['lock']))
            Db.lock.update({'library_uuid': self.tunnel + self.books_ids}, {'$set': {'lock': 'False'}})
            return
       
        book['id'] = book_id
        book['domain'] = self.domain
        book['tunnel'] = self.tunnel
        book['library_uuid'] = library_uuid
        
        if 'last_modified' in book_metadata:
            book['last_modified'] = book_metadata['last_modified']
        else:
            book['last_modified'] = book_metadata['timestamp']
        
        keys = ['uuid', 'title', 'title_sort', 'authors', 'formats', 'pubdate', 'publisher', 'format_metadata', 'idetifiers', 'comments', 'tags', 'user_metadata', 'languages']
        for key in keys:
            if key in book_metadata:
                book[key] = book_metadata[key]
        
        Db.books.update({'uuid': book_metadata['uuid']}, book, upsert=True)
        if book['uuid'] not in Db.libraries.distinct('book_uuids'):
            Db.libraries.update({'library_uuid': library_uuid}, {'$push': {'book_uuids' : book['uuid'], 'uploaded_books_ids' : book['id']}}, upsert=True)
    
    def insert_new_books(self, new_books_ids, library_uuid):
        Db.libraries.update({'library_uuid': library_uuid}, {'$set':{'books_ids': new_books_ids}}, upsert=True)
        Db.lock.update({'library_uuid': self.tunnel + self.books_ids}, {'$set': {'lock': 'True'}}, upsert=True)
        print("lock: {}".format(Db.lock.find_one({'library_uuid': self.tunnel + self.books_ids})['lock']))
        
        for book_id in new_books_ids:
            self.insert_new_book(book_id, library_uuid)
        
        Db.lock.update({'library_uuid': self.tunnel + self.books_ids}, {'$set': {'lock': 'False'}})


    def run(self):
        try:
            if Db.lock.find_one({'library_uuid': self.tunnel + self.books_ids})['lock'] == 'True':
                return
        except:
            Db.lock.update({'library_uuid': self.tunnel + self.books_ids}, {'$set': {'lock': 'False'}})

        for book_id in range(4):
            book_id = random.randint(0, len(self.books_ids))
            book = self.get_book_metadata(book_id)

            if not book:
                return
            
            libraries = [library for library in Db.libraries.find({'book_uuids': {'$in': [book['uuid']]}})]
            print("libraries: {}".format(libraries))
            if libraries:
                for library in libraries:
                    Db.libraries.update({'library_uuid': libraries[0]['library_uuid']}, {'$addToSet': {'books_ids': {'$each': library['books_ids']}, 'book_uuids': {'$each': library['book_uuids']}}}, upsert=False)
                    if library['library_uuid'] != libraries[0]['library_uuid']:
                        Db.libraries.remove({'library_uuid': library['library_uuid']})

                library_uuid = libraries[0]['library_uuid']
                if Db.books.find_one({'uuid': book['uuid']})['tunnel'] != self.tunnel:
                    #Db.books.update({'uuid': book['uuid']}, {'$set' : {'tunnel': self.tunnel}}, upsert=False)
                    for ujid in Db.libraries.find({'library_uuid': library_uuid }).distinct('book_uuids'):
                        Db.books.update({'uuid': ujid}, {'$set': {'tunnel': self.tunnel}}, upsert=False, multi=True)

                self.seqs = []
                print("books_ids_proxy: {} {} ; length={}".format(self.books_ids[0:10], self.books_ids[-10:],len(self.books_ids)))
                lib_books_ids = library['books_ids']
                print("library['books_ids']: {} {}; length={}".format(library['books_ids'][0:10], library['books_ids'][-10:], len(library['books_ids'])))
                #lib_books_ids.reverse()
                seqz = self.compare_lists(lib_books_ids, self.books_ids)
                old_books_ids = list(itertools.chain.from_iterable(seqz))
                print("old_books_ids: {} {}".format(old_books_ids[0:10], old_books_ids[-10:]))
                lib_new_books_ids = Db.libraries.find_one({'library_uuid': library_uuid})['uploaded_books_ids']
                print("lib_new_books_ids: {} {}".format(lib_new_books_ids[0:10], lib_new_books_ids[-10:]))
                new_books_ids = [book_id for book_id in self.books_ids if book_id not in set(old_books_ids) or book_id not in set(lib_new_books_ids)]
                print("new_books_ids: {} {}".format(new_books_ids[0:10], new_books_ids[-10:]))
                removed_books_ids = [book_id for book_id in library['books_ids'] if book_id not in set(self.books_ids)]
                print("removed_books_ids: {}".format(removed_books_ids))
                for book_id in removed_books_ids:
                    book_uuid = Db.books.find_one({'library_uuid' : library_uuid, 'id' : book_id})['uuid']
                    Db.libraries.update({'library_uuid': library_uuid}, {'$pull': {'uploaded_books_ids' : book_id, 'book_uuids': book_uuid, 'books_ids': book_id}})
                    Db.books.remove({'uuid': book_uuid})
                if new_books_ids != []:
                    self.insert_new_books(new_books_ids, library_uuid)
                Db.libraries.update({'library_uuid': library_uuid}, {'$set' : {'books_ids' : self.books_ids}})
                break
        print("get new books!")
        self.insert_new_books(self.books_ids, str(uuid.uuid4()))


class JSONBooks:
    def __init__(self, domain = "web.dokr"):
    #def __init__(self, domain = "memoryoftheworld.org"): ### production
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
                Db.books_ids_proxy.update({'tunnel': tunnel}, {'$set':{'books_ids': books_ids}}, upsert=True)
                thrd = UrlLibThread("".join(map(str, books_ids)), book_metadata_url, self.domain, tunnel, base_url)
                thrd.start()

        result = []
        mongo_result = Db.books.find({'tunnel': {"$in" : active_tunnels}})
        total_num = mongo_result.count()
        if offset > total_num:
            offset = total_num
        toolbar_authors = sorted(mongo_result.distinct('authors'))
        toolbar_titles = sorted(mongo_result.distinct('title_sort'))
        if total_num == 0:
            processing_status = " No shared library at the moment. Share your own :)" 

        toolbar_data = {"total_num": total_num, "authors": toolbar_authors, "titles": toolbar_titles, "query": query, "processing": processing_status}

        if query != "":
            if query.startswith("authors:"):
                pattern = query.upper()[8:]
                result =  [simplejson.loads(bjson.dumps(book, default=bjson.default)) for book in Db.books.find({"authors":{"$regex": pattern, "$options": 'i'}, 'tunnel' : {"$in" : active_tunnels}})]
                toolbar_data['total_num'] = len(result)
                result = result[start:end]
                result.append(toolbar_data)
                return result
            elif query.startswith("title:"):
                pattern = query.upper()[6:]
                result = [simplejson.loads(bjson.dumps(book, default=bjson.default)) for book in Db.books.find({"title_sort":{"$regex": pattern, "$options": 'i'}, 'tunnel' : {"$in" : active_tunnels}})]
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
#Mongo_client = MongoClient('localhost', 27017) ### production
Db = Mongo_client.letssharebooks

Current_dir = os.path.dirname(os.path.abspath(__file__))
Env = Environment(loader=FileSystemLoader('{}/templates'.format(Current_dir)))
Prefix_url = "http://www"
#Prefix_url = "https://www" ### production
Conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(Current_dir, 'static'),
                    'tools.staticdir.content_types': {'js': 'application/javascript',
                                                      'css': 'text/css',
                                                      'gif': 'image/gif'
                                                       }}}
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.server.socket_port = 4321
cherrypy.quickstart(Root(), '/', config=Conf)
