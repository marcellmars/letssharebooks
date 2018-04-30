# -*- coding: utf-8 -*-

import sqlite3
import os
import json
import hmac
import uuid
import zlib
# import dateutil.parser
# import bleach
import time

from shuffle_names import libranon


def calibre_to_json(library_uuid, library_secret, librarian, db_path):
    t = time.time()
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
        os.path.join(db_path))
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
        'librarian',
        '_id',
        'tags',
        'abstract',
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
                            library_uuid,  # library_uuid
                            librarian,  # librarian
                            str(
                                uuid.UUID(
                                    hmac.new(library_secret.encode(),
                                             book[11].encode()).hexdigest(),
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
    [books[tag[0]]['tags'].append(tag[1][:100]) for tag in sql_tags]

    # bleach.sanitizer.ALLOWED_TAGS:
    # ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i',
    #  'li', 'ol', 'strong', 'ul']
    # allowed_tags = bleach.sanitizer.ALLOWED_TAGS + ['p', 'div', 'br', 'pre']
    sql_comments = (comment for comment in cur.execute(bid_comments))
    [books[comment[0]].update(
        # {
        #     'comments': bleach.clean(comment[1][:10000],
        #                              strip=True,
        #                              tags=allowed_tags)
        # })
        {'abstract': comment[1][:10000]})
     for comment in sql_comments]
    sql_publishers = (publisher for publisher in cur.execute(bid_publishers))
    [books[publisher[0]].update({'publisher': publisher[1][:100]})
     for publisher in sql_publishers]

    sql_series = (series for series in cur.execute(bid_series))
    [books[series[0]].update({'series': series[1][:100]})
     for series in sql_series]

    sql_authors = (author for author in cur.execute(bid_authors))
    [books[author[0]]['authors'].append(author[1][:200]) for author in sql_authors]

    sql_identifiers = (identifier for identifier
                       in cur.execute(bid_identifiers))
    [books[identifier[0]]['identifiers'].append(
        {'scheme': identifier[1][:100], 'code': identifier[2][:1000]})
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
    remove_keys = ['application_id', 'isbn', 'iccn', 'path',
                   'flags', 'has_cover', 'uuid', 'author_sort',
                   'timestamp', 'series_index']
    # modify_keys = ['timestamp', 'pubdate', 'last_modified']
    for book in list(books.values()):
        for k in remove_keys:
            book.pop(k, None)
        # for k in modify_keys:
        #     book[k] = dateutil.parser.parse(book[k]).strftime("%a, %d %b %04Y %H:%M:%S GMT")
        books_list.append(book)

    print("{} processing time: {} seconds...".format(librarian,
                                                     round(time.time() - t, 3)))
    return books_list


def save_file(file_path, books_list):
    with open(file_path, "w") as f:
        json.dump(books_list, f)


def save_file(file_path, books_list, zipit=False):
    with open(file_path, "wb") as f:
        payload = json.dumps(books_list)
        if zipit:
            payload = zlib.compress(payload.encode('utf-8'))
        f.write(payload)
