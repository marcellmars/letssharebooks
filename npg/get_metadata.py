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
    '_id': 'e3b641c4-86ed-465a-9440-36a4fdd512a7',
    'library_secret': '690e7981-08b8-4e73-a2cd-dff864a902e1',
    'jsonpath': '/tmp/',
    'jsonname': 'books.json'
}


def add_item(resource, payload, base_url=dc['base_url']):
    headers = {'Content-Type': 'application/json',
               'Library-Uuid': payload[0]['_id'],
               'Library-Secret': payload[0]['library_secret']}
    r = requests.post("{}{}".format(base_url, resource), json.dumps(payload[1]), headers=headers)
    print("POSTed @{} with status code: {}".format(resource,
                                                   r.status_code))


def edit_item(resource, item, updated, dc, base_url=dc['base_url']):
    headers = {'Content-Type': 'application/json',
               'Library-Uuid': dc['_id'],
               'Library-Secret': dc['library_secret']}
    r = requests.patch("{}{}/{}".format(base_url, resource, item), json.dumps(updated), headers=headers)
    print("PATCHed @{} with status code: {}".format(resource,
                                                    r.status_code))


def delete_item(resource, item, dc, base_url=dc['base_url']):
    headers = {'Content-Type': 'application/json',
               'Library-Uuid': dc['_id'],
               'Library-Secret': dc['library_secret']}
    r = requests.delete("{}{}/{}".format(base_url, resource, item), headers=headers)
    print("deleted @{} with status code: {}".format(resource,
                                                    r.status_code))


def calibre_to_json(dc, db_file='metadata.db'):
    conn = sqlite3.connect(os.path.join(dc['calibre_path'], db_file), sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    books = [book for book in cur.execute("SELECT * FROM BOOKS")]
    bookz = []
    for book in books:
        b = {}
        b['library_uuid'] = dc['_id']
        # b['library_secret'] = dc['library_secret']
        b['librarian'] = dc['librarian']
        b['_id'] = book[11]
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
            calibre_to_json(dc),
            f
        )


def add_library(dc):
    add_item('libraries',
             [{"_id": dc['_id'],
               "library_secret": dc['library_secret']},
              {"librarian": dc['librarian'],
               "_id": dc['_id']}]
    )


def add_books(dc):
    bkz = [{
        '_id': dc['_id'],
        'library_secret': dc['library_secret']
    }]
    bkz.append(json.load(open("{}{}".format(dc['jsonpath'], dc['jsonname']))))
    add_item('books', bkz)
