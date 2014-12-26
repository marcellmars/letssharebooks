#------------------------------------------------------------------------------
# misc utility functions
#------------------------------------------------------------------------------

from bson import json_util as json
from pymongo import MongoClient
import simplejson
import settings

#------------------------------------------------------------------------------

def connect_to_db(env):
    db = None
    try:
        mongo_client = MongoClient(env['mongo_addr'],
                                   env['mongo_port'])
        db = mongo_client[env['dbname']]
        print("DB: {}".format(db))
    except Exception as e:
        print 'unable to connect to mongodb!'
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
