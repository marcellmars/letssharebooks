import sortedcontainers
import collections
import json

library = sortedcontainers.SortedDict()
library['books'] = []
library['collectionids'] = []
books_indexes = {}
indexed_by = sortedcontainers.SortedDict()
indexed_by_title = sortedcontainers.SortedDict()
indexed_by_pubdate = sortedcontainers.SortedDict()


def load_collections():
    return json.load('motw_collections.json')


def dump_collections(c):
    with open('motw_collections.json', 'w') as f:
        json.dump(c, f)


Hateoas = collections.namedtuple("Hateos", "max_results")
hateoas = Hateoas(max_results=24)

# in production load it from its own file or motw_config.json
master_secret = "874a7f15-0c02-473e-ba2c-c1ef937b9a5c"

collections = [
    "quintus",
    "slowrotation",
    "anybody",
    "badco",
    "biopolitics",
    "dubravka",
    "economics",
    "feminism",
    "herman",
    "hortense",
    "kok",
    "libros",
    "marcell",
    "midnightnotes",
    "newleftreview",
    "otpisane",
    "praxis",
    "tamoneki",
]


collection_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "title": "MotW Collection",
    "description": "A Collection for Memory of the World catalog",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "required": ["_id",
                         "title",
                         "title_sort",
                         "timestamp",
                         "tags",
                         "authors",
                         "series_index",
                         "publisher",
                         "pubdate",
                         "library_uuid",
                         "last_modified",
                         "languages",
                         "identifiers",
                         "formats",
                         "cover_url",
                         "comments",
                         "authors"],
            "_id": {"type": "string",
                     "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"},
            "authors": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maximum": 200
                }
            },
            "comments": {
                "type": "string",
                "maximum": 10000},
            "cover_url": {
                "type": "string",
                "maximum": 1000
            },
            "formats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "maximum": 10
                        },
                        "dir_path": {
                            "type": "string",
                            "maximum": 1000},
                        "file_name": {
                            "type": "string",
                            "maximum": 1000
                        },
                        "size": {
                            "type": "integer"
                        }
                    }
                }
            },
            "identifiers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "scheme": {
                            "type": "string",
                            "maximum": 100
                        },
                        "code": {
                            "type": "string",
                            "maximum": 1000
                        }
                    }
                }
            },
            "languages": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maximum": 100
                }
            },
            # "last_modified": {"type": "date-time"},
            "last_modified": {
                "type": "string",
                "maximum": 100
            },
            "library_uuid": {
                "type": "string",
                "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"},
            "pubdate": {
                "type": "string",
                "maximum": 100
            },
            # "pubdate": {"type": "date"},
            "publisher": {
                "type": "string",
                "maximum": 100
            },
            "series_index": {
                "type": "number"
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maximum": 100
                }
            },
            # "timestamp": {"type": "date-time"},
            "timestamp": {
                "type": "string",
                "maximum": 100
            },
            "title": {
                "type": "string",
                "maximum": 1000
            },
            "title_sort": {
                "type": "string",
                "maximum": 1000
            },
        }
    }
}
