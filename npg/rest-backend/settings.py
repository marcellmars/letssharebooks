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
EMBEDDING = True

BULK_ENABLED = True

add_books = {
    'item_title': 'Add books',
    'allow_unknown': True,
    'datasource': {'source': 'books'},
    'schema': {
        '_id': {'type': 'uuid'}
    }
}

books = {
    'item_title': 'Book',
    'item_methods': ['GET'],
    'datasource': {
        'default_sort': [('last_modified', -1)]
    },
    'schema': {
        '_id': {'type': 'uuid'},
        'authors': {
            'type': 'list',
            'schema': {'type': 'string'},
        },
        'comments': {'type': 'string'},
        'cover_url': {'type': 'string'},
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
        'identifiers': {
            'type': 'list',
            'schema': {'type': 'dict',
                       'schema': {
                           'scheme': {'type': 'string'},
                           'code': {'type': 'string'}
                       }}
        },
        'languages': {
            'type': 'list',
            'schema': {'type': 'string'}
        },
        'last_modified': {'type': 'string'},
        'library_uuid': {
            # 'type': 'dict',
            'type': 'uuid',
            'required': True,
            'data_relation': {
                'resource': 'libraries',
                'field': '_id',
                'embeddable': True
            },
        },
        'pubdate': {'type': 'string'},
        'publisher': {'type': 'string'},
        'series_index': {'type': 'float'},
        'tags': {
            'type': 'list',
            'schema': {'type': 'string'}
        },
        'timestamp': {'type': 'string'},
        'title': {'type': 'string'},
        'title_sort': {'type': 'string'},
    }
}

libraries = {
    'item_title': 'Library',
    'embedding': True,
    'schema': {
        '_id': {'type': 'uuid'},
        'librarian': {
            'type': 'string',
            'required': True,
            'unique': True
        },
        'last_modified': {'type': 'string'},
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

libraries_presence = {
    'item_title': "Libraries' presence",
    'item_methods': ['GET'],
    'hateoas': False,
    'pagination': False,
    'schema': libraries['schema'],
    'datasource': {'source': 'libraries',
                   'projection': {'_id': 1}},
    'url': "libraries/<regex('.*'):presence>"
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

tags_ngrams = {
    'item_title': 'Ngram',
    'item_methods': ['GET'],
    'max_results': 100,
    'url': 'autocomplete/tags/<regex(".*"):ngram>',
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
    'add_books': add_books,
    'books': books,
    'libraries': libraries,
    'libraries_presence': libraries_presence,
    'libraries_presence': libraries_presence,
    'libraries_books_ids': libraries_books_ids,
    'librarians_books': librarians_books,
    'librarians': librarians_by_name,
    'authors_ngrams': authors_ngrams,
    'titles_ngrams': titles_ngrams,
    'tags_ngrams': tags_ngrams
}
