# -*- coding: utf-8 -*-

import requests

HOST_API = "http://localhost:2018"


def add_library(library_uuid, library_secret):
    headers = {'Library-Secret': library_secret}
    return requests.get("{}/library/add/{}".format(HOST_API, library_uuid),
                        headers=headers)

def remove_library(library_uuid, library_secret):
    headers = {'Library-Secret': library_secret}
    return requests.get("{}/library/remove/{}".format(HOST_API, library_uuid),
                        headers=headers)

def library_on(library_uuid, library_secret):
    headers = {'Library-Secret': library_secret}
    return requests.get("{}/library/on/{}".format(HOST_API, library_uuid),
                        headers=headers)

def library_off(library_uuid, library_secret):
    headers = {'Library-Secret': library_secret}
    return requests.get("{}/library/off/{}".format(HOST_API, library_uuid),
                        headers=headers)

def bookids(library_uuid, library_secret):
    headers = {'Library-Secret': library_secret}
    return requests.get("{}/library/bookids/{}".format(HOST_API, library_uuid),
                        headers=headers)

def add_books(library_uuid, library_secret, payload):
    headers = {'Library-Secret': library_secret}
    return requests.post("{}/books/add/{}".format(HOST_API, library_uuid),
                         headers=headers,
                         data=payload)

def remove_books(library_uuid, library_secret, payload):
    headers = {'Library-Secret': library_secret}
    return requests.post("{}/books/remove/{}".format(HOST_API, library_uuid),
                         headers=headers,
                         data=payload)
