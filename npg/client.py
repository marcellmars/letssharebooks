# -*- coding: utf-8 -*-

"""
    eve-demo-client
    ~~~~~~~~~~~~~~~

    Simple and quickly hacked togheter, this script is used to reset the
    eve-demo API to its initial state. It will use standard API calls to:

        1) delete all items in the 'people' and 'works' collections
        2) post multiple items in both collection

    I guess it can also serve as a basic example of how to programmatically
    manage a remot e API using the phenomenal Requests library by Kenneth Reitz
    (a very basic 'get' function is included even if not used).

    :copyright: (c) 2015 by Nicola Iarocci.
    :license: BSD, see LICENSE for more details.
"""
import sys

import json
import random
import requests


ENTRY_POINT = 'localhost:5000'


def post_people():
    people = [
        {
            'firstname': 'John',
            'lastname': 'Doe',
            'role': ['author'],
            'location': {'address': '422 South Gay Street', 'city': 'Auburn'},
            'born': 'Thu, 27 Aug 1970 14:37:13 GMT'
        },
        {
            'firstname': 'Serena',
            'lastname': 'Love',
            'role': ['author'],
            'location': {'address': '363 Brannan St', 'city': 'San Francisco'},
            'born': 'Wed, 25 Feb 1987 17:00:00 GMT'
        },
        {
            'firstname': 'Mark',
            'lastname': 'Green',
            'role': ['copy', 'author'],
            'location': {'address': '4925 Lacross Road', 'city': 'New York'},
            'born': 'Sat, 23 Feb 1985 12:00:00 GMT'
        },
        {
            'firstname': 'Julia',
            'lastname': 'Red',
            'role': ['copy'],
            'location': {'address': '98 Yatch Road', 'city': 'San Francisco'},
            'born': 'Sun, 20 Jul 1980 11:00:00 GMT'
        },
        {
            'firstname': 'Anne',
            'lastname': 'Horvat',
            'role': ['contributor', 'copy'],
            'location': {'address': '32 Joseph Street', 'city': 'Ashfield'},
            'born': 'Fri, 25 Sep 1970 10:00:00 GMT'
        },
    ]

    r = perform_post('people', json.dumps(people))
    print "'people' posted", r.status_code, r.content

    valids = []
    if r.status_code == 201:
        response = r.json()
        if response['_status'] == 'OK':
            for person in response['_items']:
                if person['_status'] == "OK":
                    valids.append(person['_id'])

    return valids


def post_works(ids):
    works = []
    for i in range(28):
        works.append(
            {
                'title': 'Book Title #%d' % i,
                'description': 'Description #%d' % i,
                'owner': random.choice(ids),
            }
        )

    r = perform_post('works', json.dumps(works))
    print "'works' posted", r.status_code


def perform_post(resource, data):
    headers = {'Content-Type': 'application/json'}
    return requests.post(endpoint(resource), data, headers=headers)


def delete():
    r = perform_delete('people')
    print "'people' deleted", r.status_code
    r = perform_delete('works')
    print "'works' deleted", r.status_code


def perform_delete(resource):
    return requests.delete(endpoint(resource))


def endpoint(resource):
    return 'http://%s/%s/' % (
        ENTRY_POINT if not sys.argv[1:] else sys.argv[1], resource)


if __name__ == '__main__':
    delete()
    ids = post_people()
    post_works(ids)
