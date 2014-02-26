#------------------------------------------------------------------------------
# main library functionalities and api
#------------------------------------------------------------------------------

import os
import cherrypy
import uuid
import zipfile
import simplejson
import traceback
from bson import json_util as json
import settings
import utils
import pickle

#------------------------------------------------------------------------------

PUBLIC_BOOK_FIELDS = {
    'application_id':1,
    'title':1,
    'formats':1,
    'authors':1,
    'tunnel':1,
    'uuid':1,
    '_id': 0
    }

#------------------------------------------------------------------------------

def get_active_tunnels():
    try:
        return pickle.load(open("/tmp/active_tunnel_ports","rb"))
    except:
        return []

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
    # print("db_cat:{}".format(db_cat))
    # print("books_add: {}; books_remove: {}".format(
    #         catalog['books']['add'], catalog['books']['remove']))
    if db_cat:
        # remove books as requested
        remove_from_library(db, library_uuid, catalog['books']['remove'])
    # add books as requested (for new library and for sync)
    add_to_library(db, library_uuid, tunnel, catalog['books']['add'])
    update_catalog(db, library_uuid, last_modified, tunnel)
    return library_uuid

#------------------------------------------------------------------------------

def update_catalog(db, library_uuid, last_modified, tunnel):
    # set tunnel to 0 if there is a library with the same tunnel from before
    old_libraries = [b['library_uuid'] for b in db.catalog.find({'tunnel': tunnel})]
    db.catalog.update({'library_uuid': {'$in': old_libraries}}, {'$set': {'tunnel': 0}}, upsert=True)
    db.catalog.update({'library_uuid': library_uuid},
                      {'$set': {'last_modified': last_modified,
                                'tunnel':tunnel}},
                      upsert=True, multi=False)
    # update tunnel to the current one for all books in current library
    db.books.update({'library_uuid': library_uuid}, {'$set': {'tunnel': tunnel}}, multi=True)
#------------------------------------------------------------------------------

def remove_from_library(db, library_uuid, books_uuids):
    '''
    Remove books from the library and update catalog
    '''
    if not books_uuids:
        return
    for uid in books_uuids:
        print 'removing %s' % uid
        db.books.remove({'uuid':uid})
    db.catalog.update({'library_uuid': library_uuid},
                      {'$pull': {'books': {'$in': books_uuids}}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------

def add_to_library(db, library_uuid, tunnel, books):
    '''
    Adds books to the database and modifies catalog entry. Mostly used with
    import_catalog function.
    '''
    if not books:
        return
    books_uuid = []
    # insert books in the global library and take uuids
    for book in books:
        # add id of the library to the each book
        book['library_uuid'] = library_uuid
        book['tunnel'] = tunnel
        try:
            db.books.insert(book)
            db.books.update({'uuid': book['uuid']},
                            book,
                            upsert=True, multi=False)
            # collect book uuids for catalog entry
            books_uuid.append(book['uuid'])
        except Exception, e:
            # some books have dots in keys - not good for mongo
            utils.remove_dots_from_dict(book)
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

def get_book(db, uuid):
    '''
    Returns book with the param uuid
    '''
    book = db.books.find_one({'uuid':uuid}, PUBLIC_BOOK_FIELDS)
    return book

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
            {'tunnel': {'$in': get_active_tunnels()}})]
    # print("GET_ACTIVE_TUNNELS: {}".format(get_active_tunnels()))
    # print("LIB_UUIDS:{}".format(lib_uuids))
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
    #print("QUERY:{}".format(q))
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

def handle_uploaded_catalog(db, uploaded_file):
    '''
    Opens, unzips and parses uploaded catalog and imports books to the db
    '''
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    content = uploaded_file.file.read()
    # generate unique filename
    filename = 'tmp/%s-%s' % (uploaded_file.filename, uuid.uuid4())
    with open(filename, "wb") as f:
        f.write(content)
    # unzip file
    with zipfile.ZipFile(filename) as zfile:
        content = zfile.read('library.json')
    # decode from json and import to database
    catalog = simplejson.loads(content)
    res = import_catalog(db, catalog)
    return res

#------------------------------------------------------------------------------

def remove_all(db):
    '''
    Removes all data from the database
    '''
    db.books.remove()
    db.catalog.remove()
