# -*- coding: utf-8 -*-

import os

# We want to seamlessy run our API both locally and on Heroku. If running on
# Heroku, sensible DB connection settings are stored in environment variables.
MONGO_HOST = os.environ.get('MONGO_HOST', 'ds153494.mlab.com')
MONGO_PORT = os.environ.get('MONGO_PORT', 53494)
MONGO_USERNAME = os.environ.get('MONGO_USERNAME', 'admin')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD', 'letssharebooks')
MONGO_DBNAME = os.environ.get('MONGO_DBNAME', 'letssharebooks')


# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']

# Enable reads (GET), edits (PATCH) and deletes of individual items
# (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']

# We enable standard client cache directives for all resources exposed by the
# API. We can always override these global settings later.
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20

books = {
    # 'title' tag used in item links.
    # 'item_title': 'book',
    # 'additional_lookup': {
        # 'url': 'regex("[\w]+")',
        # 'field': 'id'
    # },
    # below will exclude library_uuid field from list after GET request
    'datasource': {
        'projection': {'library_uuid': 0}
    },
    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/pyeve/cerberus) for details.
    'schema': {
        'title': {'type': 'string'},
        'authors': {
            'type': 'list',
            'schema': {'type': 'string'},
        },
        'timestamp': {'type': 'datetime'},
        'comments': {'type': 'string'},
        'application_id': {'type': 'int'},
        'last_modified': {'type': 'datetime'},
        'cover_url': {'type': 'string'},
        'publisher': {'type': 'string'},
        'formats': {'type': 'list',
                    'schema': {'type': 'dict',
                               'schema': {
                                   'format': {'type': 'string'},
                                   'dir_path': {'type': 'string'},
                                   'file_name': {'type': 'string'},
                                   'size': {'type': 'int'}
                               }
                    }
         },
        'pubdate': {'type': 'datetime'},
        'librarian': {'type': 'string'},
        'identifiers': {'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'identifier': {'type': 'string'},
                                'value': {'type': 'string'}
                            }
                        }
        },
        'librarian': {'type': 'objectid',
                      'required': True,
                      'data_relation': {
                          'resource': 'collection',
                          'field': 'librarian',
                          'embeddable': True
                      },
        'library_uuid': {'type': 'objectid',
                         'required': True,
                         'data_relation': {
                             'resource': 'collection',
                             'field': 'library_uuid'
                         }
        },
        'motw_uuid': {'type': 'string'}}
    }
}

collections = {
    # if 'item_title' is not provided Eve will just strip the final
    # 's' from resource name, and use it as the item_title.
    'item_title': 'collection',

    # We choose to override global cache-control directives for this resource.
    'cache_control': 'max-age=10,must-revalidate',
    'cache_expires': 10,

    'schema': {
        'books': {'type': 'list',
                  'schema': {
                      'type': 'objectid',
                      'required': True,
                      'data_relation': {
                          'resource': 'books',
                          'field': 'motw_uuid'
                      }
                  }},
        'librarian': {
            'type': 'string',
            'required': True,
        },
        'library_uuid': {
            'type': 'string',
        },
        'last_modified': {'type': 'datetime'},
        'portable_url': {'type': 'string'}
    }
}

# The DOMAIN dict explains which resources will be available and how they will
# be accessible to the API consumer.
DOMAIN = {
    'books': books,
    'librarians': collections,
}
