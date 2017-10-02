# -*- coding: utf-8 -*-

"""
    Eve Demo
    ~~~~~~~~

    A demostration of a simple API powered by Eve REST API.

    The live demo is available at eve-demo.herokuapp.com. Please keep in mind
    that the it is running on Heroku's free tier using a free MongoHQ
    sandbox, which means that the first request to the service will probably
    be slow. The database gets a reset every now and then.

    :copyright: (c) 2016 by Nicola Iarocci.
    :license: BSD, see LICENSE for more details.
"""

import os
from eve import Eve
from flask import current_app as app

# Heroku support: bind to PORT if defined, otherwise default to 5000.
if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
    # use '0.0.0.0' to ensure your REST API is reachable from all your
    # network (and not only your computer).
    host = '0.0.0.0'
else:
    port = 5000
    host = '127.0.0.1'

app = Eve()


def check_catalog(items):
    print("ITEMS: {}".format(items))
    catalogs_secrets = app.data.driver.db['catalogs_secrets']
    c = catalogs_secrets.insert_one({items[0]['library_uuid']: items[0]['library_secret']}).inserted_id
    print(c)
    del items[0]['library_secret']
    return items


def check_books(items):
    print("ITEMS: {}".format(items))


app.on_insert_catalogs += check_catalog
app.on_insert_books += check_books

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
