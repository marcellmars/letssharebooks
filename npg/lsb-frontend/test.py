from pymongo import MongoClient

from get_metadata import add_library
from get_metadata import edit_library
from get_metadata import delete_library

from get_metadata import save_file
from get_metadata import add_books

from get_metadata import dc
from get_metadata import dc2


def clear_db(db):
    db.libraries.drop()
    db.libraries_secrets.drop()
    db.books.drop()
    db.authors_ngrams.drop()
    db.titles_ngrams.drop()
    db.tags_ngrams.drop()
    db.authors_ngrams.create_index([('ngram', 1), ('val', 1)], unique=True)
    db.titles_ngrams.create_index([('ngram', 1), ('val', 1)], unique=True)
    db.tags_ngrams.create_index([('ngram', 1), ('val', 1)], unique=True)


def main():
    mc = MongoClient("localhost", 27017)
    db = mc['letssharebooks']
    clear_db(db)
    print(db.collection_names())
    assert len(db.collection_names()) <= 4

    # test add and delete
    assert add_library(dc) == ('libraries', 201)
    assert delete_library(dc) == ('libraries', 204)

    # test editing librarians in libraries
    assert add_library(dc) == ('libraries', 201)
    lib1 = {'librarian': 'Henriette Davidson Avram'}
    assert edit_library(lib1, dc) == ('libraries', 200)
    lib2 = {'librarian': 'Ezra Abbot'}
    assert edit_library(lib2, dc) == ('libraries', 200)

    # test books adding
    save_file(dc)
    assert add_books(dc) == ('books', 201)
    assert add_library(dc2) == ('libraries', 201)
    save_file(dc2)
    assert add_books(dc2) == ('books', 201)

    # test editing presence in libraries
    on = {'presence': 'on'}
    off = {'presence': 'off'}
    assert edit_library(on, dc) == ('libraries', 200)
    assert db.authors_ngrams.count() == 35
    assert db.titles_ngrams.count() == 68
    assert db.tags_ngrams.count() == 11

    assert edit_library(off, dc) == ('libraries', 200)
    assert db.authors_ngrams.count() == 0
    assert db.titles_ngrams.count() == 0
    assert db.tags_ngrams.count() == 0

    assert edit_library(on, dc2) == ('libraries', 200)
    assert db.authors_ngrams.count() == 39
    assert db.titles_ngrams.count() == 146
    assert db.tags_ngrams.count() == 1

    assert edit_library(off, dc2) == ('libraries', 200)
    assert db.authors_ngrams.count() == 0
    assert db.titles_ngrams.count() == 0
    assert db.tags_ngrams.count() == 0

    assert edit_library(on, dc) == ('libraries', 200)
    assert db.authors_ngrams.count() == 35
    assert db.titles_ngrams.count() == 68
    assert db.tags_ngrams.count() == 11
    assert edit_library(on, dc2) == ('libraries', 200)
    assert db.authors_ngrams.count() == 66
    assert db.titles_ngrams.count() == 192
    assert db.tags_ngrams.count() == 11

if __name__ == '__main__':
    main()