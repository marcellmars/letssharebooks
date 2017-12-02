# -*- coding: utf-8 -*-

import sqlite3
import os
import json
import requests
import hmac
import uuid
import zlib
import dateutil.parser

from uploader import Uploader
from shuffle_names import libranom


API_ROOT = "http://localhost:5000/"


dc = {
    'local_config': {
        'calibre_path': os.path.expanduser("~/CalibreLibraries/slowrotation/"),
        # 'calibre_path': os.path.expanduser("~/CalibreLibraries/FooBar/"),
        'jsonfile': '/tmp/books_{}.json'.format('EzraAbbot'),
        'Library-Secret': '76a33991-d703-48d9-8a03-dfb3e4b69ec3'
    },
    'eve_payload': {
        'librarian': 'Ezra Abbot',
        '_id': '800fe078-9aea-4327-a4a3-eaf8cd63491f',
        'library_url': 'http://slowrotation.memoryoftheworld.org/'
        # 'library_url': 'http://localhost:2017/'
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


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def add_item(resource, headers, payload, base_url=API_ROOT):
    headers['Content-Type'] = 'application/json'
    headers['Library-Encoding'] = 'zlib'

    def _post_request(resource, headers, payload, base_url):
        payload = json.dumps(payload)
        zpayload = zlib.compress(payload.encode('utf-8'))
        print("{} - {} = {}".format(
            len(payload), len(zpayload), len(payload) - len(zpayload)))
        r = requests.post(
            "{}{}".format(base_url, resource), data=zpayload, headers=headers)
        print("POSTed @{} with status code: {}".format(resource,
                                                       r.status_code))
        return resource, r.status_code

    return _post_request(resource, headers, payload, base_url)


def edit_item(resource, headers, item, item_updated, base_url=API_ROOT):
    headers['Content-Type'] = 'application/json'
    r = requests.patch(
        "{}{}/{}".format(base_url, resource, item),
        json.dumps(item_updated),
        headers=headers)
    print("PATCHed @{} with status code: {}".format(resource, r.status_code))
    return resource, r.status_code


def delete_item(resource, headers, item, base_url=API_ROOT):
    headers['Content-Type'] = 'application/json'
    r = requests.delete(
        "{}{}/{}".format(base_url, resource, item), headers=headers)
    print("deleted @{} with status code: {}".format(resource, r.status_code))
    return resource, r.status_code


def calibre_to_json(dc, db_file='metadata.db'):
    bid = '''
    select * from books
    '''
    bid_comments = '''
    select books.id as book_id,
           comments.text as comments
    from books
    join comments on books.id = comments.book
    '''
    bid_tag = '''
    select books.id as book_id,
           tags.name as tag
    from books
    join (tags join books_tags_link on tags.id = books_tags_link.tag)
    books_tags_link on books.id = books_tags_link.book
    '''
    bid_identifiers = '''
    select books.id as book_id,
           identifiers.type as id_type,
           identifiers.val as id_val
    from books
    join identifiers on identifiers.book = books.id
    '''
    bid_formats = '''
    select books.id as book_id,
           data.format as file_format,
           data.uncompressed_size as file_size,
           data.name as file_name
    from books
    join data on data.book = books.id
    '''
    bid_publishers = '''
    select books.id as book_id,
           publishers.name
    from books
    join (publishers join books_publishers_link on publishers.id = books_publishers_link.publisher)
    books_publishers_link on books.id = books_publishers_link.book
    '''
    bid_authors = '''
    select books.id as book_id,
           authors.name
    from books join (authors join books_authors_link on authors.id = books_authors_link.author)
    books_authors_link on books.id = books_authors_link.book
    '''
    bid_series = '''
    select books.id as book_id,
           series.name
    from books join (series join books_series_link on series.id = books_series_link.series)
    books_series_link on books.id = books_series_link.book
    '''
    bid_languages = '''
    select books.id as book_id,
           languages.lang_code as lang_code
    from books join (languages join books_languages_link on languages.id = books_languages_link.lang_code)
    books_languages_link on books.id = books_languages_link.book
    '''

    conn = sqlite3.connect(
        os.path.join(dc['local_config']['calibre_path'],
                     db_file))
    cur = conn.cursor()
    sql_books = (book for book in cur.execute(bid))

    books = {}
    book_dict = [
        'application_id',
        'title',
        'title_sort',
        'timestamp',
        'pubdate',
        'series_index',
        'author_sort',
        'isbn',
        'iccn',
        'path',
        'flags',
        'uuid',
        'has_cover',
        'last_modified',  # `select * from books` ends here
        'library_uuid',
        # 'library_url',
        # 'librarian',
        '_id',
        'tags',
        'comments',
        'publisher',
        'authors',
        # 'card',
        'formats',
        'cover_url',
        'identifiers',
        'languages'
    ]

    _ = [
        books.update(
            {
                book[0]:
                dict(
                    zip(
                        book_dict,
                        book + (
                            dc['eve_payload']['_id'],  # library_uuid
                            # dc['eve_payload']['library_url'],  # library_url
                            # dc['eve_payload']['librarian'],  # librarian
                            str(
                                uuid.UUID(
                                    hmac.new(dc['local_config']['Library-Secret']
                                             .encode(), book[11].encode())
                                    .hexdigest(),
                                    version=4)),
                            [],  # tags
                            "",  # comments
                            "",  # publisher
                            [],  # authors
                            # {},  # card
                            [],  # formats
                            "{}/cover.jpg".format(book[9]),  # cover_url
                            [],  # identifiers
                            [],  # languages
                        )
                    )
                )
            }
        ) for book in sql_books
    ]

    sql_tags = [tag for tag in cur.execute(bid_tag)]
    [books[tag[0]]['tags'].append(tag[1]) for tag in sql_tags]

    # bleach.sanitizer.ALLOWED_TAGS:
    # ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i',
    #  'li', 'ol', 'strong', 'ul']
    # allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['p', 'div', 'br', 'pre']
    sql_comments = (comment for comment in cur.execute(bid_comments))
    [books[comment[0]].update(
        # {
        #     'comments': bleach.clean(comment[1],
        #                              strip=True,
        #                              tags=allowed_tags)
        # })
        {'comments': comment[1]})
     for comment in sql_comments]

    sql_publishers = (publisher for publisher in cur.execute(bid_publishers))
    [books[publisher[0]].update({'publisher': publisher[1]})
     for publisher in sql_publishers]

    sql_authors = (author for author in cur.execute(bid_authors))
    [books[author[0]]['authors'].append(author[1]) for author in sql_authors]

    sql_identifiers = (identifier for identifier
                       in cur.execute(bid_identifiers))
    [books[identifier[0]]['identifiers'].append(
        {'scheme': identifier[1], 'code': identifier[2]})
     for identifier in sql_identifiers]

    sql_formats = (frmat for frmat in cur.execute(bid_formats))
    [books[frmat[0]]['formats'].append(
        {'format': "{}".format(frmat[1].lower()),
         'file_name': "{}.{}".format(frmat[3], frmat[1].lower()),
         'dir_path': "{}/".format(books[frmat[0]]['path']),
         'size': frmat[2]})
     for frmat in sql_formats]

    sql_languages = (language for language in cur.execute(bid_languages))
    [books[language[0]]['languages'].append(language[1])
     for language in sql_languages]

    books_list = []
    remove_keys = ['application_id', 'isbn', 'iccn', 'card', 'path',
                   'flags', 'has_cover', 'uuid', 'author_sort']
    # modify_keys = ['timestamp', 'pubdate', 'last_modified']
    # modify_keys = ['last_modified', 'pubdate']
    for book in list(books.values()):
        for k in remove_keys:
            book.pop(k, None)
        # for k in modify_keys:
        #     book[k] = dateutil.parser.parse(book[k]).strftime("%a, %d %b %04Y %H:%M:%S GMT")
        books_list.append(book)
    return books_list


def post_items(dc):

    def __temp(books):
        headers = {'Library-Secret': dc['local_config']['Library-Secret']}
        add_item('add_books', headers, books)

    # books = calibre_to_json(dc)[:20000]
    books = calibre_to_json(dc)

    # print(json.dumps(books[10], indent=2, sort_keys=True))

    uploader = Uploader(__temp)
    uploader.start()

    for books_chunk in chunks(books, 1000):
        uploader.queue.put(books_chunk)

    uploader.wait()
    uploader.finish()


def save_file(dc):
    with open(dc['local_config']['jsonfile'], "w") as f:
        json.dump(calibre_to_json(dc), f)


def add_library(dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return add_item('libraries', headers, dc['eve_payload'])


def add_books(dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return add_item('books', headers,
                    # json.load(open(dc['local_config']['jsonfile'])))
                    calibre_to_json(dc))


def edit_library(item_updated, dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return edit_item('libraries', headers, dc['eve_payload']['_id'],
                     item_updated)


def delete_library(dc):
    headers = {'Library-Secret': dc['local_config']['Library-Secret']}
    return delete_item('libraries', headers, dc['eve_payload']['_id'])


def test_invalid_secret(dc):
    headers = {'Library-Secret': '123'}
    return delete_item('libraries', headers, dc['eve_payload']['_id'])
