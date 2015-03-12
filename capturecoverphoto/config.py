from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import uuid

__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

try:
    from PyQt4.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout
except ImportError:
    from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/interface_demo) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file

prefs = JSONConfig('plugins/capturecover.conf')

# Set defaults
prefs.defaults['gphoto2_server'] = 'http://192.168.109:7711'


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.ll = QHBoxLayout()
        self.server_label = QLabel('Gphoto2 server address:')
        self.ll.addWidget(self.server_label)

        self.gphoto2_server = QLineEdit(self)
        self.gphoto2_server.setText(prefs['gphoto2_server'])
        self.ll.addWidget(self.gphoto2_server)
        self.server_label.setBuddy(self.gphoto2_server)
        self.l.addLayout(self.ll)
        
    def save_settings(self):
        prefs['gphoto2_server'] = prefs['gphoto2_server']
