from __future__ import (unicode_literals, division, absolute_import, print_function)
from PyQt4.Qt import QDialog, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTimer, QTextEdit, QLineEdit, QIcon, QPixmap
from calibre.gui2.ui import get_gui as calibre_main
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique
from calibre_plugins.letssharebooks.config import prefs

import os, sys, inspect, subprocess, pty, re, tempfile, random, webbrowser, signal, urllib2

__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'


del os.environ['LD_LIBRARY_PATH']
open(".userknownhostsfile", "w").write(urllib2.urlopen('https://chat.memoryoftheworld.org/.userknownhostsfile').read())

if False:
    get_icons = get_resources = None

class LetsShareBooksDialog(QDialog):

    def __init__(self, gui, icon, do_user_config, qaction):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config
        self.qaction = qaction
        
        self.main_gui = calibre_main()
        
        self.pxmp = QPixmap()
        self.pxmp.load('images/icon_connected.png')
        self.icon_connected = QIcon(self.pxmp)

        self.ssh_proc = None

        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.setWindowTitle("Let's share books")
        self.setWindowIcon(icon)

        self.url_label = QPushButton(".....................")
        self.url_label.clicked.connect(self.open_url)
        self.l.addWidget(self.url_label)

        self.lets_share_button = QPushButton("Let's share", self)
        self.lets_share_button.clicked.connect(self.lets_share)
        self.l.addWidget(self.lets_share_button)

        self.resize(self.sizeHint())

        self.lsb_url = "http://www.memoryoftheworld.org"
        
        self.se = open("lsb.log", "w+b")
        self.so = self.se

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        os.dup2(self.so.fileno(), sys.stdout.fileno())
        os.dup2(self.se.fileno(), sys.stderr.fileno())

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_log)
        self.timer.start(1000)

    def lets_share(self):
        if not self.ssh_proc:
            self.main_gui.start_content_server()
            self.proc = subprocess.Popen(['ssh', '-T', '-N', '-g', '-o', 'UserKnownHostsFile=.userknownhostsfile', '-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveINterval=60', 'ssh.memoryoftheworld.org', '-l', 'tunnel', '-R', '0:localhost:8080', '-p', '722'])
            self.qaction.setIcon(get_icon('images/icon_connected.png'))
            self.lets_share_button.clicked.disconnect(self.lets_share)
            self.lets_share_button.clicked.connect(self.stop_share)
            self.lets_share_button.setText("Stop share")
   
    def stop_share(self):
        self.qaction.setIcon(get_icon('images/icon.png'))
        self.lets_share_button.clicked.disconnect(self.stop_share)
        self.lets_share_button.clicked.connect(self.lets_share)
        self.lets_share_button.setText("Let's share")
        self.lsb_url = "http://www.memoryoftheworld.org"
        self.url_label.setText(".....................")

        self.proc.kill()
        self.main_gui.content_server.exit()
        self.ssh_proc = None

    def check_log(self):
        self.se.seek(0)
        result = self.se.readlines()
        
        for line in result:
            m = re.match("^Allocated port (.*) for .*", line)
            try:
                self.lsb_url = 'https://www{0}.memoryoftheworld.org'.format(m.groups()[0])
                self.url_label.setText("Go to: {0}".format(self.lsb_url))

            except:
                pass
                #self.url_label.setText("processing.{0}".format("." * int(random.random()*10)))
        
        self.se.seek(0)
        self.se.truncate()

    def open_url(self):
        webbrowser.open(str(self.lsb_url))
        if self.lsb_url != "http://www.memoryoftheworld.org":
            self.url_label.setText("Sharing at: {0}".format(self.lsb_url))

    def config(self):
        self.do_user_config(parent=self)
        self.label.setText(prefs['hello_world_msg'])
