# -*- coding: utf-8 -*-

import os

MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')

# MONGO_HOST = os.environ.get('MONGO_HOST', 'ds153494.mlab.com')
# MONGO_PORT = os.environ.get('MONGO_PORT', 53494)
# MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'admin')
# MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'letssharebooks')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'letssharebooks')

RESOURCE_METHODS = ['GET', 'POST']

ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
ITEM_URL = 'regex("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}")'
CACHE_CONTROL = 'max-age=20'
CACHE_CONTROL = ''
CACHE_EXPIRES = 20
IF_MATCH = False
PAGINATION_DEFAULT = 12
PAGINATION_LIMIT = 1000
X_DOMAINS = '*'
BANDWIDTH_SAVER = True
SCHEMA_ENDPOINT = "schema"
XML = False
EMBEDDED = True

books = {
    'item_title': 'Book',
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
            'data_relation': {
                'resource': 'libraries',
                'field': 'librarian',
            }
        },
        'library_uuid': {
            'type': 'uuid',
            'required': True,
            'data_relation': {
                'resource': 'libraries',
                'field': '_id',
                'embeddable': True
            },
        },
        'presence': {
            'type': 'string',
            'default': 'off',
            'data_relation': {
                'resource': 'libraries',
                'field': 'presence',
            }
        },
        'library_url': {
            'type': 'string',
            'default': 'off',
            'data_relation': {
                'resource': 'libraries',
                'field': 'library_url',
            }
        }
    }
}

libraries = {
    'item_title': 'Library',
    'datasource': {'projection': {'library_secret': 0}},
    'schema': {
        '_id': {'type': 'uuid'},
        'librarian': {
            'type': 'string',
            'required': True,
            'unique': True
        },
        'last_modified': {'type': 'datetime'},
        'library_url': {'type': 'string'},
        'presence': {'type': 'string',
                     'default': 'off',
                     'allowed': {'on', 'off', 'check'}}
    }
}

libraries_books_ids = {
    'item_title': "Books from library",
    'item_methods': ['GET'],
    'pagination': False,
    'hateoas': False,
    'schema': {
        '_id': {
            'type': 'uuid',
            'data_relation': {
                'resource': 'books',
                'field': '_id'}
        },
        'library_uuid': {
            'type': 'uuid',
            'data_relation': {
                'resource': 'books',
                'field': 'library_uuid'
            }
        }
    },
    'datasource': {'source': 'books',
                   'projection': {'_id': 1}
    },
    'url': "libraries/<regex('.*'):library_uuid>/ids"
}

librarians_books = {
    'item_title': "Librarian's books",
    'item_methods': ['GET'],
    'schema': books['schema'],
    'datasource': {'source': 'books'},
    'url': "librarians/<regex('.*'):librarian>/books"
}

libraries_presence = {
    'item_title': "Libraries' presence",
    'item_methods': ['GET'],
    'schema': books['schema'],
    'datasource': {'source': 'books'},
    'url': "libraries/<regex('.*'):presence>/books"
}

books_presence = {
    'item_title': "Books' presence",
    'item_methods': ['GET'],
    'schema': books['schema'],
    'datasource': {'source': 'books'},
    'url': "books/<regex('.*'):presence>"
}


librarians_by_name = {
    'item_title': 'Librarian by name',
    'item_methods': ['GET'],
    'hateoas': False,
    'pagination': False,
    'schema': libraries['schema'],
    'datasource': {'source': 'libraries'},
    'url': 'librarians/<regex(".*"):librarian>'
}

authors_ngrams = {
    'item_title': 'Ngram',
    'item_methods': ['GET'],
    'url': 'autocomplete/authors/<regex(".*"):ngram>',
    # 'hateoas': False,
    # 'pagination': False,
    'datasource': {
        'projection': {'val': 1}
    },
    'schema': {
        '_id': {'type': 'objectid'},
        'ngram': {
            'type': 'string',
            'minlength': 4,
            'maxlength': 4
        },
        'val': {'type': 'string'}
    }
}

titles_ngrams = {
    'item_title': 'Ngram',
    'item_methods': ['GET'],
    'max_results': 100,
    'url': 'autocomplete/titles/<regex(".*"):ngram>',
    # 'hateoas': False,
    # 'pagination': False,
    'datasource': {
        'projection': {'val': 1}
    },
    'schema': {
        '_id': {'type': 'objectid'},
        'ngram': {
            'type': 'string',
            'minlength': 4,
            'maxlength': 4
        },
        'val': {'type': 'string'}
    }
}


DOMAIN = {
    'books': books,
    'libraries': libraries,
    'libraries_presence': libraries_presence,
    'books_presence': books_presence,
    'libraries_books_ids': libraries_books_ids,
    'librarians_books': librarians_books,
    'librarians': librarians_by_name,
    'authors_ngrams': authors_ngrams,
    'titles_ngrams': titles_ngrams
}
