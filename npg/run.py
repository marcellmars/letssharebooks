# -*- coding: utf-8 -*-

import os
from eve import Eve
from flask import current_app as app
from flask import abort

if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
    host = '0.0.0.0'
else:
    port = 5000
    host = '127.0.0.1'


app = Eve()


def check_books(items):
    catalogs_secrets = app.data.driver.db['catalogs_secrets']
    c = catalogs_secrets.find_one({items[0]['library_uuid']: items[0]['library_secret']})
    if c:
        del items[0]['library_secret']
        return items
    else:
        abort(403)



def check_catalogs(items):
    print("ITEMS: {}".format(items))
    catalogs_secrets = app.data.driver.db['catalogs_secrets']
    c = catalogs_secrets.insert_one({items[0]['library_uuid']: items[0]['library_secret']}).inserted_id
    print(c)
    del items[0]['library_secret']
    return items


app.on_insert_catalogs += check_catalogs
app.on_insert_books += check_books

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
