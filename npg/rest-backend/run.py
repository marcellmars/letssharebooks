# -*- coding: utf-8 -*-

import os
from uuid import UUID

from eve import Eve
from eve.io.base import BaseJSONEncoder
from eve.io.mongo import Validator

from flask import current_app as app
from flask import abort
from flask import request

from bson import ObjectId


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


# def make_ngrams(word, min_size=4):
#     word += " "
#     length = len(word)
#     size_range = range(4, min(length, 5) + 1)
#     return list(set(
#         word[i:i + size]
#         for size in size_range
#         for i in range(0, max(0, length - size) + 1)
#     ))


# def add_ngrams(books):
#     authors_ngrams = app.data.driver.db['authors_ngrams']
#     for book in books:
#         for author in book['authors']:
#             for word in author.split(" "):
#                 if len(word) < 3:
#                     continue
#                 ngrams = make_ngrams(word.lower())
#                 for ngr in ngrams:
#                     r = authors_ngrams.update_many({'ngram': ngr},
#                                                    {'$addToSet': {'authors': author}},
#                                                    upsert=True)
#                     print("NGRAMS UPDATE_MANY: {}".format(r))
def add_4grams(books):
    authors_ngrams = app.data.driver.db['authors_ngrams']
    titles_ngrams = app.data.driver.db['titles_ngrams']
    for book in books:
        for word in book['title'].split(" "):
            if len(word) < 3:
                continue
            elif len(word) == 3:
                word += " "
            r = titles_ngrams.update_many({'ngram': word[:4].lower()},
                                          {'$addToSet': {'titles': book['title']}},
                                          upsert=True)

        for author in book['authors']:
            for word in author.split(" "):
                if len(word) < 3:
                    continue
                elif len(word) == 3:
                    word += " "
                r = authors_ngrams.update_many({'ngram': word[:4].lower()},
                                               {'$addToSet': {'authors': author}},
                                               upsert=True)
                # print("AUTHORS 4GRAMS UPDATE_MANY: {}".format(r))
    print("FINISHED 4GRAMS!")


def check_libraries_secrets(library_uuid, library_secret):
    libraries_secrets = app.data.driver.db['libraries_secrets']
    c = libraries_secrets.find_one({library_uuid: library_secret})
    return c


def check_insert_books(items):
    if 'Library-Uuid' in request.headers and 'Library-Secret' in request.headers:
        if check_libraries_secrets(request.headers['Library-Uuid'], request.headers['Library-Secret']):
            print("@INSERT books secret passed the test...")
        else:
            abort(403)
    else:
        abort(403)


def check_delete_item_books(item):
    print("@DELETE arg#item {}".format(item))
    print("@DELETE headers {}".format(request.headers))
    if 'Library-Uuid' in request.headers and 'Library-Secret' in request.headers:
        if check_libraries_secrets(request.headers['Library-Uuid'], request.headers['Library-Secret']):
            print("@DELETE {}".format(item))
        else:
            abort(403)
    else:
        abort(403)


def check_insert_libraries(items):
    print("@INSERT libraries arg#items: {}".format(items))
    libraries_secrets = app.data.driver.db['libraries_secrets']
    if 'Library-Uuid' in request.headers and 'Library-Secret' in request.headers:
        c = libraries_secrets.insert_one({request.headers['Library-Uuid']: request.headers['Library-Secret']}).inserted_id
        print("inserted_id: {}".format(c))
    else:
        abort(403)


def check_delete_item_libraries(item):
    print("@DELETE arg#item {}".format(item))
    print("@DELETE headers {}".format(request.headers))
    if 'Library-Uuid' in request.headers and 'Library-Secret' in request.headers:
        c = check_libraries_secrets(request.headers['Library-Uuid'], request.headers['Library-Secret'])
        if c:
            libraries_secrets = app.data.driver.db['libraries_secrets']
            libraries_secrets.remove({request.headers['Library-Uuid']: request.headers['Library-Secret']})
            print("@DELETE {}".format(item))
        else:
            abort(403)
    else:
        abort(403)


def check_update(updates, original):
    print("@UPDATE arg#updates: {}, arg#original: {}".format(updates, original))
    print("@UPDATE headers {}".format(request.headers))
    if 'Library-Uuid' in request.headers and 'Library-Secret' in request.headers:
        if check_libraries_secrets(request.headers['Library-Uuid'], request.headers['Library-Secret']):
            print("@UPDATE secret passed the test...")
        else:
            abort(403)
    else:
        abort(403)


app.on_insert_libraries += check_insert_libraries
app.on_update_libraries += check_update
app.on_delete_item_libraries += check_delete_item_libraries

app.on_insert_books += check_insert_books
app.on_update_books += check_update
app.on_delete_item_books += check_delete_item_books
app.on_inserted_books += add_4grams

if __name__ == '__main__':
    ## before running it in production check threaded=True and how to run it with uwsgi
    app.run(host=host, port=port, threaded=True, debug=True)
