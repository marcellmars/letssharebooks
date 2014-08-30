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
import BaseHTTPServer

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
                          QCursor)
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
                          QCursor)



from calibre_plugins.letssharebooks.common_utils import get_icon
from calibre_plugins.letssharebooks.config import prefs
from calibre_plugins.letssharebooks import requests
from calibre_plugins.letssharebooks import LetsShareBooks as lsb
from calibre.library.server import server_config
from calibre_plugins.letssharebooks.shuffle_names import get_libranon


__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

if False:
    get_icons = get_resources = None

#- set up logging -------------------------------------------------------------
from calibre_plugins.letssharebooks.my_logger import get_logger
logger = get_logger('letssharebooks', disabled=True)

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
    #downloaded_data = pyqtSignal(QString, QString, int, int)
    #canceled_download = pyqtSignal(QString, QString, int, int)
    #finished_file = pyqtSignal(QString, QString)
    downloaded_data = pyqtSignal()
    canceled_download = pyqtSignal()
    finished_file = pyqtSignal()


    def __init__(self, uuid4, url, dl_file):
        QThread.__init__(self)
        self.uuid4 = uuid4
        self.url = url
        self.dl_file = dl_file
        self.download_pass = True

    def run(self):
        with open(self.dl_file, "wb") as f:
            response = requests.get(self.url, stream=True, verify=False)
            total_length = response.headers.get('content-length')

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
    def do_OPTIONS(self):
        self.send_response(200, 'OK')
        self.send_header('Allow', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.server.html.web_signal.emit(self.path)
        self.wfile.write('<body onload="window.close();">')


class ThreadedServer(QThread):
    web_signal = pyqtSignal(str, name="web_signal")

    def __init__(self, port):
        QThread.__init__(self)
        SocketServer.TCPServer.allow_reuse_address = True
        self.httpd = BaseHTTPServer.HTTPServer(("", port), HTTPHandler)
        self.httpd.html = self

        #- self.httpd.socket  will make this http server ----------------------
        # running through https -----------------------------------------------
        #self.httpd.socket = ssl.wrap_socket(self.httpd.socket,
        #                                    keyfile='localmemory.key',
        #                                    certfile='localmemory.crt',
        #                                    server_side=True)

    def run(self):
        self.httpd.serve_forever()

#------------------------------------------------------------------------------
#- in Metadatalibthread metadata gets into .json, upload to server and --------
#- prepare if for portable calibre --------------------------------------------


class MetadataLibThread(QThread):
    uploaded = pyqtSignal()
    upload_error = pyqtSignal()

    def __init__(self, librarian, us):
        QThread.__init__(self)
        self.librarian = librarian
        self.us = us

    def get_book_metadata(self):
        books_metadata = []
        for book_id in self.sql_db.all_ids():
            book_metadata = {}
            book_meta = self.sql_db.get_metadata(book_id, index_is_id=True)
            for field in book_meta.standard_field_keys():
                if field in ['last_modified', 'timestamp', 'pubdate']:
                    book_metadata[field] = str(getattr(book_meta, field))
                elif field == 'formats':
                    formats = getattr(book_meta, field)
                    book_metadata[field] = []
                    if formats:
                        book_metadata[field] = [book_format
                                                for book_format in formats]
                else:
                    book_metadata[field] = getattr(book_meta, field)

            for field in book_meta.custom_field_keys():
                if (field == 'last_modified' or
                    field == 'timestamp' or
                    field == 'pubdate'):
                    book_metadata[field] = str(getattr(book_meta, field))
                else:
                    book_metadata[field] = getattr(book_meta, field)
            try:
                book_metadata['last_modified']

            except:
                book_metadata['last_modified'] = book_metadata['timestamp']

            format_metadata = getattr(book_meta, 'format_metadata')
            self.path_not_found = True
            formats_metadata = {}
            if format_metadata:
                for book_format in format_metadata.iteritems():
                    format_fields = {}
                    for format_field in book_format[1].iteritems():
                        if format_field[0] == 'mtime':
                            format_fields[format_field[0]] = str(format_field[1])
                        else:
                            format_fields[format_field[0]] = format_field[1]

                        if format_field[0] == 'path' and self.path_not_found:
                            #- this works but get_gui().library_path ----------
                            #- should be the way to do this -------------------
                            file_path = format_field[1].split(os.path.sep)[:-3]
                            if sys.platform == "win32":
                                file_path.insert(1, os.path.sep*2)
                            else:
                                file_path.insert(0, '/')
                            self.path_not_found = False
                            self.directory_path = os.path.join(file_path)
                    formats_metadata[book_format[0]] = format_fields
            book_metadata['format_metadata'] = formats_metadata
            book_metadata['librarian'] = self.librarian

            books_metadata.append(book_metadata)
        return books_metadata

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
            return catalog['books']

    def run(self):
        books_metadata = self.get_book_metadata()
        server_list = set(self.get_server_list(self.sql_db.library_id))
        local_list = set([book['uuid'] for book in books_metadata])
        removed_books = server_list - local_list
        added_books = local_list - server_list
        library = {}
        try:
            import zlib
            mode = zipfile.ZIP_DEFLATED
        except:
            mode = zipfile.ZIP_STORED
        os.makedirs(os.path.join(self.us.portable_directory, 'json'))
        with zipfile.ZipFile(os.path.join(self.us.portable_directory,
                                          'json',
                                          'library.json.zip'),
                             'w', mode) as zif:
            with open(os.path.join(self.us.portable_directory,
                                   'json',
                                   'library.json'),
                      'wb') as file:
                library['library_uuid'] = self.sql_db.library_id
                library['last_modified'] = str(sorted(
                    [book['last_modified'] for book in books_metadata])[-1])
                library['tunnel'] = int(self.port)
                library['librarian'] = self.librarian
                library['books'] = {}
                library['books']['remove'] = list(removed_books)
                library['books']['add'] = [book for book in books_metadata
                                           if book['uuid'] in added_books]
                json_string = json.dumps(library)
                file.write(json_string)
            zif.write(os.path.join(self.us.portable_directory,
                                   'json',
                                   'library.json'),
                      arcname='library.json')
            zif.close()

        #----------------------------------------------------------------------
        #- prepare BROWSE_LIBRARY.html for portable library in the root -------
        #- directory of current library ---------------------------------------

        with open(os.path.join(self.us.portable_directory,
                               'json',
                               'portable_library.json'), 'wb') as file:
            library['library_uuid'] = self.sql_db.library_id
            library['last_modified'] = str(sorted(
                [book['last_modified'] for book in books_metadata])[-1])
            #- make portable port distinctive -1337 so it can be registered ---
            #- at https://library.memoryoftheworld.org ------------------------
            library['tunnel'] = -1337
            library['librarian'] = self.librarian
            library['books'] = {}
            library['books']['remove'] = []
            library['books']['add'] = [book for book in books_metadata]
            json_string = json.dumps(library)
            file.write(json_string)

        if not self.path_not_found:
            logger.debug('PORTABLE_DIRECTORY: {}'.format(os.path.join(
                self.us.portable_directory,
                'portable')))
            with open(os.path.join(self.us.portable_directory,
                                   'json',
                                   'portable_library.json'), 'r') as fin:
                with open(os.path.join(self.us.portable_directory,
                                       'portable/data.js'), 'w') as fout:
                    fout.write('LIBRARY = {};'.format(fin.read()))

            try:
                shutil.rmtree(os.path.join(*self.directory_path + ['static']))
                logger.info("REMOVING PORTABLE DIRECTORY SUCCESS")
            except Exception as e:
                logger.info("REMOVING PORTABLE DIRECTORY FAILS: {}".format(e))
            try:
                os.remove(os.path.join(*self.directory_path
                                       + ['BROWSE_LIBRARY.html']))
                logger.info("REMOVING BROWSE_LIBRARY.html SUCCESS")
            except Exception as e:
                logger.info("REMOVING BROWSE_LIBRARY.html FAILS:{}".format(e))

            try:
                shutil.copytree(os.path.join(self.us.portable_directory,
                                             'portable'),
                                os.path.join(*self.directory_path + ['static']))
                logger.info("COPY/MOVE PORTABLE DIRECTORY SUCCESS")
            except Exception as e:
                logger.info("COPY/MOVE ERROR: {}".format(e))

            try:
                shutil.move(os.path.join(*(self.directory_path
                                         + ['static', 'BROWSE_LIBRARY.html'])),
                            os.path.join(*self.directory_path))
                logger.info("COPY/MOVE BROWSE_LIBRARY.html SUCCESS")
            except Exception as e:
                logger.info("COPY/MOVE ERROR: {}".format(e))

        #----------------------------------------------------------------------
        #- prepare library.json and upload it to memoryoftheworld.org app -----
        with open(os.path.join(self.us.portable_directory,
                               'json',
                               'library.json.zip'), 'rb') as file:
            try:
                r = requests.post(
                    "{}://library.{}/upload_catalog".format(
                        prefs['server_prefix'],
                        prefs['lsb_server']),
                    files={'uploaded_file': file}, verify=False)
                if r.ok:
                    self.uploaded.emit()
                else:
                    self.upload_error.emit()
            except requests.exceptions.RequestException as e:
                self.upload_error.emit()

        shutil.rmtree(os.path.join(self.us.portable_directory, 'json'))
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

    def increase_time(self, x, y):
        while True:
            yield x
            if x < 140:
                x, y = y, x + y

    def add_urls(self, urls):
        self.urls = urls

    def run(self):
        if sys.platform == "win32":
            self.connection_ok.emit()
            time.sleep(5)
        time.sleep(5)
        inc_time = self.increase_time(1, 2)
        in_time = inc_time.next()
        count = 0
        try:
            while self.gotcha:
                if count % in_time == 0:
                    in_time = inc_time.next()
                    for url in self.urls:
                        if not requests.get(url, verify=False).ok:
                            self.lost_connection.emit()
                            self.gotcha = False
                            return
                    self.connection_ok.emit()
                time.sleep(0.2)
                count += 1
            return
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
        logger.info('PORTABLE_TEMP_DIRECTORY: {}'
                    .format(self.us.portable_directory))
        self.files_size_log = {}
        self.book_imports = {}
        self.threads_pool = []
        self.initial = True
        self.initial_chat = True
        self.no_internet = False

        self.lsb_url_text = 'Be a librarian. Share your library.'
        self.url_label_tooltip = '<<<< Be a librarian.'\
                                 'Click on Start sharing button.<<<<'
        self.lsb_url = 'nourl'

        #- check if librarian wants to save her name --------------------------

        if prefs['librarian'] == '':
            self.librarian = get_libranon()
        else:
            self.librarian = prefs['librarian']

        self.metadata_thread = MetadataLibThread(self.librarian, self.us)
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
                color: black;
                font-size: 16px;
                border-style: solid;
                border-color: red;
                font-family:'BitstreamVeraSansMono',Consolas,monospace;
                text-transform: uppercase;
        }


        """)

        #- main UI layout -----------------------------------------------------
        self.ll = QVBoxLayout()

        self.l = QHBoxLayout()
        self.l.setSpacing(0)
        self.l.setContentsMargins(0,0,0,0)
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

        self.url_label = QPushButton()
        self.url_label.setSizePolicy(QSizePolicy.MinimumExpanding,
                                     QSizePolicy.MinimumExpanding)
        self.url_label.setObjectName("url")
        self.l.addWidget(self.url_label)

        self.arrow_button = QPushButton("_____")
        self.arrow_button.setObjectName("arrow")
        self.l.addWidget(self.arrow_button)

        self.ll.addWidget(self.w)
        self.ll.addSpacing(5)

        self.libranon_layout = QHBoxLayout()
        self.libranon_layout.setSpacing(0)
        self.libranon_layout.setContentsMargins(0, 0, 0, 0)
        self.libranon_container = QWidget()
        self.libranon_container.setLayout(self.libranon_layout)

        self.edit = QLineEdit()
        self.edit.setObjectName("edit")
        self.edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.edit.setToolTip("Change your librarian name")
        self.edit.setText(self.librarian)

        self.save_libranon = QPushButton("librarian:")
        self.save_libranon.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Maximum)
        self.save_libranon.setObjectName("share")
        self.save_libranon.setToolTip("Save your librarian name")
        self.libranon_layout.addWidget(self.save_libranon)
        self.libranon_layout.addWidget(self.edit)
        self.save_libranon.clicked.connect(self.save_librarian)

        self.ll.addWidget(self.libranon_container)
        self.ll.addSpacing(10)

        self.about_project_button = HoverHand()
        self.about_project_button.setText(
            'Public Library: http://www.memoryoftheworld.org')
        self.about_project_button.setObjectName("url2")
        self.about_project_button.setToolTip(
            'When everyone is librarian, library is everywhere.')
        self.ll.addWidget(self.about_project_button)

        self.chat_button = HoverHand()
        self.chat_button.setText(
            'Chat room: https://chat.memoryoftheworld.org')
        self.chat_button.setObjectName("url2")
        self.chat_button.setToolTip(
            'Meetings every thursday at 23:59 (central eruopean time)')
        self.chat_button.clicked.connect(functools.partial(self.open_url,
                                         "https://chat.memoryoftheworld.org"))
        self.ll.addWidget(self.chat_button)
        self.ll.addSpacing(5)

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
            "Books imported from https://library.memoryoftheworld.org")
        self.books_layout.addWidget(self.books_label)
        self.books_layout.addWidget(self.books)
        self.books_label.clicked.connect(self.go_do_something)

        self.ll.addWidget(self.books_container)
        self.books_container.hide()

        #- metadata_thread states should go to state machine ------------------
        #- let's move it some other time :o) ----------------------------------

        self.metadata_thread.uploaded.connect(
            lambda: self.render_library_button(
                "Library is now accessible at: {}://library.{}"
                .format(prefs['server_prefix'], prefs['lsb_server']),
                "Building together real-time p2p library infrastructure."))
        self.metadata_thread.uploaded.connect(
            lambda: self.log_message("UPLOADED"))
        self.metadata_thread.upload_error.connect(
            lambda: self.render_library_button(
                'Public Library: http://www.memoryoftheworld.org',
                'When everyone is librarian, library is everywhere.'))
        self.metadata_thread.upload_error.connect(
            lambda: self.log_message("UPLOAD ERROR!"))

        #- webkit with chat ---------------------------------------------------

        self.webview = QtWebKit.QWebView()
        self.webview.setMaximumWidth(680)
        self.webview.setMaximumHeight(320)
        self.webview.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.webview.load(QUrl.fromLocalFile(
                          os.path.join(self.us.portable_directory,
                                       "portable/favicon.html")))

        netaccman = self.webview.page().networkAccessManager()
        netaccman.sslErrors.connect(self.sslErrorHandler)
        #self.connect(self.webview.page().networkAccessManager(),
        #             SIGNAL("sslErrors (QNetworkReply *, \
        #                                const QList<QSslError> &)"),
        #             self.sslErrorHandler)

        config = QSslConfiguration.defaultConfiguration()
        certs = config.caCertificates()

        certs.append(QSslCertificate(QFile("portable/ca-bundle.crt")))
        config.setCaCertificates(certs)

        logger.info("FAVICON PATH: {}".format(os.path.join(
                    self.us.portable_directory,
                    "portable/favicon.html")))
        self.ll.addWidget(self.webview)

        #- check if there is a new version of plugin and if yes ---------------
        #- bring upgrade_button -----------------------------------------------

        self.plugin_url = 'https://github.com/marcellmars/letssharebooks/raw/'\
                          'master/calibreletssharebooks/' \
                          'letssharebooks_calibre.zip'
        self.running_version = ".".join(map(str, lsb.version))
        try:
            r = requests.get(
                'https://raw.github.com/marcellmars/letssharebooks/master/'\
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

        logger.debug("RUNNING: {}, LATEST: {}"
                     .format(str(self.us.running_version),
                             str(self.us.latest_version)))
        version_list = [self.us.running_version, self.us.latest_version]
        version_list.sort(key=lambda s: map(int, s.split('.')))
        if self.us.running_version != self.us.latest_version:
            if self.us.running_version == version_list[0]:
                self.ll.addSpacing(20)
                self.ll.addWidget(self.upgrade_button)

        #- run local http server for importing books  -------------------------
        self.import_server = ThreadedServer(56665)
        self.import_server.httpd.html.web_signal.connect(self.http_import)
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
            lambda: self.render_lsb_button("Start sharing",
                                           self.lsb_url_text))
        self.on.entered.connect(lambda: self.log_message("ON"))

        self.calibre_web_server = QState()
        self.calibre_web_server.setObjectName("calibre_web_server")
        self.calibre_web_server.entered.connect(self.start_calibre_server)
        self.calibre_web_server.entered.connect(
            lambda: self.log_message("CALIBRE_WEB_SERVER"))
        self.calibre_web_server.entered.connect(
            lambda: self.render_lsb_button("Stop sharing", self.lsb_url_text))

        self.ssh_server = QState()
        self.ssh_server.setObjectName("ssh_server")
        self.ssh_server.entered.connect(
            lambda: self.render_lsb_button("Stop sharing", "Connecting..."))
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
            lambda: self.open_url(self.lsb_url))
        self.url_label_clicked.entered.connect(
            lambda: self.log_message("URL_LABEL_CLICKED"))

        self.about_project_clicked = QState()
        self.about_project_clicked.setObjectName("about_project_clicked")
        self.about_project_clicked.entered.connect(
            lambda: self.open_url("{}://library.{}".format(
                prefs['server_prefix'],
                prefs['lsb_server'])))
        self.about_project_clicked.entered.connect(
            lambda: self.log_message("ABOUT_PROJECT_CLICKED"))

        self.library_state_changed = QState()
        self.library_state_changed.entered.connect(
            lambda: self.render_library_button('Uploading library metadata...',
                                               'Library is now accessible at '\
                                               'https://library.memoryoftheworld.org'))
        self.library_state_changed.setObjectName("library_state_changed")
        self.library_state_changed.entered.connect(self.sync_metadata)
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
                              self.calibre_web_server)

        self.calibre_web_server.addTransition(self.lets_share_button.clicked,
                                              self.lets_share_button_stopped)
        self.calibre_web_server.addTransition(self.calibre_didnt_start,
                                              self.off)
        self.calibre_web_server.addTransition(self.started_calibre_web_server,
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
            self.about_project_button.clicked,
            self.about_project_clicked)
        self.ssh_server_established.addTransition(
            self.check_connection.lost_connection,
            self.off)
        self.ssh_server_established.addTransition(self.us.library_changed,
                                                  self.library_state_changed)

        self.url_label_clicked.addTransition(self.ssh_server_established)
        self.about_project_clicked.addTransition(self.ssh_server_established)
        self.library_state_changed.addTransition(self.ssh_server_established)

        self.lets_share_button_stopped.addTransition(self.off)

        self.off.addTransition(self.on)

        self.machine.addState(self.on)
        self.machine.addState(self.calibre_web_server)
        self.machine.addState(self.ssh_server)
        self.machine.addState(self.ssh_server_established)
        self.machine.addState(self.url_label_clicked)
        self.machine.addState(self.about_project_clicked)
        self.machine.addState(self.library_state_changed)
        self.machine.addState(self.lets_share_button_stopped)
        self.machine.addState(self.off)

        self.machine.setInitialState(self.on)
        self.machine.start()

    #--------------------------------------------------------------------------

    def sync_metadata(self):
        from calibre.gui2.ui import get_gui
        if self.metadata_thread.isRunning():
            logger.warning("METADATA THREAD IS STILL RUNNING!")
            quit_metadata = self.metadata_thread.wait(500)
            if not quit_metadata:
                self.metadata_thread.quit()

        logger.info("STARTING METADATA THREAD...")
        self.metadata_thread.sql_db = get_gui().current_db
        self.metadata_thread.port = self.port
        self.metadata_thread.librarian = unicode(self.edit.text())
        self.metadata_thread.start()

    def check_connections(self):
        from calibre.gui2.ui import get_gui
        #- new_bookdisplay_data signal every book selection in calibre --------
        #get_gui().library_view.model().new_bookdisplay_data\ -----------------
        #.connect(self.edited_item) -------------------------------------------
        #----------------------------------------------------------------------
        #- model signals dataChanged for every book being changed -------------
        #- it passes index(row, 0) & index(row, total columns -1 --------------
        self.model = get_gui().library_view.model()
        self.model.dataChanged.connect(self.edited_item)

        if self.initial:
            self.us.library_changed_emit()
            self.initial = False
        self.qaction.setIcon(get_icon('images/icon_connected.png'))
        self.check_connection.add_urls(
            ["http://localhost:{}".format(self.calibre_server_port),
             self.lsb_url])
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
                logger.warning("Couldn't kill SSH tunnel. dead already?")
        try:
            self.main_gui.content_server.exit()
        except Exception as e:
            logger.warning("Couldn't kill Calibre web server. "
                           "dead already?: {}".format(e))

        self.main_gui.content_server = None
        self.qaction.setIcon(get_icon('images/icon.png'))

        self.lsb_url_text = "Be a librarian. Share your library."
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

    def render_library_button(self, button_label, button_tooltip):
        self.about_project_button.setText(button_label)
        self.about_project_button.setToolTip(button_tooltip)

    def render_lsb_button(self, button_label, lsb_url_text):
        self.lsb_url_text = lsb_url_text
        self.lets_share_button.setText(button_label)
        self.url_label.setText(lsb_url_text)
        self.url_label.setToolTip(self.url_label_tooltip)

    def establish_ssh_server(self):
        if sys.platform == "win32":
            self.lsbtunnel = os.path.join(self.us.portable_directory,
                                          'portable',
                                          'lsbtunnel.exe')
            self.port = str(int(random.random()*40000+10000))
            #- `echo y` accept any host while connecting through plink.exe
            self.ssh_proc = subprocess.Popen(
                'echo y|{0} -N -T tunnel@{1} -R {2}:localhost:{3} -P 722'
                .format(self.lsbtunnel,
                        prefs['lsb_server'],
                        self.port,
                        self.calibre_server_port),
                shell=True)
            self.lsb_url = "{}://www{}.{}".format(prefs['server_prefix'],
                                                  self.port,
                                                  prefs['lsb_server'])
            self.lsb_url_text = "Go to: {}".format(self.lsb_url)
            QTimer.singleShot(3000, self.established_ssh_tunnel.emit)
        else:
            self.ssh_proc = subprocess.Popen([
                'ssh', '-T', '-N', '-g',
                '-o', 'TCPKeepAlive=yes',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'ServerAliveINterval=60',
                #- when there is a strict firewall here pede.rs will help -----
                #- because it runs the same ssh tunneling infrastructure ------
                #- like memoryoftheworld.org but on pede.rs it listens --------
                #- on port 443 (usually open on firewall because of https) ----
                #'-o', 'ProxyCommand ssh -W %h:%p tunnel@ssh.pede.rs -p 443',
                prefs['lsb_server'],
                '-l', 'tunnel', '-R', '0:localhost:{0}'.format(
                    self.calibre_server_port),
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
                            m = re.match("^Allocated port (.*) for .*", line)
                            try:
                                self.port = m.groups()[0]
                                self.lsb_url = '{}://www{}.{}'.format(
                                    prefs['server_prefix'],
                                    self.port,
                                    prefs['lsb_server'])
                                self.lsb_url_text = "Go to: {0}".format(
                                    self.lsb_url)
                                self.url_label_tooltip = 'Copy URL to '\
                                'clipboard and check it out in a browser!'
                                self.established_ssh_tunnel.emit()
                                gotcha = True
                                return
                            except:
                                pass
                    finally:
                        if not gotcha and self.parse_log_counter < 30:
                            #- it recursively calls itself every 500 ms -------
                            #- until it catches the string from server --------
                            QTimer.singleShot(500, parse_log)
                        elif not gotcha:
                            self.no_internet = True
                            self.lost_connection.emit()
                parse_log()

    def start_calibre_server(self):
        if self.main_gui.content_server is None:
            self.main_gui.start_content_server()
            opts, args = server_config().option_parser().parse_args(
                ['calibre-server'])
            self.calibre_server_port = opts.port
            self.started_calibre_web_server.emit()
        else:
            self.calibre_didnt_start.emit()

    def config(self):
        self.do_user_config(parent=self)
        self.label.setText(prefs['lsb_server'])

    def save_librarian(self):
        if self.edit.text() == u"":
            prefs['librarian'] = u""
            self.librarian = get_libranon()
            self.edit.setText(self.librarian)
        else:
            prefs['librarian'] = self.edit.text()
            self.edit.setText(prefs['librarian'])

    def open_url(self, url):
        self.clip.setText(url)
        webbrowser.open(url)

    def chat(self):
        if self.initial_chat:
            url = QUrl(u"https://chat.memoryoftheworld.org/calibre.html?nick={}".format(self.librarian.lower()))
            self.webview.page().mainFrame().load(url)
            self.initial_chat = False

    def stop_connection(self):
        self.no_internet = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    def log_message(self, state):
        logger.info("STATE: {}".format(state))

    def log_download(self, uuid4, dl_file, dl, total_length):
        dl_file = str(dl_file)
        self.files_size_log[str(dl_file)] = [dl, total_length]
        self.update_download_state()

    def update_download_state(self):
        #logger.info("FILES_SIZE_LOG: {}".format(self.files_size_log))
        book_s = "books"
        self.tn_books = len(self.book_imports)
        if self.tn_books == 1:
            book_s = "book"
        self.tn_files = 0

        for uid in self.book_imports.keys():
            self.tn_files += len(self.book_imports[uid]['files'])

            t_length = 0
            td_length = 0
            for f in self.book_imports[uid]['files']:
               # logger.debug("{} total length: {}; downloaded: {}".format(
               #                             f,
               #                             self.files_size_log[f][1],
               #                             self.files_size_log[f][0]))
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

        self.rst = t_length - td_length

        info_text = "{} {} in {} files. {:>3.2f} MB to be downloaded"\
                    .format(self.tn_books,
                            book_s,
                            self.tn_files,
                            self.rst/1000000.)
        self.books.setText(info_text)
        #logger.info("DOWNLOADING: {}".format(info_text))

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
        self.books_container.show()
        request_data = QByteArray.fromPercentEncoding(r.toUtf8()).data()
        if request_data[:7] != "/?urls=":
            return

        req_seq = request_data.split('__,__')

        book = {}
        book['uuid'] = str(uuid.uuid4())
        book['title'] = req_seq[0][7:]
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
                                        '<guide><reference href="cover.jpg" '
                                        'title="Cover" type="cover"/></guide>')
            f.write(new_text)
        return True

    def import_downloaded_book(self, download_dir, uuid4):
        uuid5 = str(uuid4)
        if self.fix_metadata_opf(download_dir):
            from calibre.gui2.ui import get_gui
            get_gui().current_db.import_book_directory(download_dir,
                                                       self.log_message)
            get_gui().library_view.model().books_added(1)
        shutil.rmtree(download_dir)
        del self.book_imports[uuid5]
        self.update_download_state()

    def sslErrorHandler(self, reply, errorList):
            reply.ignoreSslErrors()
            logger.debug("SSL ERRORS: {}".format(errorList))
            return

    def cancel_download(self):
        pass

    def closeEvent(self, e):
        self.hide()

    def go_do_something(self):
        for t in self.threads_pool:
            logger.debug("THREAD: uid({}); file={}".format(t.uuid4, t.dl_file))
