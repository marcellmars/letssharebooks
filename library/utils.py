#------------------------------------------------------------------------------
# misc utility functions
#------------------------------------------------------------------------------

from bson import json_util as json
from pymongo import MongoClient
import simplejson
import time
import socket
import logging
import settings

#------------------------------------------------------------------------------

def ensure_all_indexes(db):
    '''
    Create some indexes
    '''
    logging.info('Ensuring db indexes.')
    db.books.ensure_index([('authors', 1)])
    db.books.ensure_index([('title', 1)])
    db.books.ensure_index([('uuid', 1), ('library_uuid', 1), ('librarian', 1)])

#------------------------------------------------------------------------------

def connect_to_db(env):
    logging.info('connecting to db {}'.format(env['mongo_addr']))
    db = None
    mongo_client = MongoClient(env['mongo_addr'], env['mongo_port'])
    db = mongo_client[env['dbname']]
    ensure_all_indexes(db)
    return db

#------------------------------------------------------------------------------

def remove_dots_from_dict(d):
    '''
    Remove dots from keys in dict d
    '''
    for k, v in d.iteritems():
        if isinstance(v, dict):
            d[k] = remove_dots_from_dict(v)
        else:
            if k.find('.') >= 0:
                del d[k]
                new_key = k.replace('.', '')
                d[new_key] = v
    return d

#------------------------------------------------------------------------------

def ser2json(data):
    '''
    Pretty print for json
    '''
    indent=None
    if settings.ENV_NAME in ['local', 'test']:
        indent=4
    return json.dumps(data, sort_keys=True, indent=indent,
                      default=json.default)

#------------------------------------------------------------------------------

def remove_all_data(db):
    '''
    Removes all data from the database
    '''
    db.books.remove()
    db.catalog.remove()

#------------------------------------------------------------------------------

def jsonp(func):
    def foo(self, *args, **kwargs):
        callback, _ = None, None
        if 'callback' in kwargs and '_' in kwargs:
            callback, _ = kwargs['callback'], kwargs['_']
            del kwargs['callback'], kwargs['_']
        ret = func(self, *args, **kwargs)
        if callback is not None:
            ret = '%s(%s)' % (callback, simplejson.dumps(ret))
        return ret
    return foo

#------------------------------------------------------------------------------

def timeit(method):
    '''
    Simple profiling decorator
    '''
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('Exec time for method --{}--: {:.2f} sec'.format(
                method.__name__,te-ts))
        return result

    return timed

#------------------------------------------------------------------------------

def get_mongo_live_addr():
    '''
    Tries to locate "mongodb" instance. If host address resolving fails then is
    assumes that local configuration is active.
    '''
    try:
        return socket.gethostbyname('mongodb')
    except Exception:
        logging.error('socket.gethostbyname for mongodb failed. assume local.',
                      exc_info=True)
    return None
