# -*- coding: utf-8 -*-

import sqlite3, os

#- set up logging -------------------------------------------------------------
#from calibre_plugins.letssharebooks.my_logger import get_logger
#logger = get_logger('letssharebooks', disabled=False)

#------------------------------------------------------------------------------


def get_lsb_metadata(directory_path, librarian):
    conn = sqlite3.connect(os.path.join(directory_path, 'metadata.db'))
    cur = conn.cursor()
    books = [book for book in cur.execute("SELECT * FROM BOOKS")]
    bookz = []
    for book in books:
        b = {}
        b['librarian'] = librarian
        b['uuid'] = book[11]
        b['application_id'] = book[0]
        if not book[1]:
            book[1] = "Unknown"
        b['title'] = book[1]
        if not book[2]:
            book[2] = "Unknown"
        b['title_sort'] = book[2]
        b['timestamp'] = book[3]
        b['pubdate'] = book[4]
        #b['path'] = book[9]
        if not book[13]:
            book[13] = b['timestamp']
        b['last_modified'] = book[13]

        #authors
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

        #comments/description of the book
        comments = cur.execute("""SELECT COMMENTS.TEXT
                                  FROM BOOKS,
                                       COMMENTS
                                  WHERE BOOKS.ID = {book} AND
                                        BOOKS.ID = COMMENTS.BOOK;""".format(book=book[0])).fetchone()
        if not comments:
            comments = ("",)
        b['comments'] = comments[0]

        #publishers
        publishers = cur.execute("""SELECT PUBLISHERS.NAME
                                    FROM BOOKS,
                                         BOOKS_PUBLISHERS_LINK,
                                         PUBLISHERS
                                    WHERE BOOKS.ID = {book} AND
                                          BOOKS.ID = BOOKS_PUBLISHERS_LINK.BOOK AND
                                          PUBLISHERS.ID = BOOKS_PUBLISHERS_LINK.PUBLISHER;""".format(book=book[0])).fetchone()
        if not publishers:
            publishers = ("Unknown",)
        b['publishers'] = publishers[0]

        #formats
        formats = cur.execute("""SELECT DATA.NAME,
                                        DATA.FORMAT,
                                        DATA.UNCOMPRESSED_SIZE
                                 FROM BOOKS,
                                      DATA
                                 WHERE BOOKS.ID = {book} AND
                                       BOOKS.ID = DATA.BOOK;""".format(book=book[0])).fetchall()
        bkf = {}
        bk = []
        for frmat in formats:
            bkf[frmat[1]] = {'path' :  "{}/{}/{}.{}".format(directory_path,
                                                        book[9],
                                                        frmat[0],
                                                        frmat[1].lower()),
                                    'size' : frmat[2]}
            bk.append(frmat[1])
        if not bkf:
            bkf['FOO'] = {'path' :  "{}/{}/{}.{}".format(directory_path,
                                                    book[9],
                                                    "FOO",
                                                    "BRR"),
                        'size': 0}
        b['format_metadata'] = bkf
        if not bk:
            bk = ['BRR']
        b['formats'] = bk

        #identifiers
        identifiers = cur.execute("""SELECT IDENTIFIERS.TYPE,
                                            IDENTIFIERS.VAL
                                     FROM BOOKS,
                                          IDENTIFIERS
                                     WHERE BOOKS.ID = {book} AND
                                           BOOKS.ID = IDENTIFIERS.BOOK;""".format(book=book[0])).fetchall()
        if identifiers:
            ids = {}
            for i in identifiers:
                ids[i[0]] = i[1]
            b['identifiers'] = ids

        #tags
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

