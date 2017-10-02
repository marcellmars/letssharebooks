# -*- coding: utf-8 -*-

import os
from eve import Eve
from flask import current_app as app
from flask import abort
from flask import request

if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
    host = '0.0.0.0'
else:
    port = 5000
    host = '127.0.0.1'


app = Eve()


def check_catalogs_secrets(library_uuid, library_secret):
    catalogs_secrets = app.data.driver.db['catalogs_secrets']
    c = catalogs_secrets.find_one({library_uuid: library_secret})
    return c


def check_insert_books(items):
    if 'library_uuid' and 'library_secret' in items[0]:
        if check_catalogs_secrets(items[0]['library_uuid'], items[0]['library_secret']):
            del items[0]['library_secret']
        else:
            abort(403)
    else:
        abort(403)


def check_delete_item_books(item):
    print("@DELETE arg#item {}".format(item))
    print("@DELETE headers {}".format(request.headers))
    if 'LIBRARY_UUID' and 'LIBRARY_SECRET' in request.headers:
        if check_catalogs_secrets(request.headers['LIBRARY_UUID'], request.headers['LIBRARY_SECRET']):
            print("@DELETE {}".format(item))
        else:
            abort(403)
    else:
        abort(403)


def check_insert_catalogs(items):
    print("@INSERT catalogs arg#items: {}".format(items))
    catalogs_secrets = app.data.driver.db['catalogs_secrets']
    if 'library_uuid' and 'library_secret' in items[0]:
        c = catalogs_secrets.insert_one({items[0]['library_uuid']: items[0]['library_secret']}).inserted_id
        print("inserted_id: {}".format(c))
        del items[0]['library_secret']
    else:
        abort(403)


def check_delete_item_catalogs(item):
    print("@DELETE arg#item {}".format(item))
    print("@DELETE headers {}".format(request.headers))
    if 'LIBRARY_UUID' and 'LIBRARY_SECRET' in request.headers:
        c = check_catalogs_secrets(request.headers['LIBRARY_UUID'], request.headers['LIBRARY_SECRET'])
        if c:
            catalogs_secrets = app.data.driver.db['catalogs_secrets']
            catalogs_secrets.remove({request.headers['LIBRARY_UUID']: request.headers['LIBRARY_SECRET']})
            print("@DELETE {}".format(item))
        else:
            abort(403)
    else:
        abort(403)

def check_update(updates, original):
    print("@UPDATE arg#updates: {}, arg#original: {}".format(updates, original))
    if 'library_uuid' and 'library_secret' in updates:
        if check_catalogs_secrets(updates['library_uuid'], updates['library_secret']):
            del items[0]['library_secret']
        else:
            abort(403)
    else:
        abort(403)


app.on_insert_catalogs += check_insert_catalogs
app.on_update_catalogs += check_update
app.on_delete_item_catalogs += check_delete_item_catalogs

app.on_insert_books += check_insert_books
app.on_update_books += check_update
app.on_delete_item_books += check_delete_item_books

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
