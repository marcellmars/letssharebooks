import json
import random
import uuid
import time

import requests

LIBRARIES = [
    {
        'id': '1',
        'librarian': 'Muharem',
        'library_url': 'http://muharem.memoryoftheworld.org/',
        'presence': 'on'
    },
    # {
    #     'id': '2',
    #     'librarian': 'Ajnur',
    #     'library_url': 'http://ajnur.memoryoftheworld.org/',
    #     'presence': 'off'
    # }
]

resp = requests.post(
    'http://localhost:8000/libraries/',
    json=LIBRARIES)
print(resp.json())

with open('books.json') as f:
    books = json.load(f)
    books_to_upload = []
    for i in range(1000):
        r = random.randrange(len(books))
        b = dict(books[r])
        b['id'] = str(uuid.uuid4())
        b['library'] = '1'
        books_to_upload.append(b)

    t0 = time.time()
    resp = requests.post(
        'http://localhost:8000/books/',
        json=books_to_upload)
    print(resp.json())
