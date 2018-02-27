import rapidjson
from setproctitle import setproctitle
import time
import gc
import psutil
import os

proc = psutil.Process(os.getpid())
print("start mem {:>20s}: {:>15d}".format("", proc.memory_full_info().rss))

t = time.clock()
setproctitle("motw_test")

ll = [
      # "quintus",
      "slowrotation",
      # "MarcellMarsBooks",
      # "hortense",
      # "newleftreview",
      # "dubravka",
      # "kok",
]

rj = {}

schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "title": "MotW Collection",
    "description": "A Collection for Memory of the World catalog",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "required": ["title",
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
                    "type": "string"
                }
            },
            "comments": {"type": "string"},
            "cover_url": {"type": "string"},
            "formats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string"},
                        "dir_path": {"type": "string"},
                        "file_name": {"type": "string"},
                        "size": {"type": "integer"}
                    }
                }
            },
            "identifiers": {
                "type": "array",
                "items": {"type": "object",
                          "properties": {
                              "scheme": {"type": "string"},
                              "code": {"type": "string"}
                          }
                }
            },
            "languages": {
                "type": "array",
                "items": {"type": "string"}
            },
            # "last_modified": {"type": "date-time"},
            "last_modified": {"type": "string"},
            "library_uuid": {"type": "string",
                             "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"},
            "pubdate": {"type": "string"},
            # "pubdate": {"type": "date"},
            "publisher": {"type": "string"},
            "series_index": {"type": "number"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            # "timestamp": {"type": "date-time"},
            "timestamp": {"type": "string"},
            "title": {"type": "string"},
            "title_sort": {"type": "string"},
        }
    }
}


v = rapidjson.Validator(rapidjson.dumps(schema))

for l in ll:
    with open("/tmp/books_EzraAbbot.json") as f:
        js = f.read()
        t = time.time()
        try:
            v(js)
        except ValueError as e:
            print(e)

        print("time for validation of a full collection: {}".format(time.time() - t))
        rj["{}".format(l)] = rapidjson.loads(js,
                                             datetime_mode=rapidjson.DM_ISO8601,
                                             uuid_mode=rapidjson.UM_CANONICAL )
        del js

    print("mem after {:>20s}: {:>15d}".format(l, proc.memory_full_info().rss))
