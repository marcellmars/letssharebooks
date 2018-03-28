import rapidjson as rjson
import psutil
import os
import time
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
    books = [{k:v for (k, v) in b.items() if k in ['_id',
                                                   'authors',
                                                   'pubdate',
                                                   'title',
                                                   'formats',
                                                   'library_url',
                                                   'cover_url']} for b in books]
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


def add_books(bookson, request=None):
    if request and request.headers.get('Library-Encoding') == 'zlib':
        import zlib
        try:
            bookson = zlib.decompress(bookson).decode('utf-8')
        except zlib.error as e:
            abort(422, "Unzipping JSON failed...")

    if not validate_rjson(bookson):
        abort(422, "AddBooks of JSON didn't validate.")

    books = rjson.loads(bookson,
                        datetime_mode=rjson.DM_ISO8601)

    new_book_ids = set([book['_id'] for book in books])
    old_books_ids = set([book['_id'] for book in motw.library['books']])
    if new_book_ids & old_books_ids != set():
            abort(422, "AddBooks shouldn't bring duplicates...")

    motw.library['books'] += books
    motw.library['books'].sort(key=itemgetter('last_modified'),
                               reverse=True)
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
            if body is None:
                if add_books(result, request):
                    return text("OK")
                abort(422, "AddBooks failed!")
            result += body


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
    return rs.raw(h, headers={'Content-type': 'application/json'})


@app.route('/book/<book_id>')
def book(request, book_id):
    try:
        return rs.raw(rjson.dumps([book for book in motw.library['books']
                                   if book_id == book['_id']][0],
                                  datetime_mode=rjson.DM_ISO8601).encode())
    except Exception as e:
        abort(404, e)


@app.route('/library/<library_uuid>')
def library(request, library_uuid):
    h = hateoas([book for book in motw.library['books']
                 if library_uuid == book['library_uuid']],
                request,
                title="books from {}".format(library_uuid))
    return rs.raw(h, headers={'Content-type': 'application/json'})


@app.route('/librarian/<librarian>')
def librarian(request, librarian):
    h = hateoas([book for book in motw.library['books']
                 if unq(librarian).lower() == book['librarian'].lower()],
                request,
                title="catalogued by {}".format(unq(librarian)))
    return rs.raw(h, headers={'Content-type': 'application/json'})


@app.route('/libraries/')
def libraries(request):
    return json(list(set([b['library_uuid'] for b in motw.library['books']])))


@app.route('/librarians/')
def libraries(request):
    return json(list(set([b['librarian'] for b in motw.library['books']])))


@app.route('/total-books')
async def total_books(request):
    length = len(motw.library['books'])
    return json({'totalNumberOfBooks': '{}'.format(length)})


@app.route('/book-ids')
async def motw_collections(request):
    return json({'lenghts': len(motw.library['books']),
                 'book-ids': [b['_id'] for b in motw.library['books']]})


@app.route('/initial-load')
async def load_collections(request):
    for collection in motw.collections:
        with open("motw_collections/{}.json".format(collection)) as f:
            js = f.read()
            t = time.time()
            if add_books(js):
                time_spent = round(time.time() - t, 3)
                print("{} added in {} seconds.".format(collection, time_spent))
            else:
                abort(422, "Adding books from {} failed!".format(collection))
    return text("OK")


app.add_route(AddBooks.as_view(), '/add-books')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2018)
