# -*- coding: utf-8 -*-


import sqlite3
from pprint import pprint
import json

BASE_URL = "/home/m/Ubuntu One/MarcellMarsBooks/"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


conn = sqlite3.connect('{}metadata.db'.format(BASE_URL))
conn.row_factory = dict_factory
cur = conn.cursor()

books = [book for book in cur.execute("SELECT * FROM BOOKS")]
authors = [author for author in cur.execute("SELECT * FROM AUTHORS")]
books2authors = [book2author for book2author in cur.execute("SELECT * FROM BOOKS_AUTHORS_LINK")]
comments = [comment for comment in cur.execute("SELECT * FROM COMMENTS")]
format_data = [format for format in cur.execute("SELECT * FROM DATA")]
publishers = [publisher for publisher in cur.execute("SELECT * FROM PUBLISHERS")]
publishers2books = [publisher2book for publisher2book in cur.execute("SELECT * FROM BOOKS_PUBLISHERS_LINK")]
languages = [language for language in cur.execute("SELECT * FROM LANGUAGES")]
languages2books = [language2book for language2book in cur.execute("SELECT * FROM BOOKS_LANGUAGES_LINK")]
tags = [tag for tag in cur.execute("SELECT * FROM TAGS")]
tags2books = [tag2book for tag2book in cur.execute("SELECT * FROM BOOKS_TAGS_LINK")]
identifiers = [identifier for identifier in cur.execute("SELECT * FROM IDENTIFIERS")]

book_fields = ['title',
               'title_sort',
               'comments',
               'authors',
               'id',
               'timestamp',
               'last_modified',
               'path',
               'pubdate',
               'uuid',
               'languages',
               'librarian',
               'tags',
               'format_metadata',
               'publisher',
               'formats',
               'identifiers']

bookz = []
for book in books:
    ## title_sort
    book['title_sort'] = book['sort']
    
    ## authors
    book_authors = []
    for authors_list in [b2a['author'] for b2a in books2authors if book['id'] == b2a['book']]:
        book_authors.append([author['name'] for author in authors if author['id'] == authors_list][0])
    book['authors'] = book_authors
    
    ## publishers
    try:
        publisher_id = [p2b['publisher'] for p2b in publishers2books if book['id'] == p2b['book']][0]
        book['publisher'] = [publisher['name'] for publisher in publishers if publisher['id'] == publisher_id][0]
    except:
        book['publisher'] = ""
        
    ## languages
    try:
        language_id = [l2b['id'] for l2b in languages2books if book['id'] == l2b['book']][0]
        book['languages'] = [language['lang_code'] for language in languages if language['id'] == language_id][0]
    except:
        book['languages'] = ""

    ## description
    try:
        book['comments'] = [comment['text'] for comment in comments if book['id'] == comment['book']][0]
    except:
        book['comments'] = ""
    
    ## identifiers
    try:
        book['identifiers'] = [{identifier['type'] : identifier['val']} for identifier in identifiers if book['id'] == identifier['book']]
    except:
        book['identifiers'] = []
    
    ## tags
    book_tags = []
    for tag_id in [t2b['tag'] for t2b in tags2books if book['id'] == t2b['book']]:
        book_tags.append([tag['name'] for tag in tags if tag['id'] == tag_id][0])
    book['tags'] = book_tags
    
    ## last_modified
    try:
        book['last_modified']
    except:
        book['last_modified'] = book['timestamp']
            
    ## format_metadata + formats
    book_file = {}
    book_formats = []
    for form_d in [(format_d['name'], format_d['format'], format_d['uncompressed_size']) for format_d in format_data if book['id'] == format_d['book']]:
        book_file[form_d[1]] = {'path' :  "{}{}/{}.{}".format(BASE_URL,
                                                              book['path'],
                                                              form_d[0],
                                                              form_d[1].lower()),
                                'size' : form_d[2]}
        book_formats.append(form_d[1])
        
        book['format_metadata'] = book_file
        book['formats'] = book_formats
        
    try:
        book['format_metadata']
    except:
        book['format_metadata'] = {"." : {'path' : ".",
                                          'size' : 0}}
    try:
        book['formats']
    except:
        book['formats']= ["."]
    
    #pprint([(field, book[field]) for field in book_fields])
    buk = {}
    for field in book_fields:
        buk[field] = book[field]
    
    bookz.append(buk)
    #print(json.dumps(buk, indent=2, sort_keys=True))

library = {}
library['books'] = {}
library['books']['add'] = bookz
library['books']['remove'] = []
library['librarian'] = "Pasta Testo"

def json_out():
    with open("/tmp/bukz.json", "w") as f:
        f.write(json.dumps(library, indent=2, sort_keys=True))

json_out()

