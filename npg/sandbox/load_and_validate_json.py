import os
import time
import psutil
import rapidjson as rjson
from setproctitle import setproctitle
import motw


proc = psutil.Process(os.getpid())
print("RAM memory: {} MB".format(round(proc.memory_full_info().rss/1000000., 2)))
print("")

setproctitle("motw_test")

v = rjson.Validator(rjson.dumps(motw.collection_schema))

for collection in motw.collections:
    with open("motw_collections/{}.json".format(collection)) as f:
        js = f.read()
        t = time.time()
        try:
            v(js)
        except ValueError as e:
            print(e)
        print(collection)
        print("-"*len(collection))
        print("validation time: {} seconds".format(round(time.time() - t, 3)))
        t = time.time()
        motw.library['books'] += rjson.loads(
            js,
            datetime_mode=rjson.DM_ISO8601,
            # uuid_mode=rjson.UM_CANONICAL
        )
        del js
        print("loading time: {} seconds...".format(round(time.time() - t, 3)))

    print("RAM memory: {} MB".format(round(proc.memory_full_info().rss/1000000., 2)))
    print("")
