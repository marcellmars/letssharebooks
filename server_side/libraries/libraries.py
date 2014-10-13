#------------------------------------------------------------------------------
# main library functionalities and api
#------------------------------------------------------------------------------

import os
import uuid
import zipfile
import settings
import utils
import pickle
import simplejson

#------------------------------------------------------------------------------

# book fields for books in the grid
PUBLIC_BOOK_FIELDS = {
    'application_id':1,
    'title':1,
    'formats':1,
    'authors':1,
    'tunnel':1,
    'uuid':1,
    'librarian':1,
    '_id': 0
    }

# book fields for book in the modal window
PUBLIC_SINGLE_BOOK_FIELDS = {
    'application_id':1,
    'title':1,
    'formats':1,
    'authors':1,
    'tunnel':1,
    'uuid':1,
    'publisher':1,
    'comments':1,
    'librarian':1,
    '_id': 0
    }

#------------------------------------------------------------------------------

def get_active_tunnels():
    '''
    Returns list of active tunnels used by the get_books function
    '''
    try:
        return pickle.load(open('/tmp/active_tunnel_ports', 'rb'))
    except:
        return []

def get_active_tunnels_mock():
    '''
    Mock for local/test purposes
    '''
    return [12345]

def setup_active_tunnels_func():
    '''
    Called from settings.py based on current configuration
    '''
    global get_active_tunnels
    if settings.ENV_NAME in ['local', 'test']:
        get_active_tunnels = get_active_tunnels_mock
        
#------------------------------------------------------------------------------

def handle_uploaded_catalog(db, uploaded_file, zipped=True):
    '''
    Opens, unzips and parses uploaded catalog and imports books to the db
    '''
    # if uploaded file is zipped json catalog
    if zipped:
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
    # else if json is directly uploaded
    else:
        content = uploaded_file
    # decode from json and import to database
    catalog = simplejson.loads(content)
    res = import_catalog(db, catalog)
    return res

#------------------------------------------------------------------------------

def import_catalog(db, catalog):
    '''
    Imports user calibre catalog to the database.
    :db mongo database
    :catalog python object received from calibre plugin
    :portable True if this is reference to portable library
    '''
    library_uuid = catalog['library_uuid']
    last_modified = catalog['last_modified']
    librarian = catalog['librarian']
    tunnel = catalog.get('tunnel')
    portable = False
    if catalog.get('portable'):
        portable = True
    # check if library already in the db
    db_cat = db.catalog.find_one({'library_uuid': library_uuid})
    if db_cat:
        # remove books as requested
        remove_from_library(db, library_uuid, catalog['books']['remove'])
    # add books as requested (for new library and for sync)
    add_to_library(db, library_uuid, tunnel, catalog['books']['add'], portable)
    update_catalog(db, library_uuid, last_modified, tunnel, librarian,
                   portable)
    return library_uuid

#------------------------------------------------------------------------------

def update_catalog(db, library_uuid, last_modified, tunnel, librarian, portable):
    # set tunnel to 0 if there is a library with the same tunnel from before
    old_libraries = [b['library_uuid']
                     for b in db.catalog.find({'tunnel': tunnel})]
    db.catalog.update({'library_uuid': {'$in': old_libraries}},
                      {'$set': {'tunnel': 0}}, multi=True)
    db.catalog.update({'library_uuid': library_uuid},
                      {'$set': {'last_modified': last_modified,
                                'tunnel': tunnel,
                                'librarian': librarian,
                                'portable': portable}},
                      upsert=True, multi=False)
    # update tunnel for all books in current library
    db.books.update({'library_uuid': library_uuid},
                    {'$set': {'tunnel': tunnel,
                              'librarian': librarian}},
                    multi=True)
#------------------------------------------------------------------------------

def remove_from_library(db, library_uuid, books_uuids):
    '''
    Remove books from the library and update catalog
    '''
    [db.books.remove({'uuid':uid}) for uid in books_uuids]
    db.catalog.update({'library_uuid': library_uuid},
                      {'$pull': {'books': {'$in': books_uuids}}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------

def add_to_library(db, library_uuid, tunnel, books, portable):
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
        book['portable'] = portable
        try:
            db.books.update({'uuid': book['uuid']},
                            book,
                            upsert=True, multi=False)
            # collect book uuids for catalog entry
            books_uuid.append(book['uuid'])
        except Exception as e:
            # some books have dots in keys - not good for mongo
            utils.remove_dots_from_dict(book)
            db.books.update({'uuid': book['uuid']},
                            book,
                            upsert=True, multi=False)
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
    return utils.ser2json(db.catalog.find_one({'library_uuid':uuid},
                                              {'books':1,
                                               'last_modified':1, '_id' : 0}))

#------------------------------------------------------------------------------

def get_catalogs(db):
    '''
    for testing purposes
    '''
    return utils.ser2json(db.catalog.count())

#------------------------------------------------------------------------------

def get_book(db, uuid):
    '''
    Returns book with the param uuid
    '''
    book = db.books.find_one({'uuid':uuid}, PUBLIC_SINGLE_BOOK_FIELDS)
    return utils.ser2json(book)

#------------------------------------------------------------------------------

def get_books(db, page, query={}):
    '''
    Reads and returns books from the database.
    page: parameter for _paginate_ function
    '''
    # query
    q = {}
    # extract search parameters
    for k, v in query.iteritems():
        if not v:
            continue
        v = v.encode('utf-8')
        match_pattern = {'$regex':'.*{}.*'.format(v), '$options': 'i'}
        if k in ['authors', 'title', 'librarian']:
            q[k] = match_pattern
        else:
            q = {"$or": [{"title": match_pattern},
                         {"authors": match_pattern},
                         {"comments": match_pattern},
                         {"tags": match_pattern},
                         {"publisher": match_pattern},
                         {"identifiers": match_pattern}]}
    # get all libraries that have active ssh tunnel or reference portables
    active_lib_uuids = [
        i['library_uuid'] for i in db.catalog.find(
            {'$or': [{'tunnel': {'$in': get_active_tunnels()}},
                     {'portable': True}]})]
    q['library_uuid'] = {'$in': active_lib_uuids}
    # get books that match search criteria
    books = db.books.find(q, PUBLIC_BOOK_FIELDS).sort('title_sort')
    authors = books.distinct('authors')
    titles = books.distinct('title')
    # get distinct list of all (active or portable) librarians from db.catalog
    active_catalogs = db.catalog.find({'library_uuid':{'$in': active_lib_uuids}})
    librarians = active_catalogs.distinct('librarian')
    # paginate books
    items, next_page, on_page, total = paginate(books, page)
    # return serialized books with availability of next page
    return utils.ser2json({'books': list(items),
                           'next_page': next_page,
                           'on_page': on_page,
                           'total': total,
                           'authors': authors,
                           'titles': titles,
                           'librarians': librarians})

#------------------------------------------------------------------------------

def get_portables(db):
    '''
    Returns all registered portable libraries
    '''
    return utils.ser2json(list(db.catalog.find(
                {'portable': True},
                {'librarian':1, 'library_uuid':1, '_id': 0})))

#------------------------------------------------------------------------------

def remove_portable(db, lib_uuid):
    '''
    Removes registered portable library with given lib_uuid
    '''
    q = {'portable': True, 'library_uuid': lib_uuid}
    portable_cat = db.catalog.find_one(q)
    if portable_cat:
        remove_from_library(db, lib_uuid, portable_cat['books'])
        db.catalog.remove(q)
        return utils.ser2json(True)
    return utils.ser2json(False)

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
