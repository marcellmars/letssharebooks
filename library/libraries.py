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
import requests
import socket
import json
import time
import logging

#------------------------------------------------------------------------------

# book fields for books in the grid
PUBLIC_BOOK_FIELDS = {
    'application_id': 1,
    'title': 1,
    'formats': 1,
    'authors': 1,
    'tunnel': 1,
    'uuid': 1,
    'librarian': 1,
    'portable': 1,
    'portable_url': 1,
    'format_metadata': 1,
    'library_uuid': 1,
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
    'portable':1,
    'portable_url':1,
    'format_metadata':1,
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
    return [[12345]]

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

def import_catalog(db, catalog, portable_url=None):
    '''
    Imports user calibre catalog to the database.
    :db mongo database
    :catalog python object received from calibre plugin
    :portable True if this is reference to portable library
    '''
    library_uuid = catalog['library_uuid']
    last_modified = catalog['last_modified']
    librarian = catalog['librarian']
    tunnel = catalog['tunnel']
    portable = False
    if tunnel == -1337 or portable_url:
        portable = True
    # check if library already in the db
    db_cat = db.catalog.find_one({'library_uuid': library_uuid})
    if db_cat:
        print("BOOKS TO BE REMOVED: {}".format(catalog['books']['remove']))
        if portable:
            raise ValueError('already registered')
        # remove books as requested
        remove_from_library(db, library_uuid, catalog['books']['remove'])
    # add books as requested (for new library and for sync)
    add_to_library(db, library_uuid, librarian, tunnel,
                   catalog['books']['add'], portable, portable_url)
    # set tunnel to 0 if there is a library with the same tunnel from before
    old_libraries = [i['library_uuid']
                     for i in db.catalog.find({'tunnel': tunnel}) if i['library_uuid'] != library_uuid]
    print("OLD_LIBRARIES: {}".format(old_libraries))
    db.catalog.update({'library_uuid': {'$in': old_libraries}},
                      {'$set': {'tunnel': 0}}, multi=True)
    # update catalog metadata
    db.catalog.update({'library_uuid': library_uuid},
                      {'$set': {'last_modified': last_modified,
                                'tunnel': tunnel,
                                'librarian': librarian,
                                'portable': portable,
                                'portable_url': portable_url}},
                      upsert=True, multi=False)
    # update tunnel for all books in current library
    db.books.update({'library_uuid': library_uuid},
                    {'$set': {'tunnel': tunnel,
                              'librarian': librarian}},
                    multi=True)
    return library_uuid

#------------------------------------------------------------------------------

def remove_from_library(db, library_uuid, books_uuids):
    '''
    Remove books from the library and update catalog
    '''
    books_uuids = [uuid for uuid in books_uuids]
    [db.books.remove({'uuid':uid}) for uid in books_uuids]
    db.catalog.update({'library_uuid': library_uuid},
                      {'$pull': {'books': {'$in': books_uuids}}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------

def add_to_library(db, library_uuid, librarian, tunnel, books, portable, portable_url=None):
    '''
    Adds books to the database and modifies catalog entry. Mostly used with
    import_catalog function.
    '''
    print("BOOKS: {}".format(books))
    books_uuid = []
    for book in books:
        # add some catalog metadata
        book['library_uuid'] = library_uuid
        book['tunnel'] = tunnel
        book['portable'] = portable
        book['librarian'] = librarian
        book['portable_url'] = portable_url
        try:
            db.books.update({'uuid': book['uuid']},
                             utils.remove_dots_from_dict(book),
                             upsert=True, multi=False)
            #collect book uuids for catalog entry
            books_uuid.append((book['uuid'],
                               book['last_modified']))
        except Exception as e:
            print(e)
    # update catalog metadata collection
    db.catalog.update({'library_uuid': library_uuid},
                      {'$pushAll': {'books': books_uuid}},
                      upsert=True, multi=False)

#------------------------------------------------------------------------------

def get_catalog(db, uuid):
    '''
    Read catalog entry from the database and return json representation
    '''
    return utils.ser2json(db.catalog.find_one(
            {'library_uuid': uuid},
            {'books': 1, 'last_modified': 1, '_id' : 0}))

#------------------------------------------------------------------------------

def get_catalogs(db):
    '''
    for testing purposes
    '''
    return utils.ser2json(db.catalog.find(
            {},
            {'library_uuid':1, 'librarian': 1, '_id': 0}))

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
    logging.debug('QUERY: {}'.format(query))
    # extract search parameters and build query
    for field, field_value in query.iteritems():
        if field_value:
            words = field_value.encode('utf-8').split(' ')
            match_pattern = {'$regex': '.*'.join(words), '$options': 'i'}
            # match fileds with exact mapping
            if field in ['authors', 'title', 'librarian', 'uuid']:
                q[field] = match_pattern
            # search all metadata
            elif field == 'search_all':
                q = {"$or": [{'title': match_pattern},
                             {'authors': match_pattern},
                             {'comments': match_pattern},
                             {'tags': match_pattern},
                             {'publisher': match_pattern},
                             {'identifiers': match_pattern}]}
            else:
                logging.warning('Unrecognized search param {}'.format(field))
    # get all libraries that have active ssh tunnel or reference portables
    active_tunnels = get_active_tunnels()[0]
    logging.debug('active_tunnels: {}'.format(active_tunnels))
    active_catalogs = db.catalog.find({'$or': [
                {'tunnel': {'$in': active_tunnels}},
                {'portable': True}]})
    q['library_uuid'] = {'$in': [i['library_uuid'] for i in active_catalogs]}
    logging.debug('FINAL QUERY: {}'.format(q))
    librarians = active_catalogs.distinct('librarian')
    authors = db.books.find(q, PUBLIC_BOOK_FIELDS).distinct('authors')
    titles = db.books.find(q, PUBLIC_BOOK_FIELDS).distinct('title')
    # paginate books
    items, next_page, on_page, total = paginate(db.books.find(
            q, PUBLIC_BOOK_FIELDS).sort('uuid'), page)
    # return serialized books with availability of next page
    return utils.ser2json({'books': list(items),
                           'next_page': next_page,
                           'on_page': on_page,
                           'total': total,
                           'librarians': librarians,
                           'authors': authors,
                           'titles': titles
                           })

#------------------------------------------------------------------------------

def get_active_ports():
    data = {'get':'active_tunnel_ports'}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('sshd', 3773))
    s.send(json.dumps(data))
    ports = []
    while 1:
        rdata = s.recv(8192)
        if rdata:
            ports.append(json.loads(rdata))
        else:
            break
    s.close()
    print(ports[0], get_active_tunnels()[0])
    return ports[0]

#------------------------------------------------------------------------------

def get_active_librarians(db):
    time.sleep(0.5)
    active_catalogs = db.catalog.find({'$or': [
                {'tunnel': {'$in': [int(p) for p in get_active_ports()]}},
                {'portable': True}]})
    librarians = active_catalogs.distinct('librarian')
    print([c['librarian'] for c in active_catalogs], librarians)
    return utils.ser2json({'librarians' : librarians})

#------------------------------------------------------------------------------

def add_portable(db, url):
    print('Registering portable: with url {}'.format(url))
    try:
        libjs = requests.get(url + '/static/data.js').text
        libjson = libjs[libjs.find('{'):-1]
        catalog = simplejson.loads(libjson)
        res = import_catalog(db, catalog, url)
        return res
    except ValueError as e:
        return utils.ser2json('Already registered...')
    except requests.ConnectionError as e:
        print('Registering portable: ConnectionError {}'.format(e))
    except Exception as e:
        print('Registering portable: Exception {}'.format(e))
    return utils.ser2json('Error while registering portable...')

#------------------------------------------------------------------------------

def get_portables(db):
    '''
    Returns all registered portable libraries
    '''
    return utils.ser2json(list(db.catalog.find(
                {'portable': True},
                {'librarian':1, 'library_uuid':1, '_id': 0})))

#------------------------------------------------------------------------------

def remove_portable(db, url):
    '''
    Removes registered portable library with given lib_uuid
    '''
    q = {'portable': True, 'portable_url': url}
    portable_cat = db.catalog.find_one(q)
    if portable_cat:
        remove_from_library(db,
                            portable_cat['library_uuid'],
                            portable_cat['books'])
        db.catalog.remove(q)
        return utils.ser2json('Library removed.')
    return utils.ser2json('Error while removing portable...')

#------------------------------------------------------------------------------

def get_status(db):
    '''
    Return some status info
    '''
    active_catalogs = db.catalog.find({'$or': [
                {'tunnel': {'$in': get_active_tunnels()[0]}},
                {'portable': True}]})
    books = db.books.find({'library_uuid': {
                '$in': [i['library_uuid'] for i in active_catalogs]}})
    return {'num_of_books': books.count(),
            'num_of_librarians': len(active_catalogs.distinct('librarian'))}

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
