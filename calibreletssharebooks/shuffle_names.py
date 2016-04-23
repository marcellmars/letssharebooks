# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import random
import string
import base64
import uuid
from calibre_plugins.letssharebooks import pyaes
from calibre_plugins.letssharebooks import requests
from calibre_plugins.letssharebooks.my_logger import MyLogger, Om

#- set up logging -------------------------------------------------------------
# logger = MyLogger(file_name="/tmp/letssharebooks_librarians.log")
logger = Om()


def get_libranon(server_prefix, lsb_server, n=0, libranon=False):
    if not libranon:
        libranon = u"{} {}".format(string.capwords(random.choice(first_names)),
                                   string.capwords(random.choice(last_names)))
    if n > 2:
        logger.info("LIBRANON + N: {} {}".format(libranon, n))
        return libranon

    try:
        r = requests.get("{}://library.{}/get_active_librarians".format(
            server_prefix,
            lsb_server),
            timeout=2,
            verify=False)
        if r.ok:
            req = r.json()
            if 'librarians' in req:
                logger.info("LIBRANON & ACTIVE LIBRARIANS: {} {}; n={}"
                            .format(libranon,
                                    str(req['librarians']),
                                    n))

                if libranon not in req['librarians']:
                    return libranon

    except requests.exceptions.RequestException as e:
        logger.info("EXCEPTION_GET_LIBRANON: {}".format(e))
    return get_libranon(server_prefix, lsb_server, n+1)


def encrypt_uid(uid, key):
    return base64.urlsafe_b64encode(pyaes.AESModeOfOperationCTR(
        uuid.UUID(key).bytes).encrypt(uid))


def decrypt_uid(uid, key):
    return pyaes.AESModeOfOperationCTR(
        uuid.UUID(key).bytes).decrypt(base64.urlsafe_b64decode(uid))


#------------------------------------------------------------------------------
#- list of first and last names of important librarians -----------------------

first_names = [u'Aristophanes',
               u'Ezra',
               u'Regina',
               u'Henriette',
               u'Dušan',
               u'Adam',
               u'Pura',
               u'Walter',
               u'Hugo',
               u'Ethel',
               u'Jorge',
               u'Howard',
               u'Jacques',
               u'Joseph',
               u'William',
               u'Robert',
               u'Melvil',
               u'Sean',
               u'Electra',
               u'Charles',
               u'Henri',
               u'Conrad',
               u'Kenneth',
               u'Thaddeus',
               u'Georg',
               u'Charles',
               u'Joachim',
               u'Kovid',
               u'Markus',
               u'Léonie',
               u'Gaspard',
               u'Gottfried',
               u'Gotthold',
               u'Audre',
               u'Sebastian',
               u'Johann',
               u'Makoto',
               u'Gabriel',
               u'Paul',
               u'Vincentius',
               u'Shiyali',
               u'Franz',
               u'Johann',
               u'Angela',
               u'Abbe',
               u'Carol',
               u'John',
               u'Gerard',
               u'Davidson',
               u'Martin',
               u'Luis',
               u'Charles',
               u'Green',
               u'William',
               u'Philipp',
               u'Coffin',
               u'Michel',
               u'Wilhelm',
               u'Ephraim',
               u'Jakob',
               u'Ramamrita',
               u'Stephan',
               u'Wilhelm',
               u'Ruiz',
               u'Langdon',
               u'Nadežda',
               u'Georges',
               u'Alexandra',
               u'Aaron',
               u'Brewster',
               u'Rick',
               u'William']

last_names = [u'of Byzantium',
              u'Abbot',
              u'Andrews',
              u'Avram',
              u'Barok',
              u'Bartsch',
              u'Belpré',
              u'Benjamin',
              u'Blotius',
              u'Bolden',
              u'Borges',
              u'Brown',
              u'Brunet',
              u'Cogswell',
              u'Croswell',
              u'Darnton',
              u'Dewey',
              u'Dockray',
              u'Doren',
              u'Folsom',
              u'La Fontaine',
              u'Gessner',
              u'Goldsmith',
              u'Harris',
              u'Harsdorffer',
              u'Jewett',
              u'Jungius',
              u'Goyal',
              u'Krajewski',
              u'Lafontaine',
              u'Leblond',
              u'Leibniz',
              u'Lessing',
              u'Lorde',
              u'Luetgert',
              u'Moser',
              u'Nagao',
              u'Naudé',
              u'Otlet',
              u'Placcius',
              u'Ranganathan',
              u'Rautenstrauch',
              u'Ridler',
              u'Robles',
              u'Rozier',
              u'Seajay',
              u'Sibley',
              u'Van Swieten',
              u'Wells',
              u'Krupskaja',
              u'Bataille',
              u'Elbakyan',
              u'Swartz',
              u'Kahle',
              u'Prelinger',
              u'Bookwarrior',
              u'Goudy']
