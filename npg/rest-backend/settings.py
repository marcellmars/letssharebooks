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
PAGINATION_DEFAULT = 16
X_DOMAINS = '*'
BANDWIDTH_SAVER = True
SCHEMA_ENDPOINT = "schema"

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
    'item_title': 'Library',
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
    'item_title': "Librarian's books",
    'item_methods': ['GET'],
    'schema': books['schema'],
    'datasource': {'source': 'books'},
    'url': "librarians/<regex('.*'):librarian>/books"
}

librarians_by_name = {
    'item_title': 'Librarian by name',
    'item_methods': ['GET'],
    'schema': libraries['schema'],
    'datasource': {'source': 'libraries'},
    'url': 'librarians/<regex(".*"):librarian>'
}

authors_ngrams = {
    'item_title': 'Ngram',
    'item_methods': ['GET'],
    'item_lookup_field': 'ngram',
    'additional_lookup': {
        'url': 'regex(".*")',
        'field': 'ngram'
    },
    'datasource': {
        'projection': {'authors': 1}
    },
    'schema': {
        '_id': {'type': 'objectid'},
        'ngram': {
            'type': 'string',
            'minlength': 4,
            'maxlength': 4
        },
        'authors': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        }
    }
}

titles_ngrams = {
    'item_title': 'Ngram',
    'item_methods': ['GET'],
    'item_lookup_field': 'ngram',
    'additional_lookup': {
        'url': 'regex(".*")',
        'field': 'ngram'
    },
    'datasource': {
        'projection': {'titles': 1}
    },
    'schema': {
        '_id': {'type': 'objectid'},
        'ngram': {
            'type': 'string',
            'minlength': 4,
            'maxlength': 4
        },
        'titles': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        }
    }
}

DOMAIN = {
    'books': books,
    'libraries': libraries,
    'librarians_books': librarians_books,
    'librarians': librarians_by_name,
    'authors_ngrams': authors_ngrams,
    'titles_ngrams': titles_ngrams
}
