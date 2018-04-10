import rapidjson as rjson
import psutil
import os
import time
import re
import zlib
from signal import signal, SIGINT

from operator import itemgetter
from setproctitle import setproctitle
from urllib.parse import unquote_plus as unq

from sanic import Sanic
from sanic import response as rs
from sanic.response import json
from sanic.response import text
from sanic.views import HTTPMethodView
from sanic.views import stream as stream_decorator
from sanic.exceptions import abort
from sanic_cors import CORS

import motw
import asyncio
import uvloop

setproctitle("sanic_motw")


app = Sanic()
CORS(app)
app.config.REQUEST_MAX_SIZE = 1000000000


# - SANIC/rapidjson


def validate_rjson(js):
    v = rjson.Validator(rjson.dumps(motw.collection_schema))
    try:
        v(js)
        return True
    except ValueError as e:
        print(e)
        return False


def hateoas(l, request, title="books"):
    r = {}
    try:
        p = int(request.args['page'][0]) - 1
    except:
        p = 0

    last_p = int(len(l)/motw.hateoas.max_results + 1)

    if p > last_p:
        p = last_p
    elif p < 0:
        p = 0

    books = l[p*motw.hateoas.max_results:(p+1)*motw.hateoas.max_results]
    books = [{k: v for (k, v) in b.items() if k in ['_id',
                                                    'authors',
                                                    'pubdate',
                                                    'title',
                                                    'formats',
                                                    'library_url',
                                                    'cover_url']}
             for b in books]
    r = {
        "_items": books,
        "_links": {
            "parent": {
                "title": "Memory of the World Library",
                "href": "/"
            },
            "self": {
                "title": title,
                "href": request.path[1:]
            },
            "prev": {
                "title": "previous page",
                "href": "{}?page={}".format(request.path, p)
            },
            "next": {
                "title": "next page",
                "href": "{}?page={}".format(request.path, p+2)
            },
            "last": {
                "title": "last page",
                "href": "{}?page={}".format(request.path, last_p)
            }
        },
        "_meta": {
            "page": p+1,
            "max_results": motw.hateoas.max_results,
            "total": len(l),
            "status": title
        }
    }

    if p == 0:
        del r['_links']['prev']
    if p == last_p - 1:
        del r['_links']['next']

    return rjson.dumps(r,
                       datetime_mode=rjson.DM_ISO8601).encode()


def check_library_secret(library_uuid, library_secret):
    ret = True if (library_secret == motw.master_secret or
                   library_secret == motw.load_collections()) else False
    if ret:
        return ret
    else:
        abort(403)


def add_books(bookson, request):
    encoding_header = (request.headers.get('library-encoding') or
                       request.headers.get('Library-Encoding'))

    if encoding_header == 'zlib':
        try:
            bookson = zlib.decompress(bookson).decode('utf-8')
        except zlib.error as e:
            abort(422, "Unzipping JSON failed...")

    if not validate_rjson(bookson):
        abort(422, "AddBooks of JSON didn't validate.")

    books = rjson.loads(bookson,
                        datetime_mode=rjson.DM_ISO8601)

    new_book_ids = set((book['_id'] for book in books))
    old_books_ids = set((book['_id'] for book in motw.library['books']))
    ids_to_add = set(new_book_ids - old_books_ids)

    motw.library['books'] += [book for book in books
                              if book['_id'] in ids_to_add]

    motw.library['books'].sort(key=itemgetter('last_modified'),
                               reverse=True)

    for i, b in enumerate(motw.library['books']):
        motw.books_indexes['_id'] = i
        motw.indexed_by_title.update({b['title_sort'] + b['_id']: i})
        motw.indexed_by_pubdate.update({str(b['pubdate']) + b['_id']: i})

    return True


class AddBooks(HTTPMethodView):

    def get(self, request):
        assert request.stream is None
        return text('Here you should upload, no?')

    @stream_decorator
    async def post(self, request):
        assert isinstance(request.stream, asyncio.Queue)
        result = b''
        while True:
            body = await request.stream.get()
            print(".", end="")
            if body is None:
                if add_books(result, request):
                    return text("OK")
                abort(422, "AddBooks failed!")
            result += body


@app.route('/library/<verb>/<library_uuid>')
def library(request, verb, library_uuid):
    try:
        library_secret = (request.headers.get('Library-Secret') or
                          request.headers.get('library-secret'))
        r = re.match("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}", library_secret)
        if not r or verb not in ['add', 'remove']:
            abort(422)

        if verb == 'add':
            if library_uuid not in motw.library['collections']:
                motw.library['collections']['library_uuid'] = library_secret
                motw.library.dump_collections()
        elif verb == 'remove':
                if check_library_secret(library_uuid, library_secret):
                    del motw.library['collections']['library_uuid']
                    motw.library.dump_collections()

    except Exception as e:
        abort(404, e)


@app.route('/memory')
async def get_memory(request):
    proc = psutil.Process(os.getpid())
    return json({"memory": "{}".format(
        round(proc.memory_full_info().rss/1000000.,
              2)),
    })


@app.route('/search/<field>/<q>')
def search(request, field, q):
    try:
        title = "search in {}".format(field)
        if field in ['_id',
                     'title',
                     'titles',
                     'publisher',
                     'library_uuid',
                     'comments',
                     'librarian']:
            if field == 'titles':
                field = 'title'
            h = hateoas([b for b in motw.library['books']
                         if unq(q).lower() in b[field].lower()],
                        request,
                        title)
            # h = hateoas([
            #     motw.library['books'][i] for i in motw.indexed_by['title']
            #     if unq(q).lower() in motw.library['books'][i][field].lower()],
            #             request,
            #             title
            # )
            return rs.raw(h)

        elif field in ['authors', 'languages', 'tags', '']:
            h = hateoas([b for b in motw.library['books']
                         if unq(q).lower() in " ".join(b[field]).lower()],
                        request,
                        title)
            return rs.raw(h)

    except Exception as e:
        abort(404, e)


@app.route('/autocomplete/<field>/<sq>')
def autocomplete(request, field, sq):
    r = set()
    if len(sq) < 4:
        return json({})
    if field in ['titles', 'publisher']:
        if field == 'titles':
            field = 'title'
            if unq(sq.lower()) in ['the ']:
                return json({})
        r = [b[field] for b in motw.library['books']
             if unq(sq.lower()) in b[field].lower()]
    elif field in ['authors', 'tags']:
        for bf in [b[field] for b in motw.library['books']]:
            for f in bf:
                if unq(sq.lower()) in f.lower():
                    r.add(f)
    r = {'_items': list(r)}
    return json(r)


@app.route('/books')
def books(request):
    h = hateoas([b for b in motw.library['books']],
                request,
                title="books")
    # h = hateoas([motw.library['books'][i] for i in motw.indexed_by['title'],
    #             request,
    #             title="books")

    return rs.raw(h, headers={'Content-type': 'application/json'})


@app.route('/book/<book_id>')
def book(request, book_id):
    try:
        return rs.raw(rjson.dumps(
            motw.library['books'][motw.books_indexes[book_id]],
            datetime_mode=rjson.DM_ISO8601).encode())
    except Exception as e:
        abort(404, e)


@app.route('/initial-load')
async def load_collections(request):
    for collection in motw.collections:
        with open("motw_collections/{}.json".format(collection)) as f:
            js = f.read()
            t = time.time()
            if add_books(js, request):
                time_spent = round(time.time() - t, 3)
                print("{} added in {} seconds.".format(collection, time_spent))
            else:
                abort(422, "Adding books from {} failed!".format(collection))
    return text("OK")


app.add_route(AddBooks.as_view(), '/add-books')

asyncio.set_event_loop(uvloop.new_event_loop())
server = app.create_server(host="0.0.0.0", port=2018)
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(server)

signal(SIGINT, lambda s, f: loop.stop())
try:
    loop.run_forever()
except:
    loop.stop()
