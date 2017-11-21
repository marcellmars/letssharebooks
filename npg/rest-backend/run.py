# -*- coding: utf-8 -*-

import os
import re
from uuid import UUID
import itertools

from eve import Eve
from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Validator

from flask import abort
from flask import request

from bson import ObjectId


# TODO: should be changed in production.
MASTER_SECRET = "874a7f15-0c02-473e-ba2c-c1ef937b9a5c"


class UUIDValidator(Validator):
    def _validate_type_uuid(self, key, value):
        try:
            UUID(value)
        except ValueError:
            pass


class UUIDEncoder(BaseJSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super(UUIDEncoder, self).default(obj)


if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
    host = '0.0.0.0'
else:
    port = 5000
    host = '127.0.0.1'


app = Eve(json_encoder=UUIDEncoder, validator=UUIDValidator)

with app.app_context():
    app.data.driver.db.authors_ngrams.create_index(
        [('ngram', 1), ('val', 1)], unique=True)
    app.data.driver.db.titles_ngrams.create_index(
        [('ngram', 1), ('val', 1)], unique=True)
    app.data.driver.db.tags_ngrams.create_index(
        [('ngram', 1), ('val', 1)], unique=True)


def check_library_secret(library_uuid):
    library_secret = request.headers.get('Library-Secret')
    if library_secret:
        if library_secret == MASTER_SECRET:
            return True
        libraries_secrets = app.data.driver.db['libraries_secrets']
        c = libraries_secrets.find_one({library_uuid: library_secret})
        if c:
            return c
    abort(403)


# 4-letter words OR 3-letter words followed by space (unless at the
# end of the string)
NGRAM_RE = re.compile('\w{4,}|\w{3}\s|\w{3}$')


def generate_4grams(books):
    def __add_kgrams(texts):
        for text in texts:
            for w in NGRAM_RE.findall(text):
                yield {'ngram': w[:4].lower(), 'val': text}

    authors_ngrams = app.data.driver.db['authors_ngrams']
    titles_ngrams = app.data.driver.db['titles_ngrams']
    tags_ngrams = app.data.driver.db['tags_ngrams']

    ac_authors = []
    ac_titles = []
    ac_tags = []
    for book in books:
        ac_titles.extend(__add_kgrams([book['title']]))
        ac_authors.extend(__add_kgrams(book['authors']))
        ac_tags.extend(__add_kgrams(book['tags']))

    return [
        ('authors', authors_ngrams, ac_authors),
        ('title', titles_ngrams, ac_titles),
        ('tags', tags_ngrams, ac_tags)
    ]


def delete_4grams(library_uuid):
    books = app.data.driver.db['books']

    # titles
    titles_off = {book['title']
                  for book in books.find({'library_uuid': library_uuid})}
    titles_on = {book['title']
                 for book in books.find({'library_uuid': {'$nin': [library_uuid]},
                                         'presence': 'on'})}
    titles = titles_off - titles_on

    # authors
    authors_off = (book['authors']
                   for book in books.find({'library_uuid': library_uuid}))
    authors_off = set(itertools.chain.from_iterable(authors_off))

    authors_on = (book['authors']
                  for book in books.find({'library_uuid':
                                          {'$nin': [library_uuid]},
                                          'presence': 'on'}))
    authors_on = set(itertools.chain.from_iterable(authors_on))
    authors = authors_off - authors_on

    # tags
    tags_off = (book['tags']
                for book in books.find({'library_uuid': library_uuid}))
    tags_off = set(itertools.chain.from_iterable(tags_off))

    tags_on = (book['tags']
               for book in books.find({'library_uuid': {'$nin': [library_uuid]},
                                       'presence': 'on'}))
    tags_on = set(itertools.chain.from_iterable(tags_on))
    tags = tags_off - tags_on

    books = []
    books.append({'title': '', 'authors': authors, 'tags': tags})
    for title in titles:
        books.append({'title': title, 'authors': [], 'tags': []})

    for _, coll, lst in generate_4grams(books):
        try:
            for l in lst:
                r = coll.delete_one(l)
                print("@DELETE 4 GRAMS: {}, {}".format(l, r.raw_result))
        except Exception as e:
            print(e)
    print("FINISHED DELETING 4GRAMS!")


def add_4grams(library_uuid):
    books = app.data.driver.db['books']
    b = books.find({'library_uuid': library_uuid})
    for _, coll, lst in generate_4grams(b):
        try:
            r = coll.insert_many(lst, ordered=False)
            print("@ADDING 4 GRAMS: {}, {}".format(lst, r.raw_result))
        except Exception as e:
            print(e)
    print("FINISHED ADDING 4GRAMS!")


def check_insert_books(items):
    check_library_secret(items[0]['library_uuid'])
    print("@INSERT books secret passed the test...")


def check_delete_item_books(item):
    print("@DELETE_ITEM_BOOKS arg#item {}".format(item))
    print("@DELETE_ITEM_BOOKS headers {}".format(request.headers))
    check_library_secret(item['library_uuid'])

    books = app.data.driver.db['books']
    for attr_name, coll, lst in generate_4grams([item]):
        # set of items to delete
        items_del = set((i['val'] for i in lst))

        # select all values for corresponding ngrams
        q = [{attr_name: i['val']} for i in lst]

        # take all existing values for corresponding attribute
        if attr_name == 'titles':
            items_existing = set((b['title'] for b in books.find(
                {'presence': 'on', '$or': q})))
        elif attr_name == 'authors':
            items_existing = set((a for b in books.find(
                {'presence': 'on', '$or': q}) for a in b['authors']))
        elif attr_name == 'tags':
            items_existing = set((a for b in books.find(
                {'presence': 'on', '$or': q}) for a in b['tags']))

        # remove only those that are not currently active
        to_del = items_del - items_existing
        for i in lst:
            if i['val'] in to_del:
                try:
                    coll.delete_one(i)
                except Exception as e:
                    print(e)

    print("FINISHED DELETING 4GRAMS!")

    print("@DELETE {}".format(item))


def check_insert_libraries(items):
    print("@INSERT_LIBRARIES arg#items: {}".format(items))
    libraries_secrets = app.data.driver.db['libraries_secrets']
    if 'Library-Secret' in request.headers:
        c = libraries_secrets.insert_one({
            items[0]['_id']: request.headers['Library-Secret']
        })
        print("@INSERT_LIBRARIES: {}".format(c.inserted_id))
    else:
        abort(403)


def check_delete_item_libraries(item):
    print("@DELETE_ITEM_LIBRARIES arg#item {}".format(item))
    print("@DELETE_ITEM_LIBRARIES headers {}".format(request.headers))
    check_library_secret(item['_id'])

    libraries_secrets = app.data.driver.db['libraries_secrets']
    libraries_secrets.remove({
        item['_id']: request.headers['Library-Secret']
    })
    print("@DELETE_ITEM_LIBRARIES {}".format(item))
    books = app.data.driver.db['books']
    if books.count():
        r = books.remove({'library_uuid': item['_id']})
        delete_4grams(item['_id'])
        print("@DELETE_ITEM_LIBRARIES delete related books... {}".format(
            r.raw_result))


def check_update_libraries(updates, original):
    print("@UPDATE_LIBRARIES arg#updates: {}, arg#original: {}".format(
        updates, original))
    print("@UPDATE_LIBRARIES headers {}".format(request.headers))
    check_library_secret(original['_id'])
    print("@UPDATE secret passed the test...")


def check_update_books(updates, original):
    print("@UPDATE_BOOKS arg#updates: {}, arg#original: {}".format(updates, original))
    print("@UPDATE_BOOKS headers {}".format(request.headers))
    check_library_secret(original['library_uuid'])
    print("@UPDATE secret passed the test...")


def update_books_on_updated(updates, original):
    print("@UPDATE_BOOKS_ON_UPDATED_LIBRARIES arg#updates: {}, arg#original: {}".format(updates, original))
    print("@UPDATE_BOOKS_ON_UPDATED_LIBRARIES headers {}".format(request.headers))
    check_library_secret(original['_id'])
    print("@UPDATE_BOOKS_ON_UPDATED secret passed the test...")
    books = app.data.driver.db['books']
    if 'presence' in updates:
        # r = books.update_many({'library_uuid': original['_id']},
        #                       {"$set": {'presence': updates['presence']}})
        # print("@UPDATE_BOOKS_ON_UPDATED_LIBRARIES set new presence in books {}".format(r.raw_result))
        if updates['presence'] == 'off':
            delete_4grams(original['_id'])
            print("@UPDATE_BOOKS_ON_UPDATED delete 'off' 4grams ...")
        elif updates['presence'] == 'on':
            add_4grams(original['_id'])
            print("@UPDATE_BOOKS_ON_UPDATED add 'on' 4grams ...")

    # for l in ['librarian', 'library_url']:
    #     if l in updates:
    #         r = books.update_many({'library_uuid': original['_id']},
    #                               {"$set": {l: updates[l]}})


def pre_req(res, req):
    if request.headers.get('Library-Encoding') == 'zlib':
        import zlib
        request.data = zlib.decompress(req.data).decode('utf-8')
        request._cached_data = request.data


app.on_pre_POST += pre_req

app.on_insert_libraries += check_insert_libraries
app.on_update_libraries += check_update_libraries
app.on_updated_libraries += update_books_on_updated
app.on_delete_item_libraries += check_delete_item_libraries

app.on_insert_books += check_insert_books
app.on_update_books += check_update_books
app.on_deleted_item_books += check_delete_item_books
app.on_inserted_books += add_4grams


if __name__ == '__main__':
    # before running it in production check threaded=True and how to run it with uwsgi
    app.run(host=host, port=port, threaded=True, debug=True)
