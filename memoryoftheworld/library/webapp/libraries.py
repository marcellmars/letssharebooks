# ------------------------------------------------------------------------------
# main library functionalities and api
# ------------------------------------------------------------------------------

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
from bson.objectid import ObjectId
from datetime import datetime

# ------------------------------------------------------------------------------

LOG = logging.getLogger('motw.' + __name__)
LOG.setLevel(logging.DEBUG)

# ------------------------------------------------------------------------------

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
    'prefix_url': 1,
    'cover_url': 1,
    'last_modified': 1
    }

# book fields for book in the modal window
PUBLIC_SINGLE_BOOK_FIELDS = {
    'application_id': 1,
    'title': 1,
    'formats': 1,
    'authors': 1,
    'tunnel': 1,
    'uuid': 1,
    'publisher': 1,
    'comments': 1,
    'librarian': 1,
    'library_uuid': 1,
    'portable': 1,
    'portable_url': 1,
    'prefix_url': 1,
    'cover_url': 1,
    'card': 1,
    'format_metadata': 1,
    '_id': 0
    }

# ------------------------------------------------------------------------------


def init(db):
    '''
    Perform some actions on startup
    '''
    # pre-calculate autocomplete
    calculate_autocomplete(db)

# ------------------------------------------------------------------------------


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

# ------------------------------------------------------------------------------


def handle_uploaded_catalog(db, uploaded_file, zipped=True):
    '''
    Opens, unzips and parses uploaded catalog and imports books to the db

    :param uploaded_file: file provided by cherrypy
    :param zipped: true if file is zipped
    '''
    LOG.info('>>> Processing uploaded file')
    # if uploaded file is zipped json catalog
    if zipped:
        # save files to tmp folder
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        content = uploaded_file.file.read()
        # generate unique filename and write
        filename = 'tmp/%s-%s' % (uploaded_file.filename, uuid.uuid4())
        with open(filename, "wb") as f:
            f.write(content)
        # unzip file
        with zipfile.ZipFile(filename) as zfile:
            content = zfile.read('library.json')
    # else if json is directly uploaded
    else:
        content = uploaded_file
    # decode from json
    catalog = simplejson.loads(content)
    # import to database
    res, err = import_catalog(db, catalog)
    return res

# ------------------------------------------------------------------------------


def import_catalog(db, catalog, portable_url=None):
    '''
    Imports user catalog to the database.

    :param db: database connection
    :param catalog: catalog dict received from calibre plugin
    :param portable_url: url of the portable library (if portable)

    :returns (library_uuid, err_msg)
    '''
    LOG.info('>>> Importing catalog {}'.format(catalog['library_uuid']))
    catalog['portable_url'] = portable_url
    catalog['portable'] = False
    # check of uploaded catalog is provided as portable library
    if catalog['tunnel'] == -1337 or portable_url:
        catalog['portable'] = True
    # check if catalog already exists in the db
    db_cat = db.catalog.find_one({'library_uuid': catalog['library_uuid']})
    if db_cat:
        if catalog['portable']:
            # cannot add portable more than once
            return None, 'portable already registered'
        # first remove books (as requested in the uploaded catalog)
        remove_from_library(
            db, catalog['library_uuid'], catalog['books']['remove'])
    # add books as requested (for new library and for sync)
    add_to_library(db, catalog)
    # update catalog metadata
    update_catalog(db, catalog)
    # update books metadata
    update_books(db, catalog)
    # pre-calculate autocomplete
    calculate_autocomplete(db)
    return catalog['library_uuid'], None

# ------------------------------------------------------------------------------


def update_catalog(db, catalog):
    '''
    Sets tunnel to 0 if there is a library with the same tunnel from before.
    Updates catalog metadata.

    :param db: database connection
    :param catalog: catalog dict received from calibre plugin
    '''
    LOG.info('>>> Updating catalog {}'.format(catalog['library_uuid']))
    # find libraries that have tunnel number equal to uploaded catalog's
    old_libraries = [i['library_uuid']
                     for i in db.catalog.find({'tunnel': catalog['tunnel']})
                     if i['library_uuid'] != catalog['library_uuid']]
    # reset their tunnel number to 0
    db.catalog.update({'library_uuid': {'$in': old_libraries}},
                      {'$set': {'tunnel': 0}}, multi=True)
    # update catalog metadata
    db.catalog.update({'library_uuid': catalog['library_uuid']},
                      {'$set': {'last_modified': catalog['last_modified'],
                                'tunnel': catalog['tunnel'],
                                'librarian': catalog['librarian'],
                                'portable': catalog['portable'],
                                'portable_url': catalog['portable_url']}},
                      upsert=True, multi=False)

# ------------------------------------------------------------------------------


def update_books(db, catalog):
    '''
    Updates book metadata for all books in the given library when sharing
    status is changed. Dynamic book properties that are updated or
    recalculated are:

        - tunnel number
        - librarian's name
        - prefix_url (depends on the tunnel)
        - portable_url
        - portable flag
    '''

    def gen_prefix_url(catalog):
        '''
        Generates prefix (base) url depending on the type of the library and
        currently active tunnel
        '''
        if catalog['portable_url']:
            return '{}/'.format(catalog['portable_url'])
        else:
            return 'https://www{}.{}/'.format(
                catalog['tunnel'], settings.ENV['domain_url'])

    def gen_cover_url(book, prefix_url):
        '''
        Generates cover url
        '''
        fmt = book['formats'][0]
        return '{}{}cover.jpg'.format(
            prefix_url, book['format_metadata'][fmt]['dir_path'])

    LOG.info('>>> Updating books {}'.format(catalog['library_uuid']))
    books_to_update = db.books.find(
        {'library_uuid': catalog['library_uuid']})
    for book in books_to_update:
        prefix_url = gen_prefix_url(catalog)
        db.books.update(
            {'uuid': book['uuid']},
            {'$set': {'tunnel': catalog['tunnel'],
                      'librarian': catalog['librarian'],
                      'portable': catalog['portable'],
                      'portable_url': catalog['portable_url'],
                      'prefix_url': prefix_url,
                      'cover_url': gen_cover_url(book, prefix_url)}},
            multi=False,
            upsert=False)

# ------------------------------------------------------------------------------


def add_to_library(db, catalog):
    '''
    Adds books to the database and modifies catalog entry. Mostly used with
    import_catalog function.

    :param db: database connection
    :param catalog: uploaded catalog
    '''
    LOG.info('>>> Adding books {} to {}'.format(len(catalog['books']['add']),
                                                catalog['library_uuid']))
    books_uuids = []  # will hold inserted books' uuids
    books = []

    # add each book to the db.books collection
    for book in catalog['books']['add']:
        # embed library_uuid to every book
        book['library_uuid'] = catalog['library_uuid']
        book = utils.remove_dots_from_dict(book)
        books_uuids.append((book['uuid'], book['last_modified']))
        books.append(book)

    db.books.insert_many(books, ordered=False)
    LOG.info('>>> Added books {} to {}'.format(len(catalog['books']['add']),
                                               catalog['library_uuid']))
    db.catalog.update_one({'library_uuid': catalog['library_uuid']},
                          {'$set': {'books': books_uuids}},
                          upsert=True)
    # try:
        #     db.books.update_one({'uuid': book['uuid']},
        #                         {'$set': utils.remove_dots_from_dict(book)},
        #                         upsert=True)
        #     # collect (uuid, last_modified) for catalog entry
        # LOG.info('>>> Added book {}'.format(book['uuid']))
        # except Exception:
        #     LOG.error('error in book update ({})'
        #               .format(book['uuid']),
        #               exc_info=True)
    # update catalog metadata collection

# ------------------------------------------------------------------------------


def remove_from_library(db, library_uuid, books_uuids):
    '''
    Remove books from the library and update catalog

    :param db: database connection
    :param library_uuid: uuid of the library
    :param books_uuids: uuids of the books that need to be removed
    '''
    LOG.info('>>> Removing books ({})'.format(len(books_uuids)))
    # remove books
    [db.books.remove({'uuid': uuid}) for uuid in books_uuids]
    # update catalog metadata
    db.catalog.update(
        {'library_uuid': library_uuid},
        {'$pull': {'books': {'$in': books_uuids}}},
        upsert=True, multi=False)

# ------------------------------------------------------------------------------


def get_catalog(db, uuid):
    '''
    Read catalog entry from the database and return json representation
    '''
    return utils.ser2json(db.catalog.find_one(
        {'library_uuid': uuid},
        {'books': 1,
         'last_modified': 1,
         '_id': 0}))

# ------------------------------------------------------------------------------


def get_catalogs(db):
    '''
    for testing purposes
    '''
    return utils.ser2json(db.catalog.find(
        {},
        {'library_uuid': 1,
         'librarian': 1,
         '_id': 0}))

# ------------------------------------------------------------------------------


def get_book(db, uuid):
    '''
    Returns book with the param uuid
    '''
    book = db.books.find_one({'uuid': uuid}, PUBLIC_SINGLE_BOOK_FIELDS)
    if book:
        return utils.sanitize_html(book)
    return None

# ------------------------------------------------------------------------------


def get_books(db, last_id, query={}):
    '''
    Reads and returns books from the database.
    '''
    # query
    q = {}
    LOG.debug('>'*30)
    LOG.debug('>>> QUERY: {}, LAST_ID: {}'.format(query, last_id))

    # extract search parameters and build query
    # text + property
    q_text = query.get('text')
    q_property = query.get('property', 'all')
    if q_text:
        q_words = q_text.encode('utf-8').split(' ')
        match_pattern = {'$regex': '.*'.join(q_words), '$options': 'i'}

        if q_property in ['authors', 'title', 'tags']:
            q[q_property] = match_pattern

        elif q_property == 'pubdate':
            # validate entered date, but query as string
            try:
                date = datetime.strptime(q_text, '%Y-%m-%d')
                q[q_property] = {'$regex': '^{}.*'.format(q_text),
                                 '$options': 'i'}
            except Exception as e:
                LOG.error('invalid date: {}'.format(q_text))

        elif q_property == 'formats':
            q[q_property] = {'$all': [i.upper() for i in q_words]}

        else:
            q = {"$or": [{'title': match_pattern},
                         {'authors': match_pattern},
                         {'comments': match_pattern},
                         {'tags': match_pattern},
                         {'publisher': match_pattern},
                         {'identifiers': match_pattern}]}

    # dropdown value + property
    q_dproperty = query.get('dproperty')
    q_dvalue = query.get('dvalue')
    if q_dvalue:
        if q_dproperty == 'librarians':
            q['librarian'] = q_dvalue.encode('utf-8')
        elif q_dproperty == 'collections':
            q['collection'] = q_dvalue.encode('utf-8')
        else:
            LOG.error('unsupported dropdown property: {}'.format(q_dproperty))

    # get all libraries that have active ssh tunnel or reference portables
    active_tunnels = get_active_tunnels()
    LOG.debug('>>> Active_tunnels: {}'.format(active_tunnels))
    active_catalogs = db.catalog.find(
        {'$or': [
            {'tunnel':   {'$in': active_tunnels}},
            {'portable': True}]})
    q['library_uuid'] = {'$in': [i['library_uuid'] for i in active_catalogs]}

    # infinite scroll query part
    if last_id:
        q['_id'] = {'$lt': ObjectId(last_id)}

    # fetch final cursor
    LOG.debug('>>> FINAL QUERY: {}'.format(q))
    dbb = db.books.find(q, PUBLIC_BOOK_FIELDS).sort('last_modified', -1)

    # do infinite loading
    books = list(dbb.limit(settings.ITEMS_PER_PAGE))
    
    # calculate last_id
    current_last_id = None
    if books and len(books) == settings.ITEMS_PER_PAGE:
        current_last_id = str(books[len(books) - 1]['_id'])

    return utils.ser2json({
        'books': books,
        'last_id': current_last_id,
    })

# ------------------------------------------------------------------------------
#- get_active_ports() is called after url/get_active_librarians
#- from calibre plugin when librarian start to share her catalog.
#- regular pickle is too slow for this
# ------------------------------------------------------------------------------


def get_active_ports():
    data = {'get': 'active_tunnel_ports'}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('sshd', 3773))
    s.send(json.dumps(data))
    ports = []
    data = ""
    while True:
        rdata = s.recv(8192)
        print("rdata: {}".format(rdata))
        if rdata:
            data += rdata
        else:
            try:
                data = json.loads(data)
                ports = list(data)
            except Exception as e:
                print("Exception: {}\ndata, rdata: {}, {}".format(e,
                                                                  data,
                                                                  rdata))
            break
    s.close()
    return ports


def get_active_librarians(db):
    time.sleep(0.5)
    active_catalogs = db.catalog.find(
        {'$or': [
            {'tunnel': {'$in': [p for p in get_active_ports()]}},
            {'portable': True}]})
    librarians = active_catalogs.distinct('librarian')
    #print([c['librarian'] for c in active_catalogs], librarians)
    return utils.ser2json({'librarians': librarians})

# ------------------------------------------------------------------------------


def get_status(db):
    '''
    Return some status info
    '''
    active_catalogs = db.catalog.find(
        {'$or': [
            {'tunnel': {'$in': get_active_tunnels()}},
            {'portable': True}]})
    books = db.books.find(
        {'library_uuid': {
            '$in': [i['library_uuid'] for i in active_catalogs]}})
    return {'num_of_books': books.count(),
            'num_of_librarians': len(active_catalogs.distinct('librarian'))}

# ------------------------------------------------------------------------------


def get_autocomplete(db):
    '''
    Returns pre-computed autocomplete data
    '''
    return utils.ser2json(db.autocomplete.find_one({}, {'_id': 0}))

# ------------------------------------------------------------------------------


def calculate_autocomplete(db):
    '''
    Calculates autocomplete data and insert them into db.autocomplete
    collection
    '''
    q = {}
    active_tunnels = get_active_tunnels()
    active_catalogs = db.catalog.find(
        {'$or': [{'tunnel': {'$in': active_tunnels}},
                 {'portable': True}]})
    q['library_uuid'] = {'$in': [i['library_uuid'] for i in active_catalogs]}
    dbb = db.books.find(
        q, {'authors': 1, 'title': 1, 'tags': 1, 'formats': 1})
    # calculate books' tags and formats
    tags = set()
    formats = set()
    for book in dbb:
        tags.update(book.get('tags', set()))
        formats.update(book.get('formats', set()))
    # update db
    db.autocomplete.drop()
    db.autocomplete.insert({
        'authors': dbb.distinct('authors'),
        'titles': dbb.distinct('title'),
        'tags': list(tags),
        'formats': list(formats),
        'librarians': active_catalogs.distinct('librarian'),
        'num_books': dbb.count()
    })

# ------------------------------------------------------------------------------
# PORTABLE management
# ------------------------------------------------------------------------------


def add_portable(db, portable_url):
    '''
    Registers and import portable library

    :param db: database connection
    :param portable_url: url of the portable library
    '''
    LOG.info('>>> Registering portable {}'.format(portable_url))
    try:
        headers = {"Accept-Encoding": "gzip"}
        libjs = requests.get(portable_url + '/static/data.js',
                             headers=headers,
                             stream=True).text.strip()
        # remove javascript wrapper around json
        libjson = libjs[libjs.find('{'):-1]
        catalog = simplejson.loads(libjson)
        res, err = import_catalog(db, catalog, portable_url)
        if err:
            return err
        return res
    except requests.ConnectionError:
        return utils.ser2json(
            'Error while registering portable: connection error')
    except Exception:
        LOG.error('Registering portable', exc_info=True)
    return utils.ser2json('Error while registering portable. Check logs...')

# ------------------------------------------------------------------------------


def get_portables(db):
    '''
    Returns all registered portable libraries
    '''
    return utils.ser2json(list(db.catalog.find(
        {'portable': True},
        {'librarian': 1,
         'library_uuid': 1,
         '_id': 0})))

# ------------------------------------------------------------------------------


def remove_portable(db, url):
    '''
    Removes registered portable library with given lib_uuid
    '''
    q = {'portable_url': url}
    portable_cat = db.catalog.find_one(q)
    if portable_cat:
        db.books.remove({'library_uuid': portable_cat['library_uuid']})
        db.catalog.remove({'library_uuid': portable_cat['library_uuid']})
        return utils.ser2json('Library removed.')
    else:
        return utils.ser2json('Portable not found or doomed.')

# ------------------------------------------------------------------------------
