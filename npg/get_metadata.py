# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import html
import json
import dateutil.parser
import requests

dc = {
    'base_url': "http://localhost:5000/",
    'calibre_path': "/home/m/CalibreLibraries/FooBar/",
    'librarian': 'Ezra Abbot',
    'library_uuid': 'e3b641c4-86ed-465a-9440-36a4fdd512a7',
    'library_secret': '690e7981-08b8-4e73-a2cd-dff864a902e1',
    'jsonpath': '/tmp/',
    'jsonname': 'books.json'
}


def add_new(resource, payload, base_url=dc['base_url']):
    headers = {'Content-Type': 'application/json'}
    r = requests.post(base_url + resource, payload, headers=headers)
    print("posted @{} with status code: {}\nand content: {}".format(resource,
                                                                    r.status_code,
                                                                    r.content))

    sccs = []
    if r.status_code == 201:
        response = r.json()
        if response['_status'] == 'OK':
            for res in response['_items']:
                if res['_status'] == "OK":
                    sccs.append(res['_id'])
    return sccs


def delete_item(resource, item, base_url=dc['base_url']):
    r = requests.delete("{}{}/{}".format(base_url, resource, item))
    print("deleted {} @{} with status code: {}\nand content: {}".format(item,
                                                                        resource,
                                                                        r.status_code,
                                                                        r.content))


def calibre_to_json(directory_path, librarian, library_uuid, library_secret, db_file='metadata.db'):
    conn = sqlite3.connect(os.path.join(directory_path, db_file), sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    books = [book for book in cur.execute("SELECT * FROM BOOKS")]
    bookz = []
    for book in books:
        b = {}
        b['library_uuid'] = library_uuid
        b['library_secret'] = library_secret
        b['librarian'] = librarian
        b['motw_uuid'] = book[11]
        b['application_id'] = book[0]
        if not book[1]:
            book[1] = "Unknown"
        b['title'] = book[1]
        if not book[2]:
            book[2] = "Unknown"
        b['title_sort'] = book[2]
        b['timestamp'] = dateutil.parser.parse(book[3]).strftime("%a, %d %b %04Y %H:%M:%S GMT")
        b['pubdate'] = dateutil.parser.parse(book[4]).strftime("%a, %d %b %04Y %H:%M:%S GMT")
        # b['path'] = book[9]
        if not book[13]:
            b['last_modified'] = b['timestamp']
        else:
            b['last_modified'] = dateutil.parser.parse(book[13]).strftime("%a, %d %b %04Y %H:%M:%S GMT")

        # b['last_modified'] = book[13]

        # authors
        authors = cur.execute("""SELECT AUTHORS.NAME
                                 FROM BOOKS,
                                      BOOKS_AUTHORS_LINK,
                                      AUTHORS
                                 WHERE BOOKS.ID = {book} AND
                                       BOOKS.ID = BOOKS_AUTHORS_LINK.BOOK AND
                                       AUTHORS.ID = BOOKS_AUTHORS_LINK.AUTHOR;""".format(book=book[0])).fetchall()
        if not authors:
            authors = [["Unknown"]]
        b['authors'] = [a[0] for a in authors]

        # comments/description of the book
        comments = cur.execute("""SELECT COMMENTS.TEXT
                                  FROM BOOKS,
                                       COMMENTS
                                  WHERE BOOKS.ID = {book} AND
                                        BOOKS.ID = COMMENTS.BOOK;""".format(book=book[0])).fetchone()
        if not comments:
            comments = ("",)
        b['comments'] = comments[0]

        # twitter/facebook cards
        card = {}
        tag_re = re.compile('(<!--.*?-->|<[^>]*>)', re.UNICODE)
        no_tags = tag_re.sub(u'', b['comments'])
        card['description'] = html.escape(no_tags)[:250].replace('"', "")
        b['card'] = card

        # publishers
        publishers = cur.execute("""SELECT PUBLISHERS.NAME
                                    FROM BOOKS,
                                         BOOKS_PUBLISHERS_LINK,
                                         PUBLISHERS
                                    WHERE BOOKS.ID = {book} AND
                                          BOOKS.ID = BOOKS_PUBLISHERS_LINK.BOOK AND
                                          PUBLISHERS.ID = BOOKS_PUBLISHERS_LINK.PUBLISHER;""".format(book=book[0])).fetchone()
        if not publishers:
            publishers = ("Unknown",)
        b['publisher'] = publishers[0]

        # formats
        formats = cur.execute("""SELECT DATA.NAME,
                                        DATA.FORMAT,
                                        DATA.UNCOMPRESSED_SIZE
                                 FROM BOOKS,
                                      DATA
                                 WHERE BOOKS.ID = {book} AND
                                       BOOKS.ID = DATA.BOOK;""".format(book=book[0])).fetchall()
        bk = []
        for frmat in formats:
            file_type = frmat[1].lower()
            file_name = "{}.{}".format(frmat[0], frmat[1].lower())
            dir_path = "{}/".format(book[9])

            bk.append({'format': "{}".format(file_type),
                       'dir_path': "{}".format(dir_path),
                       'file_name': "{}".format(file_name),
                       'size': frmat[2]})
        b['formats'] = bk

        b['cover_url'] = "{}/cover.jpg".format(book[9])

        # identifiers
        identifiers = cur.execute("""SELECT IDENTIFIERS.TYPE,
                                            IDENTIFIERS.VAL
                                     FROM BOOKS,
                                          IDENTIFIERS
                                     WHERE BOOKS.ID = {book} AND
                                           BOOKS.ID = IDENTIFIERS.BOOK;""".format(book=book[0])).fetchall()
        if identifiers:
            ids = []
            for i in identifiers:
                ids.append({'scheme': i[0],
                            'code': i[1]})
            b['identifiers'] = ids

        # tags
        tags = cur.execute("""SELECT TAGS.NAME
                                FROM BOOKS,
                                    BOOKS_TAGS_LINK,
                                    TAGS
                                WHERE BOOKS.ID = {book} AND
                                    BOOKS.ID = BOOKS_TAGS_LINK.BOOK AND
                                    TAGS.ID = BOOKS_TAGS_LINK.TAG;""".format(book=book[0])).fetchall()
        if not tags:
            tags = [[""]]
        b['tags'] = [a[0] for a in tags]
        bookz.append(b)
    return bookz


def save_file(dc):
    with open("{}{}".format(dc['jsonpath'], dc['jsonname']), "w") as f:
        json.dump(
            calibre_to_json(dc['calibre_path'],
                            dc['librarian'],
                            dc['library_uuid'],
                            dc['library_secret']),
            f
        )


def add_catalog(dc):
    r = add_new('catalogs',
                json.dumps({
                    "librarian": dc['librarian'],
                    "library_uuid": dc['library_uuid'],
                    "library_secret": dc['library_secret']
                }))
    print("add_catalog() response content: {}".format(r))


def add_books(dc):
    r = add_new('books', open("{}{}".format(dc['jsonpath'], dc['jsonname'])))
    print("add_books() response content: {}".format(r))
