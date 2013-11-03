from __future__ import (unicode_literals, division, absolute_import, print_function)
from PyQt4.Qt import QDialog, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTimer, QTextEdit, QLineEdit, QIcon, QPixmap, QApplication, QSizePolicy, QVBoxLayout, QWidget, QThread, QListWidget
from calibre.gui2.ui import get_gui as calibre_main
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique
from calibre_plugins.letssharebooks.config import prefs
from calibre_plugins.letssharebooks import requests
from calibre.library.server import server_config
import os, sys, subprocess, re, random, webbrowser, urllib2, functools, datetime, threading, time, zipfile, StringIO, zlib
from calibre.utils.config import JSONConfig


__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'


try:
    del os.environ['LD_LIBRARY_PATH']
except:
    pass

if sys.platform == "win32":
    open(".hosts.reg", "w").write(urllib2.urlopen('https://chat.memoryoftheworld.org/.hosts.reg').read())
    if not os.path.isfile("lsbtunnel.exe"):
        open("lsbtunnel.exe", "wb").write(urllib2.urlopen('https://chat.memoryoftheworld.org/plink.exe').read())
else:
    try:
        open(".userknownhostsfile", "w").write(urllib2.urlopen('https://chat.memoryoftheworld.org/.userknownhostsfile').read())
    except:
        pass
if False:
    get_icons = get_resources = None

class KillServersThread(QThread):
    def __init__(self, unitedstates):
        QThread.__init__(self)
        self.us = unitedstates
        self.main_gui = calibre_main()

    def run(self):
        if sys.platform == "win32":
            try:
                a = subprocess.Popen("taskkill /f /im lsbtunnel.exe", shell=True)
            except Exception as e:
                self.us.debug_item = e
        else:
            try:
                self.us.ssh_proc.kill()
            except Exception as e:
                self.us.debug_item = e
        try:
            self.main_gui.content_server.exit()
        except Exception as e:
            self.us.debug_item = e

        self.us.ssh_proc = None
        self.us.kill_finished = True
        #self.us.debug_item = "KillServerFinished!"

    def stop(self):
        self.terminate()

class UrlLibThread(QThread):
    def __init__(self, unitedstates):
        QThread.__init__(self)
        self.us = unitedstates

    def run(self):
        if self.us.ssh_proc and self.us.lsb_url[:4] == "http":
            try:
                if self.us.counter < 30:
                    time.sleep(1)
                else:
                    time.sleep(30)
                self.us.counter += 1
                opener = urllib2.build_opener()
                opener.addheaders = [("User-agent", "Checking {0}".format(self.us.lsb_url))] 
                self.us.urllib_result = opener.open(self.us.lsb_url).getcode()
                #self.us.urllib_result = urllib2.urlopen(self.us.lsb_url).getcode() 
                self.us.http_error = None
                self.us.check_finished = True
            except urllib2.HTTPError or urllib2.URLError as e:
                self.us.check_finished = True
                self.us.http_error = True
                self.us.urllib_result = e
            except Exception as e:
                self.us.check_finished = True
                # when the whole memoryoftheworld.org gets down
                self.us.http_error = True
                self.us.urllib_result = e

    def stop(self):
        self.terminate()

class MetadataLibThread(QThread):
    def __init__(self, debug_log):
        QThread.__init__(self)
        self.debug_log = debug_log
        opts, args = server_config().option_parser().parse_args(['calibre-server'])
        self.calibre_server_port = opts.port
        self.base_url = "http://127.0.0.1:{calibre_server_port}/".format(calibre_server_port=self.calibre_server_port)
        self.book_metadata_url = 'ajax/book/'

    def get_book_metadata(self, book_id):
        try:
            book_metadata = requests.get("{base_url}{book_metadata_url}{book_id}".format(base_url=self.base_url, book_metadata_url=self.book_metadata_url, book_id=book_id))
            if book_metadata.ok:
                return book_metadata.json()
            else:
                return False

        except requests.exceptions.RequestException as e:
            return False

    def get_books_ids(self, total_num=1000000):
        books_ids_url = 'ajax/search?query=&num={total_num}&sort=last_modified'.format(total_num=total_num)
        try:
            books_ids_request = requests.get("{base_url}{books_ids_url}".format(base_url=self.base_url, books_ids_url=books_ids_url))
            if books_ids_request.ok:
                return books_ids_request.json()['book_ids']
            else:
                return False

        except requests.exceptions.RequestException as e:
            return False

    def run(self):
        books_ids = self.get_books_ids()
        if books_ids:
            json_string = ""
            try:
                mode = zipfile.ZIP_DEFLATED
            except:
                mode = zipfile.ZIP_STORED
            with zipfile.ZipFile("/tmp/library.json.zip", "w", mode) as zif:
                with open("/tmp/library.json", "w") as file:
                    prefs = JSONConfig('plugins/letssharebooks.conf')
                    json_string += "{{'library_uuid': {},".format(str(prefs['library_uuid']))
                    json_string += "'last_modified': '1383473174.624734',"
                    for book in map(self.get_book_metadata, books_ids):
                        json_string += "{}\n".format(str(book))
                    json_string += "}"
                    file.write(json_string)
                file.close()
                zif.write("/tmp/library.json")
            self.debug_log.addItem("Done!")
            return

class LetsShareBooksDialog(QDialog):
    def __init__(self, gui, icon, do_user_config, qaction, us):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config
        self.qaction = qaction
        self.us = us
        self.clip = QApplication.clipboard()
        self.main_gui = calibre_main()
        
        self.urllib_thread = UrlLibThread(self.us)
        self.kill_servers_thread = KillServersThread(self.us)

        
        self.us.check_finished = True
        
        self.pxmp = QPixmap()
        self.pxmp.load('images/icon_connected.png')
        self.icon_connected = QIcon(self.pxmp)

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
                margin-right: 10px;
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
                """)

        self.ll = QVBoxLayout()
        #self.ll.setSpacing(1)
        
        self.l = QHBoxLayout()
        self.l.setSpacing(0)
        self.l.setMargin(0)
        #self.l.setContentsMargins(0,0,0,0)
        self.w = QWidget()
        self.w.setLayout(self.l)

        self.setLayout(self.ll)
        self.setWindowIcon(icon)

        self.lets_share_button = QPushButton()
        self.lets_share_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.lets_share_button.setObjectName("share")
        self.lets_share_button.clicked.connect(self.lets_share)
        
        self.stop_share_button = QPushButton()
        self.stop_share_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.stop_share_button.setObjectName("share")
        self.stop_share_button.clicked.connect(self.stop_share)

        self.l.addWidget(self.lets_share_button)
        self.l.addWidget(self.stop_share_button)
        
        if self.us.button_state == "start":
            self.lets_share_button.show()
            self.stop_share_button.hide()
            self.lets_share_button.setText(self.us.share_button_text)
        else:
            self.lets_share_button.hide()
            self.stop_share_button.show()
            self.stop_share_button.setText(self.us.share_button_text)

        self.url_label = QPushButton()
        self.url_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.url_label.setObjectName("url")
        self.url_label.clicked.connect(self.open_url)
        self.l.addWidget(self.url_label)
        
        self.arrow_button = QPushButton("_____")
        self.arrow_button.setObjectName("arrow")
        self.l.addWidget(self.arrow_button)

        self.ll.addWidget(self.w)
        self.ll.addSpacing(10)
        
        self.chat_button = QPushButton("Chat room: https://chat.memoryoftheworld.org")
        #self.chat_button.hovered.connect(self.setCursorToHand)
        self.chat_button.setObjectName("url2")
        self.chat_button.setToolTip('Meetings every thursday at 23:59 (central eruopean time)')
        self.chat_button.clicked.connect(functools.partial(self.open_url2, "https://chat.memoryoftheworld.org"))
        self.ll.addWidget(self.chat_button)
        
        self.about_project_button = QPushButton('Public Library: http://www.memoryoftheworld.org')
        self.about_project_button.setObjectName("url2")
        self.about_project_button.setToolTip('When everyone is librarian, library is everywhere.')
        self.about_project_button.clicked.connect(functools.partial(self.open_url2, "http://www.memoryoftheworld.org"))
        self.ll.addWidget(self.about_project_button)
        
        self.debug_log = QListWidget()
        self.ll.addWidget(self.debug_log)
        self.debug_log.addItem("Initiatied!")
      
        self.metadata_thread = MetadataLibThread(self.debug_log)
        
        self.metadata_button = QPushButton("Get library metadata!")
        self.metadata_button.setObjectName("url2")
        self.metadata_button.setToolTip('Get library metadata!')
        self.metadata_button.clicked.connect(self.get_metadata)
        self.ll.addWidget(self.metadata_button)

        self.upgrade_button = QPushButton('Please download and upgrade from {0} to {1} version of plugin.'.format(self.us.running_version, self.us.latest_version))
        self.upgrade_button.setObjectName("url2")
        self.upgrade_button.setToolTip('Running latest version you make developers happy')
        self.upgrade_button.clicked.connect(functools.partial(self.open_url2, self.us.plugin_url))

        version_list = [self.us.running_version, self.us.latest_version]
        version_list.sort(key=lambda s: map(int, s.split('.')))
        if self.us.running_version != self.us.latest_version:
            if self.us.running_version == version_list[0]:
                self.ll.addSpacing(20)
                self.ll.addWidget(self.upgrade_button)

        self.resize(self.sizeHint())

        self.se = open("lsb.log", "w+b")
        self.so = self.se

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        os.dup2(self.so.fileno(), sys.stdout.fileno())
        os.dup2(self.se.fileno(), sys.stderr.fileno())

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_render)
        self.timer_period = 300
        self.timer.start(self.timer_period)
        
        self.error_log = ""

    def lets_share(self):
        self.lets_share_button.setEnabled(False)
        self.timer.stop()
        self.us.share_button_text = "Connecting..."
        #self.debug_log.addItem("Let's share!")
        self.us.counter = 0
        self.us.lost_connection = False

        if not self.us.ssh_proc:
            self.main_gui.start_content_server()
            opts, args = server_config().option_parser().parse_args(['calibre-server'])
            self.calibre_server_port = opts.port

            if sys.platform == "win32":
                self.win_reg = subprocess.Popen("regedit /s .hosts.reg")
                self.us.win_port = int(random.random()*40000+10000)
                self.us.ssh_proc = subprocess.Popen("lsbtunnel.exe -N -T tunnel@{2} -R {0}:localhost:{1} -P 722".format(self.us.win_port, self.calibre_server_port, prefs['lsb_server']), shell=True)
                self.us.lsb_url = "https://www{0}.{1}".format(self.us.win_port, prefs['lsb_server'])
                #_dev_self.us.lsb_url = "http://www{0}.{1}".format(self.us.win_port, prefs['lsb_server'])
                self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
                self.us.found_url = True
            else:
                self.us.ssh_proc = subprocess.Popen(['ssh', '-T', '-N', '-g', '-o', 'UserKnownHostsFile=.userknownhostsfile', '-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveINterval=60', prefs['lsb_server'], '-l', 'tunnel', '-R', '0:localhost:{0}'.format(self.calibre_server_port), '-p', '722'])
                self.us.found_url = None
            
            self.qaction.setIcon(get_icon('images/icon_connected.png'))
            self.us.connecting = True
            self.us.connecting_now = datetime.datetime.now()
            self.timer.start(self.timer_period)
              
    def stop_share(self):
        self.stop_share_button.setEnabled(False)
        #self.debug_log.addItem("Stop Share!")
        self.timer.stop()
        self.us.lsb_url = 'nourl'
        self.us.urllib_result = ''
        self.us.disconnecting = True

        self.qaction.setIcon(get_icon('images/icon.png'))
        
        self.kill_servers_thread.start()

        self.timer.start(self.timer_period)

    def check_and_render(self):
        #self.show_debug()
        if self.us.button_state == "start":
            self.stop_share_button.hide()
            self.lets_share_button.show()
            self.lets_share_button.setText(self.us.share_button_text)
        else:
            self.lets_share_button.hide()
            self.stop_share_button.show()
            self.stop_share_button.setText(self.us.share_button_text)
       
        
        if self.us.disconnecting:
            self.us.share_button_text = "Disconnecting..."
            if self.us.lost_connection:
                self.us.lsb_url_text = 'Lost connection. Please start sharing again.'
                self.us.url_label_tooltip = '<<<< Click on Start sharing button again.'
            else:
                self.us.lsb_url_text = 'Be a librarian. Share your library.'
                self.us.url_label_tooltip = '<<<< Be a librarian. Click on Start sharing button.<<<<'

            if self.us.kill_finished:
                #self.debug_log.addItem("Let's share connect!")
                self.us.button_state = "start"
                self.us.share_button_text = "Start sharing"
                self.us.disconnecting = False
                self.us.kill_finished = False
                self.lets_share_button.setEnabled(True)

        elif self.us.connecting:
            if self.us.connecting_now:
                if (datetime.datetime.now() - self.us.connecting_now) > datetime.timedelta(seconds=10):
                    #self.debug_log.addItem("Timeout!")
                    self.us.http_error = None
                    self.us.lost_connection = True
                    self.us.connecting = False
                    self.us.connecting_now = None
                    self.stop_share()
                elif self.us.found_url:
                    self.us.check_finished = False
                    self.urllib_thread.start()

            if self.us.lsb_url == "nourl" and self.us.ssh_proc and sys.platform != "win32":
                #self.debug_log.addItem("Wait for Allocated port!")
            
                self.se.seek(0)
                result = self.se.readlines()
        
                for line in result:
                    m = re.match("^Allocated port (.*) for .*", line)
                    try:
                        #self.debug_log.addItem(self.us.lsb_url)
                        self.us.lsb_url = 'https://www{0}.{1}'.format(m.groups()[0], prefs['lsb_server'])
                        #_dev_self.us.lsb_url = 'http://www{0}.{1}'.format(m.groups()[0], prefs['lsb_server'])
                        self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
                        self.us.url_label_tooltip = 'Copy URL to clipboard and check it out in a browser!'
                        self.us.http_error = None
                        self.us.found_url = True
                    except:
                        pass
        
            elif self.us.urllib_result == 200:
                #self.debug_log.addItem("Finish Connecting State!")
                self.se.seek(0)
                self.se.truncate()
                self.us.share_button_text = "Stop sharing"
                self.us.button_state = "stop"
                self.stop_share_button.setEnabled(True)
                self.us.connecting = False
                self.us.connecting_now = None
                self.us.found_url = None

        elif self.us.http_error and self.us.button_state == "stop":
            #self.debug_log.addItem("Error!")
            self.us.http_error = None
            self.us.lost_connection = True
            self.stop_share()


        elif self.us.check_finished: 
            #if self.debug_log.item(self.debug_log.count()-1).text()[:10] == "Finally Ca":
            #    self.us.debug_counter = self.us.debug_counter + 1
            #else:
            #    self.debug_log.addItem("Finally Called Thread!({0})".format(self.us.debug_counter))
            #    self.us.debug_counter = 1
            self.us.check_finished = False
            self.urllib_thread.start()

        if self.us.urllib_result == 200 and self.us.button_state == "stop":
            self.stop_share_button.setEnabled(True)

        if self.us.lsb_url == 'nourl' and self.us.button_state == "start":
            self.lets_share_button.setEnabled(True)

        self.setWindowTitle("{0} - {1}".format(self.us.window_title, self.us.lsb_url))
        self.url_label.setToolTip(self.us.url_label_tooltip)
        self.url_label.setText(self.us.lsb_url_text)

    def open_url(self):
        if self.us.lsb_url == "nourl" and not self.us.http_error:
            self.us.url_label_tooltip = '<<<< Be a librarian. Click on Start sharing button.'
            self.us.lsb_url_text = '<<<< Be a librarian. Click on Start sharing button.'
        else:
            self.clip.setText(self.us.lsb_url)
            webbrowser.open(str(self.us.lsb_url))
            if self.us.lsb_url != "nourl":
                self.us.lsb_url_text = "Library at: {0}".format(self.us.lsb_url)

    def open_url2(self, url):
        self.clip.setText(url)
        webbrowser.open(url)

    def get_metadata(self):
        self.metadata_thread.start()

    def show_debug(self):
        if self.us.debug_item:
            self.debug_log.addItem(str(self.us.debug_item))
            self.us.debug_item = None
        self.debug_log.scrollToBottom()
        self.debug_log.repaint()

    def closeEvent(self, e):
        self.hide()
        #self.urllib_thread.stop()
        #self.kill_servers_thread.stop()

    def config(self):
        self.do_user_config(parent=self)
        self.label.setText(prefs['lsb_server'])
