#------------------------------------------------------------------------------
# main library functionalities and api
#------------------------------------------------------------------------------

import uuid
import simplejson as json
from bson import json_util

def import_catalog(db, catalog):
    db.books.remove()
    db.catalog.remove()
    
    for book in catalog:
        db.books.insert(book)
    books_uuid = db.books.distinct('uuid')
    catalog = {'uuid': str(uuid.uuid4()),
               'books': books_uuid}
    db.catalog.insert(catalog)
    return len(books_uuid)

def get_catalog(db, uuid):
    return serialize2json(
        [i for i in db.catalog.find({'uuid':uuid})])
    
def serialize2json(data):
    '''
    Pretty print for json
    '''
    return json.dumps(data, sort_keys=True,
                      indent=4, default=json_util.default)
