# -*- coding: utf-8 -*-

import sqlite3
import os
import bleach
import json
import dateutil.parser
import requests
import hmac
import uuid
from shuffle_names import libranom


API_ROOT = "http://localhost:5000/"

dc = {
        'local_config': {
            'calibre_path': os.path.expanduser("~/CalibreLibraries/FooBar/"),
            'jsonfile': '/tmp/books_{}.json'.format('EzraAbbot'),
            'Library-Secret': '76a33991-d703-48d9-8a03-dfb3e4b69ec3'
        },
        'eve_payload': {
            'librarian': 'Ezra Abbot',
            '_id': '800fe078-9aea-4327-a4a3-eaf8cd63491f',
            'library_url': 'http://localhost:2017/'
        }
}

dc2 = {
        'local_config': {
            'calibre_path': os.path.expanduser("~/CalibreLibraries/Economics/"),
            'jsonfile': '/tmp/books_{}.json'.format('AndrewElbakyan'),
            'Library-Secret': '0f4c02a4-b95a-48cb-9fc2-04e850cb620a'
        },
        'eve_payload': {
            'librarian': 'Andrew Elbakyan',
            '_id': 'dde67a22-8076-4906-b277-564652f90717',
            'library_url': 'http://localhost:2018/',
            'presence': 'off'
        }
}


def add_item(resource, headers, payload, base_url=API_ROOT):
    headers['Content-Type'] = 'application/json'
    r = requests.post("{}{}".format(base_url, resource),
                      json.dumps(payload),
                      headers=headers)
    print("POSTed @{} with status code: {}".format(resource,
                                                   r.status_code))
    return resource, r.status_code


def edit_item(resource, headers, item, item_updated, base_url=API_ROOT):
    headers['Content-Type'] = 'application/json'
    r = requests.patch("{}{}/{}".format(base_url, resource, item),
                       json.dumps(item_updated),
                       headers=headers)
    print("PATCHed @{} with status code: {}".format(resource,
                                                    r.status_code))
    return resource, r.status_code


def delete_item(resource, headers, item, base_url=API_ROOT):
    headers['Content-Type'] = 'application/json'
    r = requests.delete("{}{}/{}".format(base_url, resource, item),
                        headers=headers)
    print("deleted @{} with status code: {}".format(resource,
                                                    r.status_code))
    return resource, r.status_code


def calibre_to_json(dc, db_file='metadata.db'):
    conn = sqlite3.connect(os.path.join(dc['local_config']['calibre_path'],
                                        db_file),
                           sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    books = [book for book in cur.execute("SELECT * FROM BOOKS")]
    bookz = []
    for book in books:
        b = {}
        b['library_uuid'] = dc['eve_payload']['_id']
        b['library_url'] = dc['eve_payload']['library_url']
        b['librarian'] = dc['eve_payload']['librarian']
        b['_id'] = str(
            uuid.UUID(
                hmac.new(dc['local_config']['Library-Secret'].encode(),
                         book[11].encode())
                .hexdigest(),
                version=4)
        )
        # b['_id'] = book[11]
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

        # bleach.sanitizer.ALLOWED_TAGS:
        # ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i',
        #  'li', 'ol', 'strong', 'ul']

        tags = bleach.sanitizer.ALLOWED_TAGS + ['p', 'div', 'br', 'pre']
        b['comments'] = bleach.clean(comments[0], strip=True, tags=tags)

        # twitter/facebook cards
        card = {}
        card['description'] = b['comments'][:250]
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
    with open(dc['local_config']['jsonfile'], "w") as f:
        json.dump(
            calibre_to_json(dc),
            f
        )


def add_library(dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return add_item('libraries', headers, dc['eve_payload'])


def add_books(dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return add_item(
        'books', headers, json.load(open(dc['local_config']['jsonfile'])))


def edit_library(item_updated, dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return edit_item(
        'libraries', headers, dc['eve_payload']['_id'], item_updated)


def delete_library(dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return delete_item('libraries', headers, dc['eve_payload']['_id'])


def test_invalid_secret(dc):
    headers = {'Library-Secret': '123'}
    return delete_item('libraries', headers, dc['eve_payload']['_id'])
