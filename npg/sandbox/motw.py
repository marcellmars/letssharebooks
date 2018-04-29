import sortedcontainers
import collections
import json

libraries = sortedcontainers.SortedDict()
books = sortedcontainers.SortedDict()
indexed_by_time = sortedcontainers.SortedDict()
indexed_by_title = sortedcontainers.SortedDict()
indexed_by_pubdate = sortedcontainers.SortedDict()


def dump_libraries(c):
    with open('motw_libraries.json', 'w') as f:
        json.dump(c, f)


def load_libraries():
    try:
        return json.load(open('motw_libraries.json'))
    except:
        dump_libraries({})
        return json.load(open('motw_libraries.json'))


Hateoas = collections.namedtuple("Hateos", "max_results")
hateoas = Hateoas(max_results=48)

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

remove_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "title": "MotW Books to be removed",
    "description": "A List of books to be removed from MotW",
    "type": "array",
    "items": {
        "type": "string",
        "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
    }
}


collection_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "title": "MotW Collection",
    "description": "A Book Collection for Memory of the World catalog",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "required": [
                "_id",
                "title",
                "title_sort",
                "timestamp",
                "tags",
                "authors",
                "publisher",
                "pubdate",
                "library_uuid",
                "last_modified",
                "languages",
                "identifiers",
                "formats",
                "cover_url",
                "abstract",
                "authors"
            ],
            "_id": {
                "type": "string",
                "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
            },
            "authors": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maximum": 200
                }
            },
            "abstract": {
                "type": "string",
                "maximum": 10000
            },
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
            "publisher": {
                "type": "string",
                "maximum": 100
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "maximum": 100
                }
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
