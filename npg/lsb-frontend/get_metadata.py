# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import html
import json
import dateutil.parser
import requests
import hmac
import uuid
from shuffle_names import libranom


API_ROOT = "http://localhost:5000/"

dc = {
        'local_files': {
            'calibre_path': "/home/m/CalibreLibraries/FooBar/",
            'jsonfile': '/tmp/books_{}.json'.format('EzraAbbot'),
            'library_secret': '76a33991-d703-48d9-8a03-dfb3e4b69ec3'
        },
        'eve_payload': {
            'librarian': 'Ezra Abbot',
            '_id': '800fe078-9aea-4327-a4a3-eaf8cd63491f',
        }
}

dc2 = {
        'local_files': {
            'calibre_path': "/home/m/CalibreLibraries/Economics/",
            'jsonfile': '/tmp/books_{}.json'.format('AndrewElbakyan'),
            'library_secret': '0f4c02a4-b95a-48cb-9fc2-04e850cb620a'
        },
        'eve_payload': {
            'librarian': 'Andrew Elbakyan',
            '_id': 'dde67a22-8076-4906-b277-564652f90717',
            'presence': 'off'
        }
}


def add_item(resource, headers, payload, base_url=API_ROOT):
    headers = {'Content-Type': 'application/json',
               'Library-Uuid': headers['library_uuid'],
               'Library-Secret': headers['library_secret']}
    r = requests.post("{}{}".format(base_url, resource),
                      json.dumps(payload),
                      headers=headers)
    print("POSTed @{} with status code: {}".format(resource,
                                                   r.status_code))


def edit_item(resource, headers, item, item_updated, base_url=API_ROOT):
    headers = {'Content-Type': 'application/json',
               'Library-Uuid': headers['library_uuid'],
               'Library-Secret': headers['library_secret']}
    r = requests.patch("{}{}/{}".format(base_url, resource, item),
                       json.dumps(item_updated),
                       headers=headers)
    print("PATCHed @{} with status code: {}".format(resource,
                                                    r.status_code))


def delete_item(resource, headers, item, base_url=API_ROOT):
    headers = {'Content-Type': 'application/json',
               'Library-Uuid': headers['library_uuid'],
               'Library-Secret': headers['library_secret']}
    r = requests.delete("{}{}/{}".format(base_url, resource, item),
                        headers=headers)
    print("deleted @{} with status code: {}".format(resource,
                                                    r.status_code))


def calibre_to_json(dc, db_file='metadata.db'):
    conn = sqlite3.connect(os.path.join(dc['local_files']['calibre_path'], db_file),
                           sqlite3.PARSE_DECLTYPES)
    cur = conn.cursor()
    books = [book for book in cur.execute("SELECT * FROM BOOKS")]
    bookz = []
    for book in books:
        b = {}
        b['library_uuid'] = dc['eve_payload']['_id']
        # b['library_secret'] = dc['library_secret']
        # b['librarian'] = dc['eve_payload']['librarian']
        b['_id'] = str(
            uuid.UUID(
                    hmac.new(dc['local_files']['library_secret'].encode(),
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
    with open(dc['local_files']['jsonfile'], "w") as f:
        json.dump(
            calibre_to_json(dc),
            f
        )


def add_library(dc):
    headers = {'library_uuid': dc['eve_payload']['_id'],
               'library_secret': dc['local_files']['library_secret']}
    add_item('libraries', headers, dc['eve_payload'])


def add_books(dc):
    headers = {'library_uuid': dc['eve_payload']['_id'],
               'library_secret': dc['local_files']['library_secret']}
    add_item('books', headers, json.load(open(dc['local_files']['jsonfile'])))


def edit_library(item_updated, dc):
    headers = {'library_uuid': dc['eve_payload']['_id'],
               'library_secret': dc['local_files']['library_secret']}
    edit_item('libraries', headers, dc['eve_payload']['_id'], item_updated)


def delete_library(dc):
    headers = {'library_uuid': dc['eve_payload']['_id'],
               'library_secret': dc['local_files']['library_secret']}
    delete_item('libraries', headers, dc['eve_payload']['_id'])

# def delete_item(resource, headers, item, base_url=API_ROOT):
# def edit_item(resource, headers, item, item_updated, base_url=API_ROOT):
# def add_item(resource, headers, payload):