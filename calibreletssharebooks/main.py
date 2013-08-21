from __future__ import (unicode_literals, division, absolute_import, print_function)
from PyQt4.Qt import QDialog, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTimer, QTextEdit, QLineEdit, QIcon, QPixmap, QApplication, QSizePolicy, QVBoxLayout, QWidget, QThread 
from calibre.gui2.ui import get_gui as calibre_main
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique
from calibre_plugins.letssharebooks.config import prefs
from calibre.library.server import server_config
import os, sys, subprocess, re, random, webbrowser, urllib2, functools, datetime, threading, time

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
    open(".userknownhostsfile", "w").write(urllib2.urlopen('https://chat.memoryoftheworld.org/.userknownhostsfile').read())

if False:
    get_icons = get_resources = None

class UrlLibThread(QThread):
    def __init__(self, unitedstates):
        QThread.__init__(self)
        self.us = unitedstates

    def run(self):
        if self.us.ssh_proc and self.us.lsb_url[:5] == "https":
            try:
                if self.us.counter > 10:
                    time.sleep(5)
                self.us.counter += 1
                opener = urllib2.build_opener()
                opener.addheaders = [("User-agent", "Checking {0}".format(self.us.lsb_url))] 
                self.us.urllib_result = opener.open(self.us.lsb_url).getcode()
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

        if self.us.button_state == "start" and not self.us.connecting:
            self.lets_share_button.clicked.connect(self.lets_share)
        elif self.us.button_state == "stop":
            self.lets_share_button.clicked.connect(self.stop_share)


        self.l.addWidget(self.lets_share_button)

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
        
        self.debug_log = QTextEdit()
        self.ll.addWidget(self.debug_log)
       
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

    def kill_servers(self):
        if sys.platform == "win32":
            try:
                a = subprocess.Popen("taskkill /f /im lsbtunnel.exe", shell=True)
            except:
                pass
        else:
            try:
                self.us.ssh_proc.kill()
            except:
                pass
        try:
            self.main_gui.content_server.exit()
        except:
            pass

        self.us.ssh_proc = None


    def lets_share(self):
        self.kill_servers()
        self.us.counter = 0

        if not self.us.ssh_proc:
            self.main_gui.start_content_server()
            opts, args = server_config().option_parser().parse_args(['calibre-server'])
            self.calibre_server_port = opts.port

            if sys.platform == "win32":
                self.win_reg = subprocess.Popen("regedit /s .hosts.reg")
                self.us.win_port = int(random.random()*40000+10000)
                self.us.ssh_proc = subprocess.Popen("lsbtunnel.exe -N -T tunnel@ssh.memoryoftheworld.org -R {0}:localhost:{1} -P 722".format(self.us.win_port, self.calibre_server_port), shell=True)
                self.us.lsb_url = "https://www{0}.memoryoftheworld.org".format(self.us.win_port)
                self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
                self.us.check_finished = False
                self.urllib_thread.start()
            else:
                self.us.ssh_proc = subprocess.Popen(['ssh', '-T', '-N', '-g', '-o', 'UserKnownHostsFile=.userknownhostsfile', '-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveINterval=60', 'ssh.memoryoftheworld.org', '-l', 'tunnel', '-R', '0:localhost:{0}'.format(self.calibre_server_port), '-p', '722'])
            
            self.qaction.setIcon(get_icon('images/icon_connected.png'))
            self.lets_share_button.clicked.disconnect()
            self.us.share_button_text = "Connecting..."
            self.us.connecting = True
              
    def stop_share(self):
        self.us.lsb_url = 'nourl'
        self.us.urllib_result = ''

        self.kill_servers()

        self.qaction.setIcon(get_icon('images/icon.png'))

        self.lets_share_button.clicked.disconnect()
        self.lets_share_button.clicked.connect(self.lets_share)

        if self.us.lost_connection:
            self.us.lost_connection = False
            self.us.lsb_url_text = 'Lost connection. Please start sharing again.'
            self.us.url_label_tooltip = '<<<< Click on Start sharing button again.'
        else:
            self.us.url_label_tooltip = '<<<< Be a librarian. Click on Start sharing button.'
            self.us.lsb_url_text = '<<<< Be a librarian. Click on Start sharing button.'

              
        self.us.share_button_text = "Start sharing"
        self.us.button_state = "start"

    def check_and_render(self):
        self.debug_log.setPlainText("lsb_url: {0}, urllib_result:{1}, connecting:{2}, counter: {3}".format(self.us.lsb_url, self.us.urllib_result, self.us.connecting, str(self.us.counter)))

        if self.us.check_finished:
            self.us.check_finished = False
            self.urllib_thread.start()
        
        if self.us.lsb_url == "nourl" and self.us.ssh_proc:
            
            self.se.seek(0)
            result = self.se.readlines()
        
            for line in result:
                m = re.match("^Allocated port (.*) for .*", line)
                try:
                    self.us.lsb_url = 'https://www{0}.memoryoftheworld.org'.format(m.groups()[0])
                    self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
                    self.us.url_label_tooltip = 'Copy URL to clipboard and check it out in a browser!'
                    self.us.http_error = None
                    self.us.check_finished = False
                    self.urllib_thread.start()
                except:
                    pass
        
            self.se.seek(0)
            self.se.truncate()
        
        
        if self.us.urllib_result == 200 and self.us.connecting == True:
            self.us.connecting = False
            self.lets_share_button.clicked.connect(self.stop_share)
            self.us.share_button_text = "Stop sharing"
            self.us.button_state = "stop"

        elif self.us.http_error and self.us.button_state != "start":
            self.us.lost_connection = True
            self.us.http_error = None
            self.stop_share()

        self.setWindowTitle("{0} - {1}".format(self.us.window_title, self.us.lsb_url))
        self.url_label.setToolTip(self.us.url_label_tooltip)
        self.lets_share_button.setText(self.us.share_button_text)
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

    def config(self):
        self.do_user_config(parent=self)
        self.label.setText(prefs['hello_world_msg'])
