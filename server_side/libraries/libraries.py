#------------------------------------------------------------------------------
# main library functionalities and api
#------------------------------------------------------------------------------

import uuid
import traceback
import simplejson as json
from bson import json_util
import settings

#------------------------------------------------------------------------------

def import_catalog(db, catalog):
    '''
    Imports user calibre catalog to the database.
    :db mongo database
    :catalog python object received from calibre plugin
    '''
    library_uuid = catalog['library_uuid']
    last_modified = catalog['last_modified']
    books = catalog['books']
    # if never seen this library before...
    db_cat = db.catalog.find_one({'library_uuid':library_uuid})
    if not db_cat:
        print 'new library...'
        add_library(db, library_uuid, books, last_modified)
        return
    # this library is already in the db -- is it in sync?
    db_cat_len = len(db_cat['books'])
    added_books = len(books) > db_cat_len
    changed_timestamp = last_modified != db_cat['last_modified']
    if added_books or changed_timestamp:
        # user library has changed -- update needed
        print 'updating library %s' % library_uuid
        # first remove all books
        db.books.remove({'library_uuid':library_uuid})
        # add books and create catalog entry
        add_library(db, library_uuid, books, last_modified)
    else:
        print 'nothing changed...'

#------------------------------------------------------------------------------

def add_library(db, library_uuid, books, last_modified):
    '''
    Adds books to the database and modifies catalog entry. Mostly used with
    import_catalog function.
    '''
    books_uuid = []
    # insert books in the global library and take uuids
    for book in books:
        # add id of the library to the each book
        book['library_uuid'] = library_uuid
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
                      {'$set':{'books': books_uuid,
                               'last_modified': last_modified,
                               'tunnel':1234}}, # testing...
                      upsert=True, multi=False)

#------------------------------------------------------------------------------
        
def get_catalog(db, uuid):
    '''
    Read catalog entry from the database and return json representation
    '''
    return serialize2json(
        [i for i in db.catalog.find({'library_uuid':uuid})])

#------------------------------------------------------------------------------
        
def get_books(db, page, query={}):
    '''
    Reads and returns books from the database.
    page: parameter for _paginate_ function
    '''
    # query
    q = {}
    # get all libraries that have active ssh tunnel
    lib_uuids = [i['library_uuid'] for i in db.catalog.find(
            {'tunnel':{ '$gt': 0 }})]
    q['library_uuid'] = {'$in':lib_uuids}
    # extract search parameters
    for k,v in query.iteritems():
        if v != '' and k in ['authors', 'titles']:
            q[k] = {"$regex": v, "$options": 'i'}
        # elif v != '':
        #     q = {"$or": [
        #             {"title": {"$regex": ".*{}.*".format(v), "$options": 'i'}},
        #             {"authors":{"$regex":".*{}.*".format(v), "$options": 'i'}},
        #             {"comments":{"$regex":".*{}.*".format(v), "$options": 'i'}},
        #             {"tags":{"$regex":".*{}.*".format(v), "$options": 'i'}},
        #             {"publisher":{"$regex":".*{}.*".format(v), "$options": 'i'}},
        #             {"identifiers":{"$regex":".*{}.*".format(v), "$options": 'i'}}]}

    # get all books that belong to libraries with active tunnel
    books = db.books.find(q)
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
                      indent=4, default=json_util.default)

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
