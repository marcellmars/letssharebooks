# -*- coding: utf-8 -*-

import os
from uuid import UUID

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
    app.data.driver.db.authors_ngrams.create_index([('ngram', 1), ('val', 1)], unique=True)
    app.data.driver.db.titles_ngrams.create_index([('ngram', 1), ('val', 1)], unique=True)
    app.data.driver.db.tags_ngrams.create_index([('ngram', 1), ('val', 1)], unique=True)


def add_4grams(books):
    authors_ngrams = app.data.driver.db['authors_ngrams']
    titles_ngrams = app.data.driver.db['titles_ngrams']
    tags_ngrams = app.data.driver.db['tags_ngrams']

    ac_authors = []
    ac_titles = []
    ac_tags = []
    for book in books:
        for word in book['title'].split():
            if len(word) < 3:
                continue
            elif len(word) == 3:
                word += " "
            ac_titles.append({'ngram': word[:4].lower(), 'val': book['title']})

        for author in book['authors']:
            for word in author.split():
                if len(word) < 3:
                    continue
                elif len(word) == 3:
                    word += " "
                ac_authors.append({'ngram': word[:4].lower(), 'val': author})

        for tag in book['tags']:
            for word in tag.split():
                if len(word) < 3:
                    continue
                elif len(word) == 3:
                    word += " "
                ac_tags.append({'ngram': word[:4].lower(), 'val': tag})

    ngrams_list = [
        (authors_ngrams, ac_authors),
        (titles_ngrams, ac_titles),
        (tags_ngrams, ac_tags)
    ]

    for coll, lst in ngrams_list:
        try:
            coll.insert_many(list(lst), ordered=False)
        except Exception as e:
            print(e)

    print("FINISHED 4GRAMS!")


def check_libraries_secrets(library_uuid, library_secret):
    if library_secret == MASTER_SECRET:
        return True
    libraries_secrets = app.data.driver.db['libraries_secrets']
    c = libraries_secrets.find_one({library_uuid: library_secret})
    return c


def check_insert_books(items):
    if 'Library-Secret' in request.headers:
        if check_libraries_secrets(items[0]['library_uuid'],
                                   request.headers['Library-Secret']):
            print("@INSERT books secret passed the test...")
        else:
            abort(403)
    else:
        abort(403)


def check_delete_item_books(item):
    print("@DELETE arg#item {}".format(item))
    print("@DELETE headers {}".format(request.headers))
    if 'Library-Secret' in request.headers:
        if check_libraries_secrets(item['library_uuid'],
                                   request.headers['Library-Secret']):
            print("@DELETE {}".format(item))
        else:
            abort(403)
    else:
        abort(403)


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
    if 'Library-Secret' in request.headers:
        c = check_libraries_secrets(item['_id'],
                                    request.headers['Library-Secret'])
        if c:
            libraries_secrets = app.data.driver.db['libraries_secrets']
            libraries_secrets.remove({
                item['_id']: request.headers['Library-Secret']
            })
            print("@DELETE_ITEM_LIBRARIES {}".format(item))

            books = app.data.driver.db['books']

            if books.count():
                r = books.remove({'library_uuid': item['_id']})
                print("@DELETE_ITEM_LIBRARIES delete related books... {}".format(r.raw_result))

        else:
            abort(403)
    else:
        abort(403)


def check_update_libraries(updates, original):
    print("@UPDATE_LIBRARIES arg#updates: {}, arg#original: {}".format(updates, original))
    print("@UPDATE_LIBRARIES headers {}".format(request.headers))
    if 'Library-Secret' in request.headers:
        if check_libraries_secrets(original['_id'],
                                   request.headers['Library-Secret']):
            print("@UPDATE secret passed the test...")
        else:
            abort(403)
    else:
        abort(403)


def check_update_books(updates, original):
    print("@UPDATE_BOOKS arg#updates: {}, arg#original: {}".format(updates, original))
    print("@UPDATE_BOOKS headers {}".format(request.headers))
    if 'Library-Secret' in request.headers:
        if check_libraries_secrets(original['library_uuid'],
                                   request.headers['Library-Secret']):
            print("@UPDATE secret passed the test...")
        else:
            abort(403)
    else:
        abort(403)


def update_books_on_updated(updates, original):
    print("@UPDATE_BOOKS_ON_UPDATED_LIBRARIES arg#updates: {}, arg#original: {}".format(updates, original))
    print("@UPDATE_BOOKS_ON_UPDATED_LIBRARIES headers {}".format(request.headers))
    if 'Library-Secret' in request.headers:
        if check_libraries_secrets(original['_id'],
                                   request.headers['Library-Secret']):
            print("@UPDATE_BOOKS_ON_UPDATED secret passed the test...")
            if 'presence' in updates:
                books = app.data.driver.db['books']
                r = books.update_many({'library_uuid': original['_id']},
                                      {"$set": {'presence': updates['presence']}})
                print("@UPDATE_BOOKS_ON_UPDATED_LIBRARIES set new presence in books {}".format(r.raw_result))
                if updates['presence'] == 'off':
                    titles_off = [(book['title'], book['presence'])
                                  for book in books.find({'library_uuid': original['_id']})]
                    titles_on = [(book['title'], book['presence'])
                                 for book in books.find({'library_uuid': {'$nin': [original['_id']]},
                                                         'presence': 'on'})]
                    print("TITLES OFF: {}".format(titles_off))
                    print("TITLES ON: {}".format(titles_on))
        else:
            abort(403)
    else:
        abort(403)


app.on_insert_libraries += check_insert_libraries
app.on_update_libraries += check_update_libraries
app.on_updated_libraries += update_books_on_updated
app.on_delete_item_libraries += check_delete_item_libraries

app.on_insert_books += check_insert_books
app.on_update_books += check_update_books
app.on_delete_item_books += check_delete_item_books
app.on_inserted_books += add_4grams

if __name__ == '__main__':
    # before running it in production check threaded=True and how to run it with uwsgi
    app.run(host=host, port=port, threaded=True, debug=True)
