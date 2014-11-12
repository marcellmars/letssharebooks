import subprocess, os


FOOBAR_LIBRARY = "/home/m/devel/letssharebooks/misc/Foobar"

def create_library(library=FOOBAR_LIBRARY):
    o = subprocess.check_output(["calibredb", "add", "-d", "--library-path", library, "-e"])
    print(o)

def add_book(book, library=FOOBAR_LIBRARY, metadata={}):
    arg_list = ["calibredb", "add", "-d", "--library-path", library]
    if not book:
        arg_list = ["calibredb", "add", "-e", "--library-path", library]

    for md in metadata.items():
        if md[1] != "":
            arg_list.extend(["--{}".format(md[0]), '{}'.format(md[1])])

    print(arg_list)
    if book:
        arg_list.append(book)
    oput = subprocess.check_output(arg_list)
    book_id = [o.split(" ")[-1] for o in oput.split("\n") if o.startswith("Added book ids: ")][0]
    print(book_id)
    return book_id

def set_metadata(book_id, library=FOOBAR_LIBRARY, metadata={}):
    arg_list = ["calibredb", "set_metadata", "--library-path", library]
    ident_values = ""
    for md in metadata.items():
        if md[1] != "":
            if md[0] == "identifiers" and md[1][1] != "":
                ident_values += '"{}":"{}",'.format(md[1][0], md[1][1])
            else:
                arg_list.extend(["--field", "{}:{}".format(md[0], md[1])])

    if ident_values != "":
        arg_list.extend(['--field', 'identifiers:{}'.format(ident_values[:-1])])
    arg_list.append(book_id)
    oput = subprocess.check_output(arg_list)
    print(oput)

def set_custom_metadata(book_id, library=FOOBAR_LIBRARY, metadata={}):
    for md in metadata.items():
        arg_list = "calibredb set_custom --library-path {} ".format(library)
        arg_list += '{} {} "{}"'.format(md[0], book_id, md[1])
        os.system(arg_list)

'''MDR
'''
import csv

ci = [i for i in csv.DictReader(open("/tmp/mdr_all.csv"))]
for i in ci:
    book_id = add_book("/tmp/empty.pdf",
                       FOOBAR_LIBRARY,
                       metadata={"title": i["FILE NAME"],
                                 "authors": i["AUTHOR"]})

    set_custom_metadata(book_id,
                        FOOBAR_LIBRARY,
                        metadata={"collection": i["COLLECTION"],
                                  #"location": i["LOCATION"],
                                  "types": i["TYPE"],
                                  "custom_date": i["DATE"],
                                  "depositor": i["DONOR"],
                                  "activation_notes": i["QUESTIONS_NOTES"]})

    set_metadata(book_id,
                 FOOBAR_LIBRARY,
                 metadata={"identifiers": ["mdr_ref", i["REF NO."]],
                           "identifiers": ["mdr_box", i["BOX NO."]]})
''''''
