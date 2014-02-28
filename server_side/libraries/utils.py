#------------------------------------------------------------------------------
# misc utility functions
#------------------------------------------------------------------------------

from pymongo import MongoClient

#------------------------------------------------------------------------------

def connect_to_db(env):
    db = None
    try:
        Mongo_client = MongoClient(env['mongo_addr'],
                                   env['mongo_port'])
        db = Mongo_client[env['dbname']]
    except Exception as e:
        print 'unable to connect to mongodb!'
    return db

#------------------------------------------------------------------------------

def remove_dots_from_dict(d):
    '''
    Remove dots from keys in dict d
    '''
    for k,v in d.iteritems():
        if isinstance(v, dict):
            d[k] = remove_dots_from_dict(v)
        else:
            if k.find('.') >= 0:
                del d[k]
                new_key = k.replace('.', '')
                d[new_key] = v

#------------------------------------------------------------------------------

def remove_all_data(db):
    '''
    Removes all data from the database
    '''
    db.books.remove()
    db.catalog.remove()
