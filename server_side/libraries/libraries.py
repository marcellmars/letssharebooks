#------------------------------------------------------------------------------
# main library functionalities and api
#------------------------------------------------------------------------------

import uuid
import traceback
from bson import json_util as json
import settings

#------------------------------------------------------------------------------

PUBLIC_BOOK_FIELDS = {
    'application_id':1,
    'title':1,
    'formats':1,
    'authors':1,
    'tunnel':1,
    '_id': 0
    }

#------------------------------------------------------------------------------

def import_catalog(db, catalog):
    '''
    Imports user calibre catalog to the database.
    :db mongo database
    :catalog python object received from calibre plugin
    '''
    library_uuid = catalog['library_uuid']
    last_modified = catalog['last_modified']
    tunnel = catalog['tunnel']
    # check if library already in the db
    db_cat = db.catalog.find_one({'library_uuid':library_uuid})
    if db_cat:
        # remove books as requested
        remove_from_library(db, library_uuid, catalog['books']['remove'])
    # add books as requested (for new library and for sync)
    add_to_library(db, library_uuid, tunnel, catalog['books']['add'])
    update_catalog(db, library_uuid, last_modified, tunnel)
    return

#------------------------------------------------------------------------------

def update_catalog(db, library_uuid, last_modified, tunnel):
    db.catalog.update({'library_uuid': library_uuid},
                      {'$set': {'last_modified': last_modified,
                                'tunnel':tunnel}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------

def remove_from_library(db, library_uuid, books_uuids):
    '''
    Remove books from the library and update catalog
    '''
    if len(books_uuids) == 0:
        return
    for uuid in books_uuids:
        print 'removing %s' % uuid
        db.books.remove({'uuid':uuid})
    db.catalog.update({'library_uuid': library_uuid},
                      {'$pull': {'books': {'$in': books_uuids}}},
                      upsert=True, multi=False)
    
#------------------------------------------------------------------------------
    
def add_to_library(db, library_uuid, tunnel, books):
    '''
    Adds books to the database and modifies catalog entry. Mostly used with
    import_catalog function.
    '''
    if len(books) == 0:
        return
    books_uuid = []
    # insert books in the global library and take uuids
    for book in books:
        # add id of the library to the each book
        book['library_uuid'] = library_uuid
        book['tunnel'] = tunnel
        try:
            db.books.insert(book)
            # collect book uuids for catalog entry
            books_uuid.append(book['uuid'])
        except Exception, e:
            # some books have dots in keys - not good for mongo
            remove_dots_from_dict(book)
            db.books.insert(book)
            books_uuid.append(book['uuid'])
    # update catalog metadata collection
    db.catalog.update({'library_uuid': library_uuid},
                      {'$pushAll': {'books': books_uuid}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------
        
def get_catalog(db, uuid):
    '''
    Read catalog entry from the database and return json representation
    '''
    return serialize2json(
        db.catalog.find_one({'library_uuid':uuid},
                            {'books':1, 'last_modified':1, '_id' : 0}))

#------------------------------------------------------------------------------
        
def get_books(db, page, query={}):
    '''
    Reads and returns books from the database.
    page: parameter for _paginate_ function
    '''
    # query
    q = {}
    # get all libraries that have active ssh tunnel
    lib_uuids = [i['library_uuid'] for i in db.catalog.find({'tunnel': {'$gt':0}})]
    print("lib_uuids: {}".format(db.catalog.find({'tunnel': {'$gt':0}})))
    q['library_uuid'] = {'$in': lib_uuids}
    # extract search parameters
    for k,v in query.iteritems():
        if v != '' and k in ['authors', 'titles']:
            q[k] = {"$regex": v, "$options": 'i'}
        elif v != '':
            q = {"$or": [
                    {"title": {"$regex": ".*{}.*".format(v), "$options": 'i'}},
                    {"authors":{"$regex":".*{}.*".format(v), "$options": 'i'}},
                    {"comments":{"$regex":".*{}.*".format(v), "$options": 'i'}},
                    {"tags":{"$regex":".*{}.*".format(v), "$options": 'i'}},
                    {"publisher":{"$regex":".*{}.*".format(v), "$options": 'i'}},
                    {"identifiers":{"$regex":".*{}.*".format(v), "$options": 'i'}}]}

    # get all books that belong to libraries with active tunnel
    books = db.books.find(q, PUBLIC_BOOK_FIELDS)
    authors = books.distinct('authors')
    titles = books.distinct('title_sort')
    # paginate books
    items, next_page, on_page, total = paginate(books, page)
    # return serialized books with availability of next page
    return serialize2json({'books': list(items),
                           'next_page': next_page,
                           'on_page': on_page,
                           'total': total,
                           'authors': authors,
                           'titles': titles})

#------------------------------------------------------------------------------    

def serialize2json(data):
    '''
    Pretty print for json
    '''
    return json.dumps(data, sort_keys=True,
                      indent=4, default=json.default)

#------------------------------------------------------------------------------

def paginate(cursor, page=1, per_page=settings.ITEMS_PER_PAGE):
    '''
    Use this in request with pagination
    '''
    items = cursor.skip((page-1) * per_page).limit(per_page)
    next_page = page + 1
    num_items_page = items.count(True)
    if num_items_page < per_page:
        next_page = None
    return (items, next_page, num_items_page, cursor.count())

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
