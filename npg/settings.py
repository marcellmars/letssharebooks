# -*- coding: utf-8 -*-

import os

MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')

# MONGO_HOST = os.environ.get('MONGO_HOST', 'ds153494.mlab.com')
# MONGO_PORT = os.environ.get('MONGO_PORT', 53494)
# MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'admin')
# MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'letssharebooks')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'letssharebooks')

RESOURCE_METHODS = ['GET', 'POST']

ITEM_METHODS = ['GET', 'PATCH', 'DELETE']
ITEM_URL = 'regex("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}")'
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20
IF_MATCH = False

books = {
    'schema': {
        '_id': {'type': 'uuid'},
        'title': {'type': 'string'},
        'title_sort': {'type': 'string'},
        'authors': {
            'type': 'list',
            'schema': {'type': 'string'},
        },
        'timestamp': {'type': 'datetime'},
        'comments': {'type': 'string'},
        'application_id': {'type': 'integer'},
        'last_modified': {'type': 'datetime'},
        'cover_url': {'type': 'string'},
        'publisher': {'type': 'string'},
        'formats': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'format': {'type': 'string'},
                    'dir_path': {'type': 'string'},
                    'file_name': {'type': 'string'},
                    'size': {'type': 'integer'}
                }
            }
        },
        'tags': {
            'type': 'list',
            'schema': {'type': 'string'}
        },
        'card': {
            'type': 'dict',
            'schema': {
                'description': {'type': 'string'}
            }
        },
        'pubdate': {'type': 'datetime'},
        'identifiers': {
            'type': 'list',
            'schema': {'type': 'dict',
                       'schema': {
                           'scheme': {'type': 'string'},
                           'code': {'type': 'string'}
                       }}
        },
        'librarian': {
            'type': 'string',
            'required': True,
            'data_relation': {
                'resource': 'libraries',
                'field': 'librarian',
                'embeddable': True
            }
        },
        'library_uuid': {
            'type': 'string',
            'required': True,
            'data_relation': {
                'resource': 'libraries',
                'field': '_id',
                'embeddable': True
            },
        }
    }
}

libraries = {
    # 'datasource': {'projection': {'library_uuid': 0}},
    'item_title': 'library',
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'schema': {
        '_id': {'type': 'uuid'},
        'librarian': {
            'type': 'string',
            'required': True,
            'unique': True
        },
        'library_secret': {
            'type': 'string'
        },
        'last_modified': {'type': 'string'},
        'portable_url': {'type': 'string'}
    }
}

librarians_books = {
    'item_methods': ['GET'], 
    'schema': books['schema'],
    'item_title': "librarian's books",
    'datasource': {'source': 'books'},
    'url': "librarians/<regex('.*'):librarian>/books",
    'field': 'librarian'
}

librarian_by_name = {
    'item_methods': ['GET'], 
    'schema': libraries['schema'],
    'item_title': 'librarian by name',
    'datasource': {'source': 'libraries'},
    'url': 'librarian/<regex(".*"):librarian>',
    'field': 'librarian'
}

libraries_books = {
    'item_methods': ['GET'], 
    'schema': books['schema'],
    'datasource': {'source': 'books'},
    'url': "libraries/<regex('.*'):library_uuid>/books",
    'field': 'library_uuid'
}


DOMAIN = {
    'books': books,
    'libraries': libraries,
    'librarians_books': librarians_books,
    'librarians': librarian_by_name,
    'libraries_books': libraries_books,

}
