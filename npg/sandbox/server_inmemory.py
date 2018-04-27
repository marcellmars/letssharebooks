import rapidjson as rjson
import psutil
import os
import time
import re
import zlib
import pickle
from signal import signal, SIGINT
from asgiref.sync import sync_to_async

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

motw.library['collectionids'] = motw.load_collections()

# - SANIC/rapidjson


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

    books = [{k: v for (k, v) in b.items() if k in ['_id',
                                                    'authors',
                                                    'pubdate',
                                                    'title',
                                                    'formats',
                                                    'library_url',
                                                    'cover_url']}
             for b in l[p*motw.hateoas.max_results:(p+1)*motw.hateoas.max_results]]

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
                   library_secret in motw.load_collections()[library_uuid]) else False
    if ret:
        return ret
    else:
        abort(403)


@sync_to_async
def validate_books(bookson, schema, enc_zlib):
    if enc_zlib:
        try:
            bookson = zlib.decompress(bookson).decode('utf-8')
        except zlib.error as e:
            abort(422, "Unzipping JSON failed...")

    validate = rjson.Validator(rjson.dumps(schema))
    try:
        validate(bookson)
        return bookson
    except ValueError as e:
        print(e)
        abort(422, "JSON didn't validate.")


@sync_to_async
def remove_books(rookson, library_uuid):
    bookids = rjson.loads(rookson)
    if bookids == []:
        return True

    for bookid in bookids:
        book = motw.books.pop(bookid, None)
        motw.indexed_by_time.pop(
            "{}{}".format(book['last_modified'], bookid),
            None)
        motw.indexed_by_title.pop(
            "{}{}".format(book['title_sort'], bookid),
            None)
        motw.indexed_by_pubdate.pop(
            "{}{}".format(book['pubdate'], bookid),
            None)

    with open("motw_cache/{}".format(library_uuid), "wb") as f:
        pickle.dump([book for book in motw.books.values()
                     if book['library_uuid'] == library_uuid],
                    f)
    return True


@sync_to_async
def add_books(bookson, library_uuid):
    books = rjson.loads(bookson,
                        datetime_mode=rjson.DM_ISO8601)
    if books == []:
        return True
    library_uuid_check = list(set([book['library_uuid'] for book in books]))
    if len(library_uuid_check) != 1 or library_uuid_check[0] != library_uuid:
        return False

    new_book_ids = set((book['_id'] for book in books))
    old_books_ids = motw.books.keys()

    if not old_books_ids:
        with (open("motw_cache/{}".format(library_uuid), 'rb')) as f:
            motw.books.update(pickle.load(f))
        old_books_ids = motw.books.keys()

    ids_to_add = set(new_book_ids - old_books_ids)
    for b in books:
        if b['_id'] not in ids_to_add:
            continue
        motw.books.update(
            {
                b['_id']: b
            }
        )
        motw.indexed_by_time.update(
            {
                str(b['last_modified']) + b['_id']: b['_id']
            })
        motw.indexed_by_title.update(
            {
                b['title_sort'] + b['_id']: b['_id']
            })
        motw.indexed_by_pubdate.update(
            {
                str(b['pubdate']) + b['_id']: b['_id']
            })

    library_url = books[0]['library_url']
    bs = {}
    for b in motw.books.values():
        if b['library_uuid'] == library_uuid:
            b.update(
                {
                    'library_url': library_url
                }
            )
            bs.update(b)

    with open("motw_cache/{}".format(library_uuid), "wb") as f:
        pickle.dump(bs, f)

    # print("index/url written in {} seconds.".format(round(time.time() - t, 3)))
    return True


class AddBooks(HTTPMethodView):

    def get(self, request, verb, library_uuid):
        assert request.stream is None
        return text('Here you should upload, no?')

    @stream_decorator
    async def post(self, request, verb, library_uuid):
        library_secret = (request.headers.get('Library-Secret') or
                          request.headers.get('library-secret'))
        encoding_header = (request.headers.get('library-encoding') or
                           request.headers.get('Library-Encoding'))
        enc_zlib = False
        if encoding_header == 'zlib':
            enc_zlib = True

        check_library_secret(library_uuid, library_secret)

        assert isinstance(request.stream, asyncio.Queue)
        result = b''
        while True:
            body = await request.stream.get()
            if body is None:
                if verb == 'add':
                    bookson = await validate_books(result,
                                                   motw.collection_schema,
                                                   enc_zlib)
                    if bookson:
                        if await add_books(bookson, library_uuid):
                            return text("Books added...")
                elif verb == 'remove':
                    bookson = await validate_books(result,
                                                   motw.remove_schema,
                                                   enc_zlib)

                    if bookson:
                        if await remove_books(bookson, library_uuid):
                            return text("Books removed...")

                abort(422, "{}-ing books failed!".format(verb))
            result += body


@app.route('/library/<verb>/<library_uuid>')
def library(request, verb, library_uuid):
    library_secret = (request.headers.get('Library-Secret') or
                      request.headers.get('library-secret'))
    r = re.match("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}",
                 library_secret)
    if not r or verb not in ['add', 'remove', 'bookids']:
        abort(422, "Wrong verb, ha!")

    if verb == 'add':
        if library_uuid not in motw.library['collectionids']:
            motw.library['collectionids'] = {library_uuid: library_secret}
            with open("motw_cache/{}".format(library_uuid), 'wb') as f:
                pickle.dump([], f)
            motw.dump_collections(motw.library['collectionids'])
            return text("{} added. Let's share books...".format(library_uuid))
        else:
            abort(422, "Library already added.")
    elif verb == 'remove' and library_uuid in motw.library['collectionids']:
            if check_library_secret(library_uuid, library_secret):
                del motw.library['collectionids'][library_uuid]
                motw.dump_collections(motw.library['collectionids'])
            return text("{} removed.".format(library_uuid))
    elif verb == 'bookids' and library_uuid in motw.library['collectionids']:
        if check_library_secret(library_uuid, library_secret):
            bookids = ["{}___{}".format(book['_id'], book['last_modified'])
                       for book in motw.books.values()
                       if library_uuid == book['library_uuid']]
            if bookids == []:
                try:
                    with (open("motw_cache/{}".format(library_uuid), 'rb')) as f:
                        bookids = ["{}___{}".format(book['_id'], book['last_modified'])
                                   for book in pickle.load(f)]
                except Exception as e:
                    print("No cache + {}".format(e))
                    bookids = []
            return json(bookids)
    elif library_uuid not in motw.library['collectionids']:
            abort(404, "{} doesn't exist.".format(library_uuid))


@app.route('/memory')
async def get_memory(request):
    proc = psutil.Process(os.getpid())
    import ipdb;ipdb.set_trace()
    return json({"memory": "{}".format(round(proc.memory_full_info().rss/1000000., 2))})


@app.route('/search/<field>/<q>')
def search(request, field, q):
    try:
        title = "search in {}".format(field)
        if field in ['_id',
                     'title',
                     'titles',
                     'publisher',
                     'series',
                     'library_uuid',
                     'abstract',
                     'librarian']:
            if field == 'titles':
                field = 'title'
            h = hateoas([b for b in motw.books.values()
                         if unq(q).lower() in b[field].lower()],
                        request,
                        title)
            return rs.raw(h, content_type='application/json')

        elif field in ['authors', 'languages', 'tags', '']:
            h = hateoas([b for b in motw.books.values()
                         if unq(q).lower() in " ".join(b[field]).lower()],
                        request,
                        title)
            return rs.raw(h, content_type='application/json')

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
        r = [b[field] for b in motw.books.values()
             if unq(sq.lower()) in b[field].lower()]
    elif field in ['authors', 'tags']:
        for bf in [b[field] for b in motw.books.values()]:
            for f in bf:
                if unq(sq.lower()) in f.lower():
                    r.add(f)
    r = {'_items': list(r)}
    return json(r)


@app.route('/books')
def books(request):
    # h = hateoas([b for b in motw.books.values()],
    h = hateoas([motw.books[bid] for bid in reversed(motw.indexed_by_time.values())],
                request)
    return rs.raw(h, content_type='application/json')


@app.route('/book/<book_id>')
def book(request, book_id):
    try:
        return rs.raw(rjson.dumps(
            motw.books[book_id],
            datetime_mode=rjson.DM_ISO8601).encode(),
                      content_type='application/json')
    except Exception as e:
        abort(404, e)


app.add_route(AddBooks.as_view(), '/books/<verb>/<library_uuid>')

asyncio.set_event_loop(uvloop.new_event_loop())
server = app.create_server(host="0.0.0.0", port=2018)
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(server)

signal(SIGINT, lambda s, f: loop.stop())
try:
    loop.run_forever()
except:
    loop.stop()
