# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os
import sys
import subprocess
import re
import random
import webbrowser
import time
import zipfile
import json
import functools
import shutil
import SimpleHTTPServer
import SocketServer
import uuid
import datetime
import cStringIO
import gzip
import posixpath
import urllib
import mimetypes
import operator
import threading
import cgi
import hashlib

try:
    from PyQt4 import QtWebKit
except ImportError:
    from PyQt5 import QtWebKitWidgets as QtWebKit

try:
    from PyQt4.Qt import (Qt,
                          QDialog,
                          QHBoxLayout,
                          QPushButton,
                          QTimer,
                          QIcon,
                          QPixmap,
                          QApplication,
                          QSizePolicy,
                          QVBoxLayout,
                          QWidget,
                          QLineEdit,
                          QThread,
                          QSslConfiguration,
                          QSslCertificate,
                          QFile,
                          pyqtSignal,
                          QUrl,
                          QStateMachine,
                          QState,
                          QByteArray,
                          QCursor,
                          QProgressBar,
                          QLabel)
    QT_RUNNING = 4
except ImportError:
    from PyQt5.Qt import (Qt,
                        QDialog,
                        QHBoxLayout,
                        QPushButton,
                        QTimer,
                        QIcon,
                        QPixmap,
                        QApplication,
                        QSizePolicy,
                        QVBoxLayout,
                        QWidget,
                        QLineEdit,
                        QThread,
                        QSslConfiguration,
                        QSslCertificate,
                        QFile,
                        pyqtSignal,
                        QUrl,
                        QStateMachine,
                        QState,
                        QByteArray,
                        QCursor,
                        QProgressBar,
                        QLabel)
    QT_RUNNING = 5

from calibre_plugins.letssharebooks.common_utils import get_icon
from calibre_plugins.letssharebooks.config import prefs, ConfigWidget
from calibre_plugins.letssharebooks import requests
from calibre_plugins.letssharebooks import LetsShareBooks as lsb
from calibre_plugins.letssharebooks.shuffle_names import get_libranon
from calibre_plugins.letssharebooks.shuffle_names import encrypt_uid
from calibre_plugins.letssharebooks.my_logger import MyLogger, Om
from calibre_plugins.letssharebooks.get_metadata import get_lsb_metadata


__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

if False:
    get_icons = get_resources = None

#- set up logging -------------------------------------------------------------
# logger = MyLogger("/tmp/letssharebooks_windows.log")
logger = Om() # for silent logger
logger.debug("QT_RUNNING: {}".format(QT_RUNNING))

#------------------------------------------------------------------------------

try:
    #- calibre brings some SSL stuff which conflicts with system OpenSSL ------
    #- this gets rid off calibre's default ------------------------------------
    del os.environ['LD_LIBRARY_PATH']
except:
    pass

#------------------------------------------------------------------------------
#- runnable downloader --------------------------------------------------------


class Downloader(QThread):
    downloaded_data = pyqtSignal(str, str, int, int)
    canceled_download = pyqtSignal(str, str, int, int)
    finished_file = pyqtSignal(str, str)

    def __init__(self, uuid4, url, dl_file):
        QThread.__init__(self)
        self.uuid4 = uuid4
        self.url = url
        self.dl_file = dl_file
        self.download_pass = True

    def run(self):
        with open(self.dl_file, "wb") as f:
            total_length = None
            try:
                response = requests.get(self.url, stream=True, verify=False)
                #response = requests.get(self.url, verify=False)
                total_length = response.headers.get('content-length')
            except Exception as e:
                logger.debug("DOWNLOADING EXCEPTION: {}".format(e))
                return

            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content():
                    if self.download_pass:
                        dl += len(data)
                        f.write(data)
                        if dl % 100000 == 0:
                            self.downloaded_data.emit(self.uuid4,
                                                      self.dl_file,
                                                      dl,
                                                      total_length)
                    else:
                        self.canceled_download.emit(self.uuid4,
                                                    self.dl_file,
                                                    dl,
                                                    total_length)
                        return

        self.finished_file.emit(self.uuid4, self.dl_file)
        return


#------------------------------------------------------------------------------
#- local HTTP daemon waiting for urls from library.memoryoftheworld.org -------
#- to import the book(s) ------------------------------------------------------

class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    timeout = 5
    lock = threading.Lock()

    def copyfile(self, source, outputfile):
        if self.gzip_on:
            outputfile = gzip.GzipFile(mode='wb', fileobj=outputfile)
        shutil.copyfileobj(source, outputfile)

    def serve_library(self, path):
        path = self.translate_path(path)
        f = None
        self.gzip_on = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return
            for index in "index.html", "index.htm", "BROWSE_LIBRARY.html":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
        ctype = self.guess_type(path)

        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            if path.endswith("cover.jpg"):
                cover_md5 = "{}.jpg".format(hashlib.md5(open(path, 'rb')
                                                        .read())
                                            .hexdigest())
                tpath = os.path.join(self.server.html.portable_dir, cover_md5)
                if not os.path.exists(tpath):
                    cover = QPixmap(path)
                    cover_scaled = cover.scaled(255, 360,
                                                Qt.KeepAspectRatio,
                                                Qt.SmoothTransformation)
                    cover_scaled.save(tpath)
                path = tpath

            f = open(path, 'rb')

        except IOError:
            self.send_error(404, 'File not found')
            self.connection.close()
            return

        if not f:
            self.send_error(404, 'File not found')
            self.connection.close()
            return

        self.send_response(200)
        self.send_header("Content-type", ctype)
        #self.send_header("Content-Encoding", "gzip")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()
        return

    def do_GET(self):
        from calibre.gui2.ui import get_gui

        file_path = get_gui().library_path.split(os.path.sep)
        if sys.platform == "win32":
            file_path.insert(1, os.path.sep)
        else:
            file_path.insert(0, '/')

        os.chdir(os.path.join(*file_path))

        library_aes_id = encrypt_uid(prefs['library_uuid'],
                                     get_gui().current_db.library_id)
        gifs = ['0.gif',
                '{}.gif'.format(library_aes_id),
                'favicon.ico']
        #logger.debug("REQUEST FILE PATH: {}".format(self.path))
        if self.path[1:] in gifs:
            self.serve_gif()
        elif self.path[:7] == "/?urls=":
            self.send_response(200, 'OK')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.server.html.web_signal.emit(self.path)
            self.wfile.write('<body onload="window.close();">')
        else:
            self.serve_library(self.path)

    def translate_path(self, path):
       # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def serve_gif(self):
        gif_b64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        f = cStringIO.StringIO(gif_b64.decode('base64'))
        self.send_response(200, 'OK')
        self.send_header("Content-type", "image/gif")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(f.read())

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',
        '.epub': 'application/epub+zip',
        '.lrf': 'application/x-sony-bbeb',
        '.azw': 'application/x-mobipocket-ebook',
        '.tpz': 'application/x-topaz-ebook',
        '.azw1': 'application/x-topaz-ebook',
        '.azw2': 'application/x-kindle-application',
        '.pobi': 'application/x-mobipocket-subscription',
        '.azw3': 'application/x-mobi8-ebook'
        })


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class ThreadedServer(QThread):
    web_signal = pyqtSignal(str, name="web_signal")

    def __init__(self, port):
        logger.debug("STARTED LOCAL HTTP SERVER!")
        QThread.__init__(self)
        SocketServer.TCPServer.allow_reuse_address = True
        #self.httpd = BaseHTTPServer.HTTPServer(("", port), HTTPHandler)
        self.httpd = ThreadedTCPServer(("", port), HTTPHandler)
        self.httpd.daemon = True
        self.httpd.html = self

        #- self.httpd.socket  will make this http server ----------------------
        # running through https -----------------------------------------------
        #self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
        #                                    keyfile='localmemory.key',
        #                                    certfile='localmemory.crt',
        #                                    server_side=True)

    def run(self):
        self.threaded_httpd = threading.Thread(target=self.httpd.serve_forever)
        #self.httpd.serve_forever()
        #self.threaded_httpd.daemon = True
        self.threaded_httpd.start()

#------------------------------------------------------------------------------
#- in Metadatalibthread metadata gets into .json, upload to server and --------
#- prepare if for portable calibre --------------------------------------------


class MetadataLibThread(QThread):
    uploaded = pyqtSignal()
    upload_error = pyqtSignal()
    uploading = pyqtSignal()

    def __init__(self, us, portable=False):
        QThread.__init__(self)
        self.us = us
        self.n_bulk = 37
        self.portable = portable

    #--------------------------------------------------------------------------
    #- this will use sqlite3 directly. it is not meant to be ------------------
    #- used for "live" so all_books_ids are mocked here. ----------------------
    #- when needed uncomment this and MOCK the one below ----------------------
    # def get_book_metadata(self, current_db):
    #     self.get_directory_path()
    #     books = get_lsb_metadata(self.directory_path,
    #                              prefs['librarian']['name'])
    #     books.append(set([0]))
    #     return books

    def get_book_metadata(self, current_db):
        self.get_directory_path()
        books = []
        books_ids = current_db.all_book_ids()
        all_book_ids = []
        for book in books_ids:
            # logger.debug("BOOK_ID BEFORE: {}".format(book))
            b = {}
            #md_fields = current_db.get_proxy_metadata(book)
            md_fields = current_db.get_metadata(book)
            logger.debug("CURRENT_DB PATH: {}".format(current_db._field_for('path', book).replace('/', os.sep)))
            # logger.debug("BOOK METADATA: {}".format(md_fields.__dict__))
            b['timestamp'] = md_fields.timestamp.isoformat()
            b['pubdate'] = md_fields.pubdate.isoformat()

            if not md_fields.last_modified:
                logger.debug("IS THIS THE REASON? {}".format(b['timestamp']))
                md_fields.last_modified = b['timestamp']

                mi = current_db.get_metadata(md_fields.id)
                mi.set("last_modified", b['timestamp'])

            b['last_modified'] = md_fields.last_modified.isoformat()

            if not md_fields.tags:
                md_fields.tags = [""]

            b['tags'] = [a for a in md_fields.tags]

            if [tag for tag in b['tags'] if tag.lower() == "private"]:
                from calibre.utils.date import utcnow
                mi = current_db.get_metadata(md_fields.id)
                mi.set("last_modified", utcnow().isoformat())
                continue

            b['librarian'] = prefs['librarian']['name']

            b['uuid'] = encrypt_uid(prefs['library_uuid'],
                                    str(md_fields.uuid))
            b['library_uuid'] = "p::{}::p".format(current_db.library_id)
            b['application_id'] = md_fields.id
            if not md_fields.title:
                md_fields.title = "Unknown"
            b['title'] = md_fields.title.replace('"', "'")
            # logger.debug("BOOK_ID: {}, TITLE: {}".format(book, b['title']))
            if not md_fields.title_sort:
                md_fields.title_sort = "Unknown"
            b['title_sort'] = md_fields.title_sort

            b['authors'] = []
            for author in md_fields.authors:
                b['authors'].append(author)

            b['comments'] = u""
            if md_fields.comments:
                b['comments'] = md_fields.comments

            card = {}
            tag_re = re.compile(ur'(<!--.*?-->|<[^>]*>)', re.UNICODE)
            no_tags = tag_re.sub(u'', b['comments'])
            card['description'] = cgi.escape(no_tags)[:250].replace('"', "")
            b['card'] = card

            b['publisher'] = md_fields.publisher

            bkf = {}
            bk = []

            b['cover_url'] = ""
            dir_path = current_db._field_for('path', book)
            b['cover_url'] = "{}/cover.jpg".format(dir_path)
            try:
                if md_fields.format_metadata:
                    for frmat in md_fields.format_metadata.iteritems():
                        logger.debug("FRMAT: {}".format(frmat))
                        file_path = frmat[1]["path"].split(os.path.sep)[-3:]
                        file_path = posixpath.join(*file_path)
                        file_name = frmat[1]["path"].split(os.path.sep)[-1]
                        # dir_path = frmat[1]["path"].split(os.path.sep)[-3:-1]
                        # dir_path = os.path.join(*dir_path)
                        bkf[frmat[0]] = {'file_path': "{}".format(file_path),
                                         'file_name': "{}".format(file_name),
                                         'dir_path': "{}/".format(dir_path),
                                         'size': frmat[1]["size"]}
                        bk.append(frmat[0])
            except Exception as e:
                #- most probably calibre needs [Fix missing formats] ----------
                #- maybe send some info to the user about this ----------------
                #- too much of a hussle at the moment -------------------------
                logger.debug("Missing 'path or 'size' in format_metadata: {}"
                             .format(e))

            if not bkf:
                bkf['0'] = {'file_path': "{}/{}.{}"
                            .format(dir_path, ".", "."),
                            'file_name': "...",
                            'dir_path': "{}".format(dir_path),
                            'size': 0}

            b['format_metadata'] = bkf

            if not bk:
                bk = ['0']
            b['formats'] = bk

            ids = {}
            if md_fields.identifiers:
                ids = md_fields.identifiers

            b['identifiers'] = ids
            all_book_ids.append(b['uuid'])
            # logger.debug("BOOK_ID FINISHED: {}".format(book))
            books.append(b)

        books.append(set(all_book_ids))
        return books

    def get_server_list(self, uuid4):
        try:
            r = requests.get("{}://library.{}/get_catalog"
                             .format(prefs['server_prefix'],
                                     prefs['lsb_server']),
                             params={'uuid': uuid4},
                             verify=False)
            catalog = r.json()
        except:
            catalog = None
            self.upload_error.emit()
        if catalog is None:
            return []
        else:
            return [(book[0], book[1]) for book in catalog['books']]

    def get_current_db(self):
        from calibre.gui2.ui import get_gui
        self.sql_db = get_gui().current_db.new_api
        library_aes_id = encrypt_uid(prefs['library_uuid'],
                                     get_gui().current_db.library_id)

        self.sql_db.library_id = library_aes_id
        return self.sql_db

    def get_directory_path(self):
        from calibre.gui2.ui import get_gui
        file_path = get_gui().library_path.split(os.path.sep)
        if sys.platform == "win32":
            file_path.insert(1, os.path.sep)
        else:
            file_path.insert(0, '/')
        self.directory_path = os.path.join(*file_path)

    def intersect(self, books_metadata):
        local_list = set([(book['uuid'], book['last_modified'])
                          for book in books_metadata])
        server_list = set(self.get_server_list(self.sql_db.library_id))

        edited_list = local_list - server_list
        added_books_ids = [book[0] for book in edited_list]
        removed_list = server_list - local_list
        removed_books = list(set([book[0] for book in removed_list]) |
                             set(added_books_ids))

        added_books = [book for book in books_metadata
                       if book['uuid'] in added_books_ids]

        return removed_books, added_books

    def make_portable(self, books_metadata):
        #----------------------------------------------------------------------
        #- prepare BROWSE_LIBRARY.html for portable library in the root -------
        #- directory of current library ---------------------------------------
        from calibre.utils.date import utcnow
        self.library = {}
        self.library['last_modified'] = utcnow().isoformat()
        self.library['librarian'] = prefs['librarian']['name']

        if not books_metadata:
            return

        with open(os.path.join(self.us.portable_directory,
                               'portable/data.js'), 'wb') as f:
            library_id = self.sql_db.library_id
            self.library['library_uuid'] = "p::{}::p".format(library_id)
            self.library['last_modified'] = str(sorted(
                [book['last_modified'] for book in books_metadata])[-1])
            #- make portable port distinctive -1337 so it can be registered ---
            #- at https://library.memoryoftheworld.org ------------------------
            self.library['tunnel'] = -1337
            self.library['portable'] = False
            self.library['portable_url'] = False
            self.library['books'] = {}
            self.library['books']['remove'] = []
            self.library['books']['add'] = sorted(books_metadata,
                                                  key=operator.itemgetter('uuid'))
            json_string = json.dumps(self.library)
            f.write("LIBRARY = {};".format(json_string))
        try:
            shutil.rmtree(os.path.join(self.directory_path, 'static'))
        except Exception as e:
            logger.debug("ERROR REMOVING 'STATIC' DIRECTORY: {}".format(e))
        try:
            os.remove(os.path.join(self.directory_path,
                                   'BROWSE_LIBRARY.html'))
        except Exception as e:
            logger.debug("ERROR REMOVING BROWSE_LIBRARY.html: {}".format(e))

        try:
            shutil.copytree(os.path.join(self.us.portable_directory,
                                         'portable'),
                            os.path.join(self.directory_path,
                                         'static'))
        except Exception as e:
            logger.debug("ERROR COPYING 'STATIC/PORTABLE' DIRS: {}".format(e))

        try:
            shutil.move(os.path.join(self.directory_path,
                                     'static',
                                     'BROWSE_LIBRARY.html'),
                        os.path.join(self.directory_path))
        except Exception as e:
            logger.debug("ERROR MOVING 'STATIC/PORTABLE' DIRS: {}".format(e))

    def zip_library(self, added_books, removed_books, mode):
        with zipfile.ZipFile(os.path.join(self.us.portable_directory,
                                          'json',
                                          'library.json.zip'),
                             'w', mode) as zif:
            with open(os.path.join(self.us.portable_directory,
                                   'json',
                                   'library.json'),
                      'wb') as f:
                self.library['library_uuid'] = str(self.sql_db.library_id)
                self.library['tunnel'] = int(self.us.port)
                self.library['books'] = {}

                self.library['books']['remove'] = list(removed_books)
                self.library['books']['add'] = list(added_books)
                json_string = json.dumps(self.library)
                f.write(json_string)
            zif.write(os.path.join(self.us.portable_directory,
                                   'json',
                                   'library.json'),
                      arcname='library.json')
            zif.close()

    def upload_zip(self, n_total, b_total, mode):
        with open(os.path.join(self.us.portable_directory,
                               'json',
                               'library.json.zip'), 'rb') as f:
            try:
                r = requests.post(
                    "{}://library.{}/upload_catalog".format(
                        prefs['server_prefix'],
                        prefs['lsb_server']),
                    files={'uploaded_file': f}, verify=False)
                if r.ok:
                    um = "{} books' metadata are uploading{}".format(
                        n_total,
                        random.randint(3, 10)*".")
                    #self.us.uploading_message = um
                    self.us.uploading_message = (b_total, n_total, um)
                    self.uploading.emit()
                else:
                    self.upload_error.emit()
                    return

            except requests.exceptions.RequestException as e:
                logger.debug("EXCEPTION_UPLOAD_ERROR: {}".format(e))
                self.upload_error.emit()
                return

    def upload_library(self, books_metadata,
                       removed_books,
                       added_books,
                       all_book_ids):
        try:
            import zlib
            mode = zipfile.ZIP_DEFLATED
        except:
            mode = zipfile.ZIP_STORED

        os.makedirs(os.path.join(self.us.portable_directory, 'json'))
        if not added_books:
            self.zip_library([], removed_books, mode)
            self.upload_zip(len(removed_books), len(books_metadata), mode)
            shutil.rmtree(os.path.join(self.us.portable_directory, 'json'))
            self.uploaded.emit()
            return
        else:
            again = False
            n_total = len(added_books)
            chunks = [added_books[b:b + max(1, self.n_bulk)]
                      for b in range(0, len(added_books), max(1, self.n_bulk))]

            for chunk in chunks:
                self.zip_library(chunk, removed_books, mode)
                n_total -= len(chunk)
                self.upload_zip(n_total, len(books_metadata), mode)
                removed_books = []
                if self.start_library != self.directory_path:
                    self.start_library = self.directory_path
                    again = True
                    break

            shutil.rmtree(os.path.join(self.us.portable_directory, 'json'))

            if again:
                books_metadata = self.get_book_metadata(self.get_current_db())
                all_book_ids = books_metadata.pop()
                self.make_portable(books_metadata)
                self.start_library = self.directory_path
                removed_books, added_books = self.intersect(books_metadata)
                self.upload_library(books_metadata,
                                    removed_books,
                                    added_books,
                                    all_book_ids)
            else:
                self.uploaded.emit()

    def run(self):
        logger.debug("METADATA THREAD STARTED!")
        #books_metadata = get_lsb_metadata(self.get_directory_path(),
        #                                  prefs['librarian'])
        books_metadata = self.get_book_metadata(self.get_current_db())
        all_book_ids = books_metadata.pop()
        self.make_portable(books_metadata)
        if self.portable:
            return

        self.start_library = self.directory_path
        removed_books, added_books = self.intersect(books_metadata)
        self.upload_library(books_metadata,
                            removed_books,
                            added_books,
                            all_book_ids)
        return

#------------------------------------------------------------------------------
#- in ConnectionCheck it checks both local calibre content server -------------
#- and the same service at the other end of ssh tunnel ------------------------


class ConnectionCheck(QThread):
    lost_connection = pyqtSignal()
    connection_ok = pyqtSignal()

    def __init__(self, gotcha=True):
        QThread.__init__(self)
        self.gotcha = gotcha

    def add_urls(self, urls):
        self.urls = urls

    def run(self):
        if sys.platform == "win32":
            self.connection_ok.emit()
            time.sleep(5)
        time.sleep(5)
        try:
            lsb_url = "{}://library.{}".format(prefs['server_prefix'],
                                               prefs['lsb_server'])
            requests.get('{}/ping_autocomplete'.format(lsb_url),
                         verify=False,
                         timeout=3)
            while self.gotcha:
                for url in self.urls:
                    url = "{}/static/favicon.svg".format(url)
                    logger.info("{} CHECKED!".format(url))
                    if not requests.get(url, verify=False, timeout=(5)).ok:
                        self.lost_connection.emit()
                        self.gotcha = False
                        return
                self.connection_ok.emit()
                time.sleep(30)
        except Exception as e:
            logger.info('LOST_CONNECTION: {}'.format(e))
            self.lost_connection.emit()
            self.gotcha = False
            return
        return


class HoverHand(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))

#-----------------------------------------------------------------------------
#- LetsShareBooksDialog is the main class of Calibre plugin-------------------


class LetsShareBooksDialog(QDialog):
    started_calibre_web_server = pyqtSignal()
    calibre_didnt_start = pyqtSignal()
    established_ssh_tunnel = pyqtSignal()
    lost_connection = pyqtSignal()

    def __init__(self, gui, icon, do_user_config, qaction, us):
        QDialog.__init__(self, gui)
        self.main_gui = gui
        self.do_user_config = do_user_config
        self.qaction = qaction
        self.us = us
        logger.info('REDIRECTED DEBUG OUTPUT: \n\ntail -f {}/log/lsb.log\n'
                    .format(self.us.portable_directory))

        if not prefs:
            #- this is most probably initial run of a plugin ------------------
            #- or someone deleted .json config file ---------------------------
            ConfigWidget().save_settings()
            libranon = get_libranon(prefs['server_prefix'],
                                    prefs['lsb_server'])
            logger.info("LIBRANON IN RETURN: {}".format(libranon))
            prefs['librarian'] = {'name': libranon,
                                  'saved': False}
        elif 'librarian' in prefs:
            if 'saved' not in prefs['librarian']:
                logger.info("SAVED NOT IN PREFS!")
                #- if config file is from the earlier version -----------------
                #- of plugin without 'saved' parameter ------------------------
                if prefs['librarian'] != '':
                    #- and if librarian name was saved ------------------------
                    #- by not being empty string ------------------------------
                    old_librarian = prefs['librarian']
                    if type(old_librarian) is str:
                        prefs['librarian'] = {'name': old_librarian,
                                              'saved': True}
                else:
                    prefs['librarian'] = {'name': get_libranon(prefs['server_prefix'],
                                                               prefs['lsb_server']),
                                          'saved': False}
            elif prefs['librarian']['saved'] is False:
                prefs['librarian'] = {'name': get_libranon(prefs['server_prefix'],
                                                           prefs['lsb_server']),
                                      'saved': False}

        self.files_size_log = {}
        self.book_imports = {}
        self.threads_pool = []
        self.initial = True
        self.initial_chat = True
        self.no_internet = False

        self.lsb_url_text = ' Be a librarian. Share your library.'
        self.url_label_tooltip = '<<<< Be a librarian.'\
                                 'Click on Start sharing button.<<<<'
        self.lsb_url = 'nourl'

        self.metadata_thread = MetadataLibThread(self.us)
        self.check_connection = ConnectionCheck()

        self.clip = QApplication.clipboard()
        self.pxmp = QPixmap()
        self.pxmp.load('images/icon_connected.png')
        self.icon_connected = QIcon(self.pxmp)

        #- main StyleSheet ----------------------------------------------------

        self.setStyleSheet("""
        QDialog {
                background-color: white;
        }

        QLabel {
                font-size: 16px;
                border-style: solid;
                border-color: red;
                background-color: white;
                color: red;
                font-family:'BitstreamVeraSansMono',Consolas,monospace;
                text-transform: uppercase;
        }

        QPushButton {
                font-size: 16px;
                border-style: solid;
                border-color: red;
                font-family:'BitstreamVeraSansMono',Consolas,monospace;
                text-transform: uppercase;
        }

        QPushButton#arrow {
                border-width: 16px;
                border-right-color:white;
                padding: -10px;
                color:red;
        }

        QPushButton#url {
                background-color: red;
                min-width: 460px;
                color: white;
                text-align: left;
               }

        QPushButton#url:hover {
                background-color: white;
                color: red;
                }

        QPushButton#share {
                background-color: red;
                color: white;
                margin-right: 5px;
                }

        QPushButton#share:hover {
                background-color: white;
                color: red;
                }

        QPushButton#url2 {
                color: #222;
                text-align: left;
        }
        QPushButton#url2:hover {
                color: red;
                }

        QLineEdit#edit {
                background-color: white;
                color: red;
                font-size: 16px;
                border-style: solid;
                border-color: red;
                font-family:'BitstreamVeraSansMono',Consolas,monospace;
                text-transform: uppercase;
        }

        QProgressBar {
                border: 1px solid red;
                border-radius: 0px;
        }

        QProgressBar::chunk {
                background-color: red;
                width: 5px;
                margin: 0px;
        }

        """)

        #- main UI layout -----------------------------------------------------
        self.ll = QVBoxLayout()

        self.l = QHBoxLayout()
        self.l.setSpacing(0)
        self.l.setContentsMargins(0, 0, 0, 0)
        self.w = QWidget()
        self.w.setLayout(self.l)

        self.setLayout(self.ll)
        self.setWindowIcon(icon)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.lets_share_button = HoverHand()
        self.lets_share_button.setSizePolicy(QSizePolicy.MinimumExpanding,
                                             QSizePolicy.MinimumExpanding)
        self.lets_share_button.setObjectName("share")

        self.l.addWidget(self.lets_share_button)

        self.url_label = HoverHand()
        self.url_label.setSizePolicy(QSizePolicy.MinimumExpanding,
                                     QSizePolicy.MinimumExpanding)
        self.url_label.setObjectName("url")
        self.l.addWidget(self.url_label)

        self.arrow_button = QPushButton("_______")
        self.arrow_button.setObjectName("arrow")
        self.l.addWidget(self.arrow_button)

        self.ll.addWidget(self.w)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setRange(1, 100)
        self.progress_bar.setTextVisible(False)
        self.ll.addWidget(self.progress_bar)
        self.progress_bar.hide()

        self.libranon_layout = QHBoxLayout()
        self.libranon_layout.setSpacing(0)
        self.libranon_layout.setContentsMargins(0, 0, 0, 0)
        self.libranon_container = QWidget()
        self.libranon_container.setLayout(self.libranon_layout)

        self.label = QLabel("Librarian: ")
        self.label.setObjectName("label")

        self.edit = QLineEdit()
        self.edit.setObjectName("edit")
        self.edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.edit.setToolTip("Change your librarian name")
        self.edit.setText(prefs['librarian']['name'])

        self.save_libranon = QPushButton(" Save ")
        self.save_libranon.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Maximum)
        self.save_libranon.setObjectName("share")
        self.save_libranon.setToolTip("Save your librarian name")
        self.save_libranon.clicked.connect(self.save_librarian)

        self.edit_libranon = QPushButton(" Edit ")
        self.edit_libranon.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Maximum)
        self.edit_libranon.setObjectName("share")
        self.edit_libranon.setToolTip("Edit your librarian name")
        self.edit_libranon.clicked.connect(self.edit_librarian)

        self.new_libranon = QPushButton(" New ")
        self.new_libranon.setSizePolicy(QSizePolicy.Maximum,
                                        QSizePolicy.Maximum)
        self.new_libranon.setObjectName("share")
        self.new_libranon.setToolTip("Get new librarian name")
        self.new_libranon.clicked.connect(self.new_librarian)

        self.libranon_layout.addWidget(self.label)
        self.libranon_layout.addWidget(self.edit)
        self.libranon_layout.addWidget(self.save_libranon)
        self.libranon_layout.addWidget(self.edit_libranon)
        self.libranon_layout.addWidget(self.new_libranon)

        self.ll.addWidget(self.libranon_container)
        self.ll.addSpacing(10)

        self.portable_bar = QHBoxLayout()
        self.portable_bar.setSpacing(0)
        self.portable_bar.setContentsMargins(0, 0, 0, 0)
        self.pw = QWidget()
        self.pw.setLayout(self.portable_bar)

        self.portable_button = HoverHand()
        self.portable_button.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Expanding)
        self.portable_button.setObjectName("url")
        self.portable_button.setText(" Make portable as {}"
                                     .format(self.edit.text()))
        self.portable_button.clicked.connect(self.generate_portable)

        self.arrow_button2 = QPushButton("__")
        self.arrow_button2.setObjectName("arrow")
        self.portable_bar.addWidget(self.portable_button)
        self.portable_bar.addWidget(self.arrow_button2)
        self.ll.addWidget(self.pw)
        self.pw.hide()

        #- books line with information about importing books ------------------
        self.books_layout = QHBoxLayout()
        self.books_layout.setSpacing(0)
        self.books_layout.setContentsMargins(0, 0, 0, 0)
        self.books_container = QWidget()
        self.books_container.setLayout(self.books_layout)

        self.books = QLineEdit()
        self.books.setObjectName("edit")
        self.books.setDisabled(True)
        self.books.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.books.setToolTip("Importing books...")
        self.books.setText("Foo bar!")

        self.books_label = QPushButton("Downloads:")
        self.books_label.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)
        self.books_label.setObjectName("share")
        self.books_label.setToolTip(
            "Books imported from {}://library.{}".format(prefs['server_prefix'],
                                                         prefs['lsb_server']))
        self.books_layout.addWidget(self.books_label)
        self.books_layout.addWidget(self.books)
        self.books_label.clicked.connect(self.go_do_something)

        self.ll.addWidget(self.books_container)
        self.books_container.hide()

        #- webkit with chat ---------------------------------------------------

        self.webview = QtWebKit.QWebView()
        self.webview.page().setLinkDelegationPolicy(2)
        self.webview.linkClicked.connect(self.open_url)
        self.webview.setMaximumWidth(680)
        self.webview.setMaximumHeight(320)
        self.webview.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.webview.load(QUrl.fromLocalFile(
            os.path.join(self.us.portable_directory,
                         "portable/favicon.html")))

        netaccman = self.webview.page().networkAccessManager()
        netaccman.sslErrors.connect(self.sslErrorHandler)

        # ssl_config = QSslConfiguration.defaultConfiguration()
        # certs = ssl_config.caCertificates()

        # certs.append(QSslCertificate(QFile("portable/ca-bundle.crt")))
        # ssl_config.setCaCertificates(certs)

        self.ll.addWidget(self.webview)

        #- check if there is a new version of plugin and if yes ---------------
        #- bring upgrade_button -----------------------------------------------

        self.plugin_url = 'https://github.com/marcellmars/letssharebooks/raw/'\
                          'master/calibreletssharebooks/' \
                          'letssharebooks_calibre.zip'
        self.running_version = ".".join(map(str, lsb.version))
        try:
            r = requests.get(
                'https://raw.github.com/marcellmars/letssharebooks/master/'
                'calibreletssharebooks/_version',
                verify=False,
                timeout=3)
            self.latest_version = r.text[:-1]
        except:
            self.latest_version = "0.0.0"

        self.upgrade_button = QPushButton(
            'Please download and upgrade from {0} to {1} version of plugin.'
            .format(self.us.running_version,
                    self.latest_version))
        self.upgrade_button.setObjectName("url2")
        self.upgrade_button.setToolTip(
            'When you run latest version you make developers happy')
        self.upgrade_button.clicked.connect(functools.partial(self.open_url,
                                                              self.plugin_url))

        logger.info("RUNNING: {}, LATEST: {}"
                    .format(str(self.us.running_version),
                            str(self.us.latest_version)))

        version_list = [self.us.running_version, self.us.latest_version]
        version_list.sort(key=lambda s: map(int, s.split('.')))
        if self.us.running_version != self.us.latest_version:
            if self.us.running_version == version_list[0]:
                self.ll.addSpacing(20)
                self.ll.addWidget(self.upgrade_button)

        #- run local http server for importing books --------------------------
        #- and serving the books via ssh tunnel  ------------------------------
        self.import_server = ThreadedServer(56665)
        self.import_server.httpd.html.web_signal.connect(self.http_import)
        self.import_server.httpd.html.portable_dir = self.us.portable_directory
        self.import_server.start()

        #----------------------------------------------------------------------

        self.resize(self.sizeHint())

        #- parsing/tee log file -----------------------------------------------

        os.makedirs(os.path.join(self.us.portable_directory, 'log'))
        self.se = open(os.path.join(self.us.portable_directory,
                                    'log',
                                    'lsb.log'), 'w+b')
        #self.se = tempfile.NamedTemporaryFile()
        self.so = self.se

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        os.dup2(self.so.fileno(), sys.stdout.fileno())
        os.dup2(self.se.fileno(), sys.stderr.fileno())

        #- state machine ------------------------------------------------------

        self.machine = QStateMachine()

        self.on = QState()
        self.on.setObjectName("on")
        self.on.entered.connect(
            lambda: self.render_lsb_button(" Start sharing ",
                                           self.lsb_url_text))
        self.on.entered.connect(lambda: self.log_message("ON"))

        self.ssh_server = QState()
        self.ssh_server.setObjectName("ssh_server")
        self.ssh_server.entered.connect(
            lambda: self.render_lsb_button(" Stop sharing ", "Connecting..."))
        self.ssh_server.entered.connect(
            lambda: self.log_message("SSH_SERVER"))
        self.ssh_server.entered.connect(self.establish_ssh_server)

        self.ssh_server_established = QState()
        self.ssh_server_established.setObjectName("ssh_server_established")
        self.ssh_server_established.entered.connect(
            lambda: self.render_lsb_button("Stop sharing", self.lsb_url_text))
        self.ssh_server_established.entered.connect(
            lambda: self.log_message("SSH_SERVER_ESTABLISHED"))
        self.ssh_server_established.entered.connect(self.check_connections)
        self.ssh_server_established.entered.connect(self.chat)

        self.url_label_clicked = QState()
        self.url_label_clicked.setObjectName("url_label_clicked")
        self.url_label_clicked.entered.connect(
            lambda: self.open_url("{}://library.{}"
                                  .format(prefs['server_prefix'],
                                          prefs['lsb_server'])))
        self.url_label_clicked.entered.connect(
            lambda: self.log_message("URL_LABEL_CLICKED"))

        self.library_state_changed = QState()
        self.library_state_changed.setObjectName("library_state_changed")
        self.library_state_changed.entered.connect(
            lambda: self.sync_metadata("library_changed"))
        self.library_state_changed.entered.connect(
            lambda: self.log_message("LIBRARY_STATE_CHANGED"))

        self.lets_share_button_stopped = QState()
        self.lets_share_button_stopped.entered.connect(
            lambda: self.stop_connection)
        self.lets_share_button_stopped.entered.connect(
            lambda: self.log_message("LETS_SHARE_BUTTON_STOPPED"))
        self.lets_share_button_stopped.setObjectName(
            "lets_share_button_stopped")

        self.off = QState()
        self.off.setObjectName("off")
        self.off.entered.connect(lambda: self.disconnect_all())
        self.off.entered.connect(lambda: self.log_message("OFF"))

        self.on.addTransition(self.lets_share_button.clicked,
                              self.ssh_server)

        self.ssh_server.addTransition(self.lets_share_button.clicked,
                                      self.lets_share_button_stopped)
        self.ssh_server.addTransition(self.check_connection.lost_connection,
                                      self.off)
        self.ssh_server.addTransition(self.lost_connection,
                                      self.off)
        self.ssh_server.addTransition(self.established_ssh_tunnel,
                                      self.ssh_server_established)

        self.ssh_server_established.addTransition(
            self.lets_share_button.clicked,
            self.off)
        self.ssh_server_established.addTransition(self.url_label.clicked,
                                                  self.url_label_clicked)
        self.ssh_server_established.addTransition(
            self.check_connection.lost_connection,
            self.off)
        self.ssh_server_established.addTransition(self.us.library_changed,
                                                  self.library_state_changed)

        self.url_label_clicked.addTransition(self.ssh_server_established)
        self.library_state_changed.addTransition(self.ssh_server_established)

        self.lets_share_button_stopped.addTransition(self.off)

        self.off.addTransition(self.on)

        self.machine.addState(self.on)
        self.machine.addState(self.ssh_server)
        self.machine.addState(self.ssh_server_established)
        self.machine.addState(self.url_label_clicked)
        self.machine.addState(self.library_state_changed)
        self.machine.addState(self.lets_share_button_stopped)
        self.machine.addState(self.off)

        self.machine.setInitialState(self.on)
        self.machine.start()

    #--------------------------------------------------------------------------

    def sync_metadata(self, what="library_changed", portable=False):
        if not portable:
            librarian = get_libranon(prefs['server_prefix'],
                                     prefs['lsb_server'],
                                     libranon=self.edit.text())
            if librarian == self.edit.text():
                prefs['librarian']['name'] = self.edit.text()
            else:
                self.edit.setText("Please, find the new name.")
                self.edit_librarian()
                return

        if self.metadata_thread.isRunning():
            if what == "library_changed":
                self.metadata_thread.get_directory_path()
                return
            else:
                logger.info("EDITED_ITEM FIRED BUT NO LUCK FOR SYNC!")
                return
        else:
            if portable:
                prefs['librarian']['name'] = self.edit.text()
                self.metadata_thread = MetadataLibThread(self.us, True)
            else:
                self.metadata_thread = MetadataLibThread(self.us)

            self.metadata_thread.uploading.connect(
                lambda: self.update_progress_bar(
                    self.us.uploading_message))

            self.metadata_thread.uploaded.connect(
                self.progress_bar.hide)

            self.metadata_thread.uploaded.connect(
                lambda: self.url_label.setToolTip(
                    "All metadata uploaded... Click & GO!"))

            self.metadata_thread.uploaded.connect(
                lambda: self.log_message("UPLOADED"))
            self.metadata_thread.upload_error.connect(
                lambda: self.log_message("UPLOAD ERROR!"))

            self.metadata_thread.start()

    def check_connections(self):
        #- new_bookdisplay_data signal every book selection in calibre --------
        #get_gui().library_view.model().new_bookdisplay_data\ -----------------
        #.connect(self.edited_item) -------------------------------------------
        #----------------------------------------------------------------------
        #- model signals dataChanged for every book being changed -------------
        #- it passes index(row, 0) & index(row, total columns -1 --------------
        #from calibre.gui2.ui import get_gui
        #self.model = get_gui().library_view.model()
        #self.model.dataChanged.connect(self.edited_item)

        if self.initial:
            self.us.library_changed_emit()
            self.initial = False
        self.qaction.setIcon(get_icon('images/icon_connected.png'))
        self.check_connection.add_urls(
            [self.lsb_url])
        self.check_connection.gotcha = True

        if not self.check_connection.isRunning():
            self.check_connection.start()

    def edited_item(self, i, ii):
        #- new_bookdisplay_data sends only one argument -----------------------
        #- where id is id and path i path -------------------------------------
        #logger.debug("UPDATE ITEM: {}, {}".format(id.id, id.path)) -----------
        #----------------------------------------------------------------------

        #- this line logs/prints out id of a edited book ----------------------
        #- it gets triggered several times so one should ----------------------
        #- maintain a set instead of list here --------------------------------
        logger.info("ITEM ID:{} EDITED".format(self.model
                                               .get_book_display_info(i.row())
                                               .id))
        now = datetime.datetime.now()
        tdelta = datetime.timedelta(seconds=3)
        if now - self.us.edit_stamp > tdelta:
            QTimer.singleShot(3000, lambda: self.sync_metadata("edited_item"))
            self.us.edit_stamp = datetime.datetime.now()

    def disconnect_all(self):
        #- send gotcha=False to check_connection to exit ----------------------
        self.check_connection.gotcha = False
        quit_check = self.check_connection.wait(1450)
        if not quit_check:
            self.check_connection.quit()

        #- emit upload_error. confusing in logs :( ----------------------------
        #- let's add new signal some other time -------------------------------
        self.metadata_thread.upload_error.emit()
        quit_metadata = self.metadata_thread.wait(500)
        if not quit_metadata:
            self.metadata_thread.quit()

        if sys.platform == "win32":
            try:
                subprocess.Popen("taskkill /f /im lsbtunnel.exe",
                                 shell=True)
            except Exception as e:
                logger.warning("Couldn't kill lsbtunnel.exe. dead already?")
        else:
            try:
                self.ssh_proc.kill()
            except Exception as e:
                logger.warning("Couldn't kill SSH tunnel. dead? {}".format(e))

        self.qaction.setIcon(get_icon('images/icon.png'))

        self.lsb_url_text = " Be a librarian. Share your library."
        self.url_label_tooltip = '<<<< Be a librarian. '\
                                 'Click on Start sharing button.'

        if self.no_internet:
            self.lsb_url_text = "Check your internet connection... Try again?"
            self.no_internet = False

        self.lsb_url = "nourl"
        self.ssh_proc = None
        self.initial = True
        self.initial_chat = True
        self.webview.load(QUrl.fromLocalFile(os.path.join(
            self.us.portable_directory,
            "portable/favicon.html")))
        return True

    # def render_library_button(self, button_label, button_tooltip):
    #     self.about_project_button.setText(button_label)
    #     self.about_project_button.setToolTip(button_tooltip)

    def render_lsb_button(self, button_label, lsb_url_text):
        self.lsb_url_text = lsb_url_text
        self.lets_share_button.setText(button_label)
        self.url_label.setText(lsb_url_text)
        self.url_label.setToolTip(self.url_label_tooltip)

    def establish_ssh_server(self):
        self.us.port = str(int(random.random()*48000+1024))
        calibre_server_port_mock = "56665"
        if sys.platform == "win32":
            lsbtunnel = os.path.join(self.us.portable_directory,
                                          'portable',
                                          'lsbtunnel.exe')
            #- `echo y` accept any host while connecting through plink.exe
            self.ssh_proc = subprocess.Popen(
                'echo y|{0} -N -T tunnel@{1} -R {2}:localhost:{3} -P 722'
                .format(lsbtunnel,
                        prefs['lsb_server'],
                        self.us.port,
                        #self.calibre_server_port),
                        calibre_server_port_mock),
                shell=True)
            self.lsb_url = "{}://www{}.{}".format(prefs['server_prefix'],
                                                  self.us.port,
                                                  prefs['lsb_server'])
            self.lsb_url_text = " Go to: {}://library.{}".format(prefs['server_prefix'],
                                                                 prefs['lsb_server'])
            QTimer.singleShot(3000, self.established_ssh_tunnel.emit)
        else:
            self.ssh_proc = subprocess.Popen([
                'ssh', '-T', '-N', '-g', '-C',
                '-c', 'arcfour,aes128-cbc,blowfish-cbc',
                '-o', 'TCPKeepAlive=yes',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ServerAliveINterval=60',
                '-o', 'ExitOnForwardFailure=yes',
                '-v',
                #- when there is a strict firewall here pede.rs will help -----
                #- because it runs the same ssh tunneling infrastructure ------
                #- like memoryoftheworld.org but on pede.rs it listens --------
                #- on port 443 (usually left opened on firewall ---------------
                #- because of https) ------------------------------------------
                #'-o', 'ProxyCommand ssh -W %h:%p tunnel@ssh.pede.rs -p 443',
                prefs['lsb_server'],
                '-l', 'tunnel', '-R', '{}:localhost:{}'.format(
                    self.us.port,
                    #self.calibre_server_port),
                    calibre_server_port_mock),
                '-p', '722'])
            if self.ssh_proc:
                self.parse_log_counter = 0

                def parse_log():
                    #- after the lsb.log got redirected (and tee-ed) ----------
                    #- here it waits for string which signals that ------------
                    #- connection got established -----------------------------
                    self.parse_log_counter += 1
                    gotcha = False
                    try:
                        self.se.seek(0)
                        result = self.se.readlines()
                        self.se.seek(0)
                        self.se.truncate()

                        for line in result:
                            #m = re.match("^Allocated port (.*) for .*", line)
                            n = re.match("^Error: remote port forwarding failed for listen port.*",
                                         line)
                            if n:
                                #- if n matched probably that port ------------
                                #- on server is already in use ----------------
                                logger.debug("ERROR: REMOTE SSH PORT FAILED!")
                                self.ssh_proc.kill()
                                self.establish_ssh_server()
                            else:
                                m = re.match(".*All remote forwarding requests processed.*",
                                             line)
                                if m:
                                    #self.port = m.groups()[0]
                                    self.lsb_url = '{}://www{}.{}'.format(
                                        prefs['server_prefix'],
                                        self.us.port,
                                        prefs['lsb_server'])
                                    self.lsb_url_text = " {}://library.{}".format(prefs['server_prefix'],
                                                                                  prefs['lsb_server'])
                                    self.url_label_tooltip = 'Copy URL to clipboard and check it out in a browser!'
                                    self.established_ssh_tunnel.emit()
                                    gotcha = True
                                    return
                    finally:
                        if not gotcha and self.parse_log_counter < 60:
                            #- it recursively calls itself every 500 ms -------
                            #- until it catches the string from server --------
                            QTimer.singleShot(500, parse_log)
                        elif not gotcha:
                            self.no_internet = True
                            self.lost_connection.emit()
                logger.debug("PARSE_LOG! COUNTER: {}"
                             .format(self.parse_log_counter))
                parse_log()

    # def config(self):
    #     logger.info("DOES THIS EVER HAPPEN? CONFIG...")
    #     self.do_user_config(parent=self)
    #     self.label.setText(prefs['lsb_server'])

    def new_librarian(self):
        prefs['librarian'] = {'name': get_libranon(prefs['server_prefix'],
                                                   prefs['lsb_server']),
                              'saved': False}
        self.edit.setText(prefs['librarian']['name'])

    def edit_librarian(self):
        self.edit.selectAll()

    def save_librarian(self):
        librarian = get_libranon(prefs['server_prefix'],
                                 prefs['lsb_server'],
                                 libranon=self.edit.text())

        if librarian == self.edit.text():
            prefs['librarian'] = {'name': librarian,
                                  'saved': True}
        else:
            self.edit.setText("Please, find the new name.")
            self.edit_librarian()

    def open_url(self, url):
        if type(url) != unicode:
            url = url.toString()
        self.clip.setText(url)
        webbrowser.open(url)

    def chat(self):
        if self.initial_chat:
            chat_url = u"{}://chat.{}/calibre.html?nick=".format(prefs['server_prefix'],
                                                                 prefs['lsb_server'])
            url = QUrl(u"{}{}".format(chat_url,
                                      self.edit.text().title()))
            self.webview.page().mainFrame().load(url)
            self.initial_chat = False

    def generate_portable(self):
        self.sync_metadata(portable=True)

    def stop_connection(self):
        self.no_internet = False

    def keyPressEvent(self, event):
        self.log_message("Key pressed: {}".format(event))
        if event.key() == Qt.Key_Escape:
            pass
        elif event.key() == Qt.Key_Control:
            self.portable_button.setText(" Make portable as {}"
                                         .format(self.edit.text()))
            self.pw.show()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.pw.hide()

    def log_message(self, state):
        logger.info("STATE: {}".format(state))

    def log_download(self, uuid4, dl_file, dl, total_length):
        dl_file = str(dl_file)
        self.files_size_log[str(dl_file)] = [dl, total_length]
        self.update_download_state()

    def update_download_state(self):
        logger.info("FILES_SIZE_LOG: {}".format(self.files_size_log))
        book_s = "books"
        tn_books = len(self.book_imports)
        if tn_books == 1:
            book_s = "book"
        self.tn_files = 0

        for uid in self.book_imports.keys():
            self.tn_files += len(self.book_imports[uid]['files'])

            t_length = 0
            td_length = 0
            for f in self.book_imports[uid]['files']:
                logger.debug("{} total length: {}; downloaded: {}"
                             .format(f,
                                     self.files_size_log[f][1],
                                     self.files_size_log[f][0]))

                t_length += self.files_size_log[f][1]
                td_length += self.files_size_log[f][0]

            rst = t_length - td_length
            logger.debug('BOOK: "{}" has {:>3.2f} MB still to download'
                         .format(self.book_imports[uid]['title'],
                                 rst/1000000.))

        t_length = 0
        td_length = 0
        for k in self.files_size_log.keys():
            t_length += self.files_size_log[k][1]
            td_length += self.files_size_log[k][0]

        rst = t_length - td_length

        info_text = "{} {} in {} files. {:>3.2f} MB to be downloaded"\
                    .format(tn_books,
                            book_s,
                            self.tn_files,
                            rst/1000000.)
        self.books.setText(info_text)
        logger.info("DOWNLOADING: {}".format(info_text))

    def finished_download(self, uuid4, dl_file):
        t = [t for t in self.threads_pool if t.dl_file == dl_file][0]
        self.threads_pool.remove(t)
        dl_file = str(dl_file)
        uuid5 = str(uuid4)
        logger.info("{}:{} FINISHED".format(uuid5, dl_file))
        book = self.book_imports[uuid5]
        book['files'].remove(dl_file)
        del self.files_size_log[dl_file]
        logger.debug("{} has {} files to download".format(book['title'],
                                                          len(book['files'])))
        self.update_download_state()
        if len(book['files']) == 0:
            self.import_downloaded_book(book['download_dir'], uuid4)

    def http_import(self, r):
        logger.debug("DOWNLOAD URLS REQUEST: {}".format(r))
        self.books_container.show()
        request_data = urllib.unquote(r).decode('utf8')
        req_seq = request_data[7:].split('__,__')

        book = {}
        book['uuid'] = str(uuid.uuid4())
        book['title'] = req_seq[0]
        book['metadata_opf'] = req_seq[1]
        book['metadata_cover'] = req_seq[2]
        book['formats'] = [format for format in req_seq[3:]]
        book['download_dir'] = os.path.join(self.us.portable_directory,
                                            book['uuid'])
        metadata_dl_file = os.path.join(book['download_dir'], 'metadata.opf')
        cover_dl_file = os.path.join(book['download_dir'], 'cover.jpg')
        book['files'] = [metadata_dl_file, cover_dl_file]

        self.files_size_log[metadata_dl_file] = [0, 0]
        self.files_size_log[cover_dl_file] = [0, 0]

        os.makedirs(os.path.join(self.us.portable_directory, book['uuid']))

        thread_pool = []
        thread_pool.append(Downloader(book['uuid'],
                                      book['metadata_opf'],
                                      metadata_dl_file))
        thread_pool.append(Downloader(book['uuid'],
                                      book['metadata_cover'],
                                      cover_dl_file))

        for frmt in book['formats']:
            frmt_dest = os.path.join(book['download_dir'], frmt.split('/')[-1])
            self.files_size_log[frmt_dest] = [0, 0]
            book['files'].append(frmt_dest)
            thread_pool.append(Downloader(book['uuid'],
                                          frmt,
                                          frmt_dest))

        self.book_imports[book['uuid']] = book

        for thrd in thread_pool:
            self.threads_pool.append(thrd)
            thrd.downloaded_data.connect(self.log_download)
            thrd.canceled_download.connect(self.cancel_download)
            thrd.finished_file.connect(self.finished_download)
            #thrd.finished.connect(lambda: self.thrd_finished(thrd))
            thrd.start()

        # Downloads: _tn_ books in _tn_ files. _tn_ bytes to be downloaded.
        logger.info("\nTITLE: {title} "
                    "\nMETADATA_OPF: {metadata_opf}"
                    "\nMETADATA_COVER: {metadata_cover}"
                    "\nBOOK_FORMAT(S): {formats}"
                    .format(**book))

    def fix_metadata_opf(self, download_dir):
        #- calibre doesn't add reference to cover.jpg in metadata.opf ---------
        #- when accessed through web content server ---------------------------
        if os.stat(os.path.join(download_dir, "metadata.opf")).st_size < 200:
            return False
        with open(os.path.join(download_dir, "metadata.opf")) as f:
            old_text = f.read()
        with open(os.path.join(download_dir, "metadata.opf"), "w") as f:
            new_text = old_text.replace('<guide/>',
                                        '<guide><reference href="cover.jpg" \
                                        title="Cover" type="cover"/></guide>')
            f.write(new_text)
        return True

    def import_downloaded_book(self, download_dir, uuid4):
        uuid5 = str(uuid4)
        if self.fix_metadata_opf(download_dir):
            logger.debug("METADATA.OPF FIXED!")
            from calibre.gui2.ui import get_gui
            get_gui().current_db.import_book_directory(download_dir,
                                                       self.log_message)

            get_gui().library_view.model().books_added(1)
            get_gui().db_images.reset()
            get_gui().tags_view.recount()
        shutil.rmtree(download_dir)
        del self.book_imports[uuid5]
        self.update_download_state()

    def cancel_download(self):
        pass

    def sslErrorHandler(self, reply, error_list):
        reply.ignoreSslErrors()
        logger.debug("SSL ERRORS: {}".format(error_list))
        return

    def update_progress_bar(self, t_books):
        if self.progress_bar.isHidden():
            self.progress_bar.show()
        self.progress_bar.setRange(1, t_books[0])
        self.progress_bar.setValue(t_books[0]-t_books[1])
        self.url_label.setToolTip(t_books[2])

    def closeEvent(self, e):
        self.hide()

    def go_do_something(self):
        for t in self.threads_pool:
            logger.debug("THREAD: uid({}); file={}".format(t.uuid4, t.dl_file))
