import subprocess
import os
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
import pymongo
from jinja2 import Environment, FileSystemLoader

def import_catalog(catalog):
    for book in catalog:
        DB.books.insert(book)

class UrlLibThread(threading.Thread):
    def __init__(self, book_metadata_url, domain, tunnel, base_url):
        threading.Thread.__init__(self)
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

    def insert_new_book(self, book_id, library_uuid, bookk={}):
        book = {}
        if bookk != {}:
            book_metadata = bookk
        else:
            book_metadata = self.get_book_metadata(book_id)
            if not book_metadata:
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
            Db.libraries.update({'library_uuid': library_uuid}, {'$push': {'book_uuids' : book['uuid'], 'books_ids' : book['id']}}, upsert=True)
    
    def insert_new_books(self, new_books_ids, library_uuid):
        Db.new_books_ids_proxy.update({'library_uuid': library_uuid}, {'$set':{'new_books_ids': new_books_ids}}, upsert=True)
        while Db.new_books_ids_proxy.find_one({'library_uuid': library_uuid}, {'new_books_ids': {'$slice': -1}})['new_books_ids'] != []:
            book_id = Db.new_books_ids_proxy.find_one({'library_uuid': library_uuid}, {'new_books_ids':{'$slice': -1}})['new_books_ids'][0]
            Db.new_books_ids_proxy.update({'library_uuid': library_uuid}, {'$pop':{'new_books_ids': 1}})
            self.insert_new_book(book_id, library_uuid)

    def run(self):
        library_uuid = str(uuid.uuid4())
        while Db.books_ids_proxy.find_one({'tunnel': self.tunnel}, {'books_ids': {'$slice': 1}})['books_ids'] != []:
            books_ids = Db.books_ids_proxy.find_one({'tunnel': self.tunnel})['books_ids']
            #books_ids.reverse()
            book_id = Db.books_ids_proxy.find_one({'tunnel': self.tunnel}, {'books_ids':{'$slice':1}})['books_ids'][0]
            book = self.get_book_metadata(book_id)

            if not book:
                return

            Db.books_ids_proxy.update({'tunnel': self.tunnel}, {'$pop': {'books_ids': -1}})
            library = Db.libraries.find_one({'book_uuids': {'$in': [book['uuid']]}})
            if library:
                library_uuid = library['library_uuid']
                if Db.books.find_one({'uuid': book['uuid']})['tunnel'] != self.tunnel:
                    #Db.books.update({'uuid': book['uuid']}, {'$set' : {'tunnel': self.tunnel}}, upsert=False)
                    for ujid in Db.libraries.find({'library_uuid': library_uuid }).distinct('book_uuids'):
                        Db.books.update({'uuid': ujid}, {'$set': {'tunnel': self.tunnel}}, upsert=False, multi=True)

                self.seqs = []
                print("books_ids_proxy: {} {} ; length={}".format(books_ids[0:10], books_ids[-10:],len(books_ids)))
                print("library['books_ids']: {} {}; length={}".format(library['books_ids'][0:10], library['books_ids'][-10:], len(library['books_ids'])))
                lib_books_ids = library['books_ids']
                #lib_books_ids.reverse()
                seqz = self.compare_lists(lib_books_ids, books_ids)
                old_books_ids = list(itertools.chain.from_iterable(seqz))
                print("old_books_ids: {} {}".format(old_books_ids[0:10],old_books_ids[-10:] ))
                lib_new_books_ids = Db.libraries.find_one({'library_uuid' : library_uuid})['books_ids']
                new_books_ids = [book_id for book_id in books_ids if book_id not in set(old_books_ids) or book_id not in set(lib_new_books_ids)]
                print("new_books_ids: {} {}".format(new_books_ids[0:10], new_books_ids[-10:]))
                removed_books_ids = [book_id for book_id in library['books_ids'] if book_id not in set(books_ids)]
                print("removed_books_ids: {}".format(removed_books_ids))
                for book_id in removed_books_ids:
                    book_uuid = Db.books.find_one({'library_uuid' : library_uuid, 'id' : book_id})['uuid']
                    Db.libraries.update({'library_uuid': library_uuid}, {'$pull': {'books_ids' : book_id, 'book_uuids': book_uuid}})
                    Db.books.remove({'uuid': book_uuid})
                if new_books_ids != []:
                    self.insert_new_books(new_books_ids, library_uuid)
                #Db.libraries.update({'library_uuid': library_uuid}, {'$set' : {'books_ids' : books_ids}})
                return
            else:
                self.insert_new_book(book_id, library_uuid, bookk=book)
        return


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
            base_url = '{prefix_url}{tunnel}.{domain}/'.format(prefix_url=PREFIX_URL, tunnel=tunnel, domain=self.domain)
            #total_num = get_total_num(base_url) 
            books_ids = self.get_books_ids(base_url)
            book_metadata_url = 'ajax/book/'

            if books_ids:
                active_tunnels.append(tunnel)
                Db.books_ids_proxy.update({'tunnel': tunnel}, {'$set':{'books_ids': books_ids}}, upsert=True)
                thrd = UrlLibThread(book_metadata_url, self.domain, tunnel, base_url)
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
