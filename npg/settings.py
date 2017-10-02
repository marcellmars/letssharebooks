# -*- coding: utf-8 -*-

import os

# We want to seamlessy run our API both locally and on Heroku. If running on
# Heroku, sensible DB connection settings are stored in environment variables.
MONGO_HOST = os.environ.get('MONGO_HOST', 'ds153494.mlab.com')
MONGO_PORT = os.environ.get('MONGO_PORT', 53494)
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'admin')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'letssharebooks')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'letssharebooks')

RESOURCE_METHODS = ['GET', 'POST']

ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20
IF_MATCH = False

books = {
    'schema': {
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
                'resource': 'catalogs',
                'field': 'librarian',
                'embeddable': True
            }
        },
        'library_uuid': {
            'type': 'string',
            'required': True,
            'data_relation': {
                'resource': 'catalogs',
                'field': 'library_uuid'
            },
        },
        'library_secret': {
            'type': 'string'
        },
        'motw_uuid': {
            'unique': True,
            'type': 'string'
        }
    }
}

catalogs = {
    'datasource': {'projection': {'library_uuid': 0}},
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,
    'schema': {
        'librarian': {
            'type': 'string',
            'required': True,
        },
        'library_uuid': {
            'type': 'string',
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
    'schema': books['schema'],
    'datasource': {'source': 'books'},
    'url': "librarians/<regex('.*'):library_uuid>/books",
    'field': 'library_uuid'
}

librarians = {
    'schema': catalogs['schema'],
    'datasource': {'source': 'catalogs',
                   'projection': {'library_uuid': 0}},
    'additional_lookup': {
        'url': 'regex("[\w]+")',
        'field': 'library_uuid'
    }
}

DOMAIN = {
    'books': books,
    'catalogs': catalogs,
    'librarians_books': librarians_books,
    'librarians': librarians
}
