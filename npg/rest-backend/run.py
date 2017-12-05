# -*- coding: utf-8 -*-

import os
import re
from uuid import UUID

from eve import Eve
from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Validator

from flask import abort
from flask import request

from bson import ObjectId

# import time
# def timeit(method):
#     def timed(*args, **kw):
#         ts = time.time()
#         result = method(*args, **kw)
#         te = time.time()
#         print('{} {:.2f} ms'.format(method.__name__, (te - ts) * 1000))
#         return result
#     return timed

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
    def __add_kgrams(texts, book_id, library_uuid):
        for text in texts:
            for w in NGRAM_RE.findall(text):
                yield {'ngram': w[:4].lower(),
                       'val': text,
                       'book_id': book_id,
                       'library_uuid': library_uuid}

    authors_ngrams = app.data.driver.db['authors_ngrams']
    titles_ngrams = app.data.driver.db['titles_ngrams']
    tags_ngrams = app.data.driver.db['tags_ngrams']

    ac_authors = []
    ac_titles = []
    ac_tags = []
    for book in books:
        ac_titles.extend(__add_kgrams([book['title']],
                                      book['_id'],
                                      book['library_uuid']))
        ac_authors.extend(__add_kgrams(book['authors'],
                                       book['_id'],
                                       book['library_uuid']))
        ac_tags.extend(__add_kgrams(book['tags'],
                                    book['_id'],
                                    book['library_uuid']))

    return [
        ('authors', authors_ngrams, ac_authors),
        ('title', titles_ngrams, ac_titles),
        ('tags', tags_ngrams, ac_tags)
    ]


def delete_4grams(library_uuid=None, book_id=None):
    for n in ['authors_ngrams', 'titles_ngrams', 'tags_ngrams']:
        if library_uuid:
            app.data.driver.db[n].remove({'library_uuid': library_uuid})
        elif book_id:
            app.data.driver.db[n].remove({'book_id': book_id})


def add_4grams(library_uuid=None, book_id=None, book_items=None):
    books = app.data.driver.db['books']

    if library_uuid:
        b = books.find({'library_uuid': library_uuid})
    elif book_id:
        b = books.find({'_id': book_id})
    elif book_items:
        b = book_items

    for _, coll, lst in generate_4grams(b):
        try:
            r = coll.insert_many(lst, ordered=False)
            print("@ADDING 4 GRAMS: {}, {}".format(lst, r.raw_result))
        except Exception as e:
            print(e)

    print("FINISHED ADDING 4GRAMS!")


def insert_ngrams(items):
    check_library_secret(items[0]['library_uuid'])
    add_4grams(book_items=items)


def check_deleted_item_books(item):
    # print("@DELETE_ITEM_BOOKS arg#item {}".format(item))
    # print("@DELETE_ITEM_BOOKS headers {}".format(request.headers))
    check_library_secret(item['library_uuid'])

    delete_4grams(book_id=item["_id"])
    print("@DELETE_ITEM_BOOKS ngrams deleted....")


def check_update_books(updates, original):
    print("@UPDATE_BOOKS arg#updates: {}, arg#original: {}".format(updates,
                                                                   original))
    print("@UPDATE_BOOKS headers {}".format(request.headers))
    check_library_secret(original['library_uuid'])
    print("@UPDATE secret passed the test...")
    delete_4grams(book_id=original['_id'])
    add_4grams(book_id=original['_id'])


def check_insert_books(items):
    check_library_secret(items[0]['library_uuid'])
    print("@INSERT books secret passed the test...")
    insert_ngrams(items)


def cleanup_library(item):
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
        print("@DELETE_ITEM_LIBRARIES delete related books... {}".format(
            r.raw_result))

    delete_4grams(library_uuid=item['_id'])
    print("@DELETE_ITEM_LIBRARIES ngrams deleted...")


def check_update_libraries(updates, original):
    print("@UPDATE_LIBRARIES arg#updates: {}, arg#original: {}".format(
        updates, original))
    print("@UPDATE_LIBRARIES headers {}".format(request.headers))
    if '_id' in updates:
        abort(403)
    check_library_secret(original['_id'])
    print("@UPDATE_LIBRARIES secret passed the test...")


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


def pre_req(res, req):
    if request.headers.get('Library-Encoding') == 'zlib':
        import zlib
        request.data = zlib.decompress(req.data).decode('utf-8')
        request._cached_data = request.data


app.on_pre_POST += pre_req

app.on_insert_libraries += check_insert_libraries
app.on_update_libraries += check_update_libraries
app.on_delete_item_libraries += cleanup_library

app.on_update_books += check_update_books
app.on_deleted_item_books += check_deleted_item_books

app.on_insert_add_ooks += check_insert_books
app.on_inserted_add_books += insert_ngrams


if __name__ == '__main__':
    # before running it in production check threaded=True and how to run it with uwsgi
    app.run(host=host, port=port, threaded=True, debug=True)
