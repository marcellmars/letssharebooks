from __future__ import (unicode_literals, division, absolute_import, print_function)
from PyQt4.Qt import QDialog, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTimer, QTextEdit, QLineEdit, QIcon, QPixmap, QApplication, QSizePolicy, QVBoxLayout, QWidget
from calibre.gui2.ui import get_gui as calibre_main
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique
from calibre_plugins.letssharebooks.config import prefs

import os, sys, subprocess, re, random, webbrowser, urllib2

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

class LetsShareBooksDialog(QDialog):

    def __init__(self, gui, icon, do_user_config, qaction, us):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config
        self.qaction = qaction
        self.us = us
        self.clip = QApplication.clipboard()
        self.main_gui = calibre_main()
        
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
                padding: -9px;
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
        if not self.us.ssh_proc:
            self.lets_share_button.clicked.connect(self.lets_share)
        else:
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
        self.chat_button.setObjectName("url2")
        self.chat_button.setToolTip('Meetings every thursday at 23:59 (central eruopean time)')
        self.chat_button.clicked.connect(self.open_chat)
        self.ll.addWidget(self.chat_button)
        
        self.about_project_button = QPushButton('Public Library: http://www.memoryoftheworld.org')
        self.about_project_button.setObjectName("url2")
        self.about_project_button.setToolTip('When everyone is librarian, library is everywhere.')
        self.about_project_button.clicked.connect(self.open_about_project)
        self.ll.addWidget(self.about_project_button)
        
        self.resize(self.sizeHint())

        self.se = open("lsb.log", "w+b")
        self.so = self.se

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        os.dup2(self.so.fileno(), sys.stdout.fileno())
        os.dup2(self.se.fileno(), sys.stderr.fileno())

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_render)
        self.timer.start(300)

    def lets_share(self):
        if not self.us.ssh_proc:
            self.main_gui.start_content_server()
            if sys.platform == "win32":
                self.win_reg = subprocess.Popen("regedit /s .hosts.reg")
                self.us.win_port = int(random.random()*40000+10000)
                self.us.ssh_proc = subprocess.Popen("lsbtunnel.exe -N -T tunnel@ssh.memoryoftheworld.org -R {0}:localhost:8080 -P 722".format(int(self.us.win_port)), shell=True)
                self.us.lsb_url = "https://www{0}.memoryoftheworld.org".format(self.us.win_port)
                self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
            else:
                self.us.ssh_proc = subprocess.Popen(['ssh', '-T', '-N', '-g', '-o', 'UserKnownHostsFile=.userknownhostsfile', '-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveINterval=60', 'ssh.memoryoftheworld.org', '-l', 'tunnel', '-R', '0:localhost:8080', '-p', '722'])
            
            self.qaction.setIcon(get_icon('images/icon_connected.png'))
            self.lets_share_button.clicked.disconnect(self.lets_share)
            self.lets_share_button.clicked.connect(self.stop_share)
            self.us.share_button_text = "Stop sharing"
   
    def stop_share(self):
        self.qaction.setIcon(get_icon('images/icon.png'))
        self.lets_share_button.clicked.disconnect(self.stop_share)
        self.lets_share_button.clicked.connect(self.lets_share)
        self.us.share_button_text = "Start sharing"
        self.us.lsb_url = 'http://www.memoryoftheworld.org'
        self.us.lsb_url_text = 'Be a librarian. Share your library.'
        if sys.platform == "win32":
            a = subprocess.Popen("taskkill /f /im lsbtunnel.exe", shell=True)
        self.us.ssh_proc.kill()
        self.main_gui.content_server.exit()
        self.us.ssh_proc = None

    def check_and_render(self):
        self.setWindowTitle("{0} - {1}".format(self.us.window_title, self.us.lsb_url))
        self.url_label.setToolTip(self.us.url_label_tooltip)
        self.lets_share_button.setText(self.us.share_button_text)
        self.url_label.setText(self.us.lsb_url_text)
        
        self.se.seek(0)
        result = self.se.readlines()
        
        for line in result:
            m = re.match("^Allocated port (.*) for .*", line)
            try:
                self.us.lsb_url = 'https://www{0}.memoryoftheworld.org'.format(m.groups()[0])
                self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
                self.us.url_label_tooltip = 'Copy URL to clipboard and check it out in a browser!'
            except:
                pass
        
        self.se.seek(0)
        self.se.truncate()

    def open_url(self):
        if self.us.lsb_url == "http://www.memoryoftheworld.org":
            self.us.url_label_tooltip = '<<<< Be a librarian. Click on Start sharing button.'
            self.us.lsb_url_text = '<<<< Be a librarian. Click on Start sharing button.'
        else:
            self.clip.setText(self.us.lsb_url)
            webbrowser.open(str(self.us.lsb_url))
            if self.us.lsb_url != "http://www.memoryoftheworld.org":
                self.us.lsb_url_text = "Library at: {0}".format(self.us.lsb_url)

    def open_chat(self):
        self.clip.setText("https://chat.memoryoftheworld.org")
        webbrowser.open("https://chat.memoryoftheworld.org")

    def open_about_project(self):
        self.clip.setText("http://www.memoryoftheworld.org")
        webbrowser.open("http://www.memoryoftheworld.org")


    def config(self):
        self.do_user_config(parent=self)
        self.label.setText(prefs['hello_world_msg'])
