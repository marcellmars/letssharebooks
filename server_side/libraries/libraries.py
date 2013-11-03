#------------------------------------------------------------------------------
# main library functionalities and api
#------------------------------------------------------------------------------

import uuid
import simplejson as json
from bson import json_util

def paginate(cursor, page=1, per_page=5):
    '''
    Use this in request with pagination
    '''
    items = cursor.skip((page-1) * per_page).limit(per_page)
    next_page = page + 1
    if items.count(True) < per_page:
        next_page = None
    return (items, next_page)

#------------------------------------------------------------------------------

def add_library(db, library_uuid, books, last_modified):
    books_uuid = []
    # insert books in the global library and take uuids
    for book in books:
        try:
            db.books.insert(book)
            books_uuid.append(book['uuid'])
        except Exception, e:
            for k in book.keys():
                new_key = key.replace('.', '')
                book[new_key] = book[key]
                db.books.insert(book)
                books_uuid.append(book['uuid'])
    # update catalog metadata collection
    db.catalog.update({'library_uuid': library_uuid},
                      {'$set':{'books': books_uuid,
                               'last_modified': last_modified,
                               'tunnel':1234}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------
    
def import_catalog(db, catalog):
    library_uuid = catalog['library_uuid']
    last_modified = catalog['last_modified']
    books = catalog['books']
    
    db_cat = db.catalog.find_one({'library_uuid':library_uuid})
    if not db_cat:
        print 'new library...'
        add_library(db, library_uuid, books, last_modified)
        return
    
    db_cat_len = len(db_cat['books'])
    # db sync conditions - resolve to True/False
    new_library = not db_cat
    added_books = len(books) > db_cat_len
    changed_timestamp = last_modified != db_cat['last_modified']
    if new_library or added_books or changed_timestamp:
        print 'updating library %s' % library_uuid
        db.books.remove({'library_uuid':library_uuid})
        add_library(db, library_uuid, books, last_modified)
    else:
        print 'nothing changed...'

#------------------------------------------------------------------------------
        
def get_catalog(db, uuid):
    return serialize2json(
        [i for i in db.catalog.find({'library_uuid':uuid})])

#------------------------------------------------------------------------------
        
def get_books(db, page):
    lib_uuids = [i['library_uuid'] for i in db.catalog.find({'tunnel':{ '$gt': 0 }})]
    books = db.books.find({'library_uuid':{'$in':lib_uuids}})
    items, next_page = paginate(books, page)
    return serialize2json({'books': list(items),
                           'next_page': next_page})

#------------------------------------------------------------------------------    

def serialize2json(data):
    '''
    Pretty print for json
    '''
    return json.dumps(data, sort_keys=True,
                      indent=4, default=json_util.default)

#------------------------------------------------------------------------------
