from __future__ import (unicode_literals, division, absolute_import, print_function)
from PyQt4.Qt import QLabel, QDialog, QHBoxLayout, QPushButton, QTimer, QIcon, QPixmap, QApplication, QSizePolicy, QVBoxLayout, QWidget, QThread, QListWidget, QLineEdit
from PyQt4 import QtCore
from calibre.gui2.ui import get_gui as calibre_main
from calibre_plugins.letssharebooks.common_utils import get_icon
from calibre_plugins.letssharebooks.config import prefs
from calibre_plugins.letssharebooks import requests
from calibre.library.server import server_config
import os, sys, subprocess, re, random, urllib2, zipfile, json, tempfile

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
        open("/tmp/.userknownhostsfile", "w").write(urllib2.urlopen('https://chat.memoryoftheworld.org/.userknownhostsfile').read())
    except:
        pass
if False:
    get_icons = get_resources = None


class LetsShareBooksDialog(QDialog):
    started_calibre_web_server = QtCore.pyqtSignal()
    established_ssh_tunnel = QtCore.pyqtSignal()
    lost_calibre_web_server = QtCore.pyqtSignal()
    lost_ssh_connection = QtCore.pyqtSignal()

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

        self.edit = QLineEdit()
        self.edit.textChanged.connect(self.handleTextChanged)
        self.ll.addWidget(self.edit)

        self.debug_label = QLabel()
        self.ll.addWidget(self.debug_label)

        self.lets_share_button = QPushButton()
        self.lets_share_button.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.lets_share_button.setObjectName("share")
        #self.lets_share_button.clicked.connect(self.lets_share)

        self.l.addWidget(self.lets_share_button)

        self.url_label = QPushButton()
        self.url_label.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.url_label.setObjectName("url")
        #self.url_label.clicked.connect(self.open_url)
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
        #self.chat_button.clicked.connect(functools.partial(self.open_url2, "https://chat.memoryoftheworld.org"))
        self.ll.addWidget(self.chat_button)

        self.about_project_button = QPushButton('Public Library: http://www.memoryoftheworld.org')
        self.about_project_button.setObjectName("url2")
        self.about_project_button.setToolTip('When everyone is librarian, library is everywhere.')
        #self.about_project_button.clicked.connect(functools.partial(self.open_url2, "http://www.memoryoftheworld.org"))
        self.ll.addWidget(self.about_project_button)

        self.debug_log = QListWidget()
        self.ll.addWidget(self.debug_log)
        self.debug_log.addItem("Initiatied!")
        self.debug_log.hide()

        self.sql_db = self.gui.current_db
        #self.metadata_thread = MetadataLibThread(self.debug_log, self.sql_db, self.us)

        self.metadata_button = QPushButton("Get library metadata!")
        self.metadata_button.setObjectName("url2")
        self.metadata_button.setToolTip('Get library metadata!')
        #self.metadata_button.clicked.connect(self.get_metadata)
        self.ll.addWidget(self.metadata_button)
        self.metadata_button.show()

        self.upgrade_button = QPushButton('Please download and upgrade from {0} to {1} version of plugin.'.format(self.us.running_version, self.us.latest_version))
        self.upgrade_button.setObjectName("url2")
        self.upgrade_button.setToolTip('Running latest version you make developers happy')
        #self.upgrade_button.clicked.connect(functools.partial(self.open_url2, self.us.plugin_url))

        version_list = [self.us.running_version, self.us.latest_version]
        version_list.sort(key=lambda s: map(int, s.split('.')))
        if self.us.running_version != self.us.latest_version:
            if self.us.running_version == version_list[0]:
                self.ll.addSpacing(20)
                self.ll.addWidget(self.upgrade_button)

        self.resize(self.sizeHint())

        #- parsing/tee log file -----------------------------------------------------------------------------

        self.se = open("/tmp/lsb.log", "w+b")
        #self.se = tempfile.NamedTemporaryFile()
        self.so = self.se

        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        os.dup2(self.so.fileno(), sys.stdout.fileno())
        os.dup2(self.se.fileno(), sys.stderr.fileno())

        #- state machine -----------------------------------------------------------------------------
        self.debug_label.setText(str(self.us.machine_state))

        self.machine = QtCore.QStateMachine()

        self.on = QtCore.QState()
        self.on.setObjectName("on")
        self.on.entered.connect(lambda: self.render("Start sharing", self.us.lsb_url_text))

        self.calibre_web_server = QtCore.QState()
        self.calibre_web_server.setObjectName("calibre_web_server")
        self.calibre_web_server.entered.connect(self.start_calibre_server)
        self.calibre_web_server.entered.connect(lambda: self.render("Stop sharing", self.us.lsb_url_text))
        self.calibre_web_server.assignProperty(self.debug_label, 'text', 'Starting Calibre web server...')

        self.ssh_server = QtCore.QState()
        self.ssh_server.setObjectName("ssh_server")
        self.ssh_server.entered.connect(lambda: self.render("Stop sharing", self.us.lsb_url_text))
        self.ssh_server.entered.connect(self.establish_ssh_server)
        self.ssh_server.assignProperty(self.url_label, 'text', 'Connecting...')
        self.ssh_server.assignProperty(self.debug_label, 'text', 'Establishing SSH tunnel...')

        self.ssh_server_established = QtCore.QState()
        self.ssh_server_established.setObjectName("ssh_server_established")
        self.ssh_server_established.entered.connect(lambda: self.render("Stop sharing", self.us.lsb_url_text))
        self.ssh_server_established.assignProperty(self.debug_label, 'text', 'Established SSH tunnel...')

        self.off = QtCore.QState()
        self.off.setObjectName("off")
        self.off.entered.connect(lambda: self.render("Stop sharing", 'Be a librarian. Share your library.'
))
        self.off.assignProperty(self.debug_label, 'text', 'Start again...')

        self.on.addTransition(self.lets_share_button.clicked, self.calibre_web_server)

        self.calibre_web_server.addTransition(self.lets_share_button.clicked, self.off)
        self.calibre_web_server.addTransition(self.started_calibre_web_server, self.ssh_server)

        self.ssh_server.addTransition(self.lets_share_button.clicked, self.off)
        self.ssh_server.addTransition(self.lost_calibre_web_server, self.off)
        self.ssh_server.addTransition(self.established_ssh_tunnel, self.ssh_server_established)

        self.ssh_server_established.addTransition(self.lets_share_button.clicked, self.off)
        self.ssh_server_established.addTransition(self.lost_calibre_web_server, self.off)
        self.ssh_server_established.addTransition(self.lost_ssh_connection, self.off)

        self.off.addTransition(self.on)

        self.machine.addState(self.on)
        self.machine.addState(self.calibre_web_server)
        self.machine.addState(self.ssh_server)
        self.machine.addState(self.ssh_server_established)
        self.machine.addState(self.off)

        if isinstance(self.us.machine_state, int):
            self.machine.setInitialState(self.on)
        else:
            print("self.{}".format(self.us.machine_state))
            self.machine.setInitialState(eval("self.{}".format(self.us.machine_state)))

        self.machine.start()

        #------------------------------------------------------------------------------

    def render(self, button_label, lsb_url_text):
        if lsb_url_text == 'Be a librarian. Share your library.':
            self.us.lsb_url_text = lsb_url_text
        self.lets_share_button.setText(button_label)
        self.url_label.setText(lsb_url_text)

    def establish_ssh_server(self):
        if sys.platform == "win32":
            self.win_reg = subprocess.Popen("regedit /s .hosts.reg")
            self.us.port = str(int(random.random()*40000+10000))
            self.us.ssh_proc = subprocess.Popen("lsbtunnel.exe -N -T tunnel@{2} -R {0}:localhost:{1} -P 722".format(self.us.port, self.calibre_server_port, prefs['lsb_server']), shell=True)
            self.us.lsb_url = "https://www{0}.{1}".format(self.us.port, prefs['lsb_server'])
            self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
            self.us.found_url = True
        else:
            #self.us.ssh_proc = subprocess.Popen(['ssh', '-T', '-N', '-g', '-o', 'UserKnownHostsFile=/tmp/.userknownhostsfile', '-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveINterval=60', prefs['lsb_server'], '-l', 'tunnel', '-R', '0:localhost:{0}'.format(self.calibre_server_port), '-p', '722'])
            self.us.ssh_proc = subprocess.Popen(['ssh', '-T', '-N', '-g', '-o', 'TCPKeepAlive=yes', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no','-o', 'ServerAliveINterval=60', prefs['lsb_server'], '-l', 'tunnel', '-R', '0:localhost:{0}'.format(self.calibre_server_port), '-p', '722'])
            if self.us.ssh_proc:
                def parse_log():
                    try:
                        self.se.seek(0)
                        result = self.se.readlines()

                        for line in result:
                            m = re.match("^Allocated port (.*) for .*", line)
                            try:
                                self.us.port = m.groups()[0]
                                #self.us.lsb_url = 'https://www{0}.{1}'.format(self.us.port, prefs['lsb_server'])
                                self.us.lsb_url = 'http://www{0}.{1}'.format(m.groups()[0], prefs['lsb_server'])
                                self.us.lsb_url_text = "Go to: {0}".format(self.us.lsb_url)
                                self.us.url_label_tooltip = 'Copy URL to clipboard and check it out in a browser!'
                                self.established_ssh_tunnel.emit()
                            except:
                                pass
                    finally:
                        QTimer.singleShot(300, parse_log)
                parse_log()

        self.qaction.setIcon(get_icon('images/icon_connected.png'))


    def start_calibre_server(self):
        self.main_gui.start_content_server()
        opts, args = server_config().option_parser().parse_args(['calibre-server'])
        self.calibre_server_port = opts.port
        self.started_calibre_web_server.emit()

    def closeEvent(self, e):
        for state in self.machine.configuration():
            self.us.machine_state = state.objectName()
        self.hide()

    def config(self):
        self.do_user_config(parent=self)
        self.label.setText(prefs['lsb_server'])

    def handleTextChanged(self, text):
        if text == 'calibre':
            self.started_calibre_web_server.emit()
        if text == 'ssh':
            self.established_ssh_tunnel.emit()
        if text == 'lost_calibre':
            self.lost_calibre_web_server.emit()
        if text == 'lost_ssh':
            self.lost_ssh_connection.emit()


