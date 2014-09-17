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

prefs = JSONConfig('plugins/letssharebooks.conf')

# Set defaults
prefs.defaults['lsb_server'] = 'memoryoftheworld.org'
prefs.defaults['server_prefix'] = 'https'

try:
    prefs['library_uuid']
except:
    prefs.defaults['library_uuid'] = str(uuid.uuid4())

try:
    prefs.defaults['librarian']
except:
    prefs.defaults['librarian'] = u''


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.l5 = QHBoxLayout()
        self.server_prefix_label = QLabel('Server prefix:')
        self.l5.addWidget(self.server_prefix_label)

        self.server_prefix = QLineEdit(self)
        self.server_prefix.setText(prefs['server_prefix'])
        self.l5.addWidget(self.server_prefix)
        self.server_prefix_label.setBuddy(self.server_prefix)
        self.l.addLayout(self.l5)

        self.ll = QHBoxLayout()
        self.server_label = QLabel('Server:')
        self.ll.addWidget(self.server_label)

        self.lsb_server = QLineEdit(self)
        self.lsb_server.setText(prefs['lsb_server'])
        self.ll.addWidget(self.lsb_server)
        self.server_label.setBuddy(self.lsb_server)
        self.l.addLayout(self.ll)

        self.lll = QHBoxLayout()
        self.librarian_label = QLabel('Librarian:')
        self.lll.addWidget(self.librarian_label)

        self.librarian = QLineEdit(self)
        self.librarian.setText(prefs['librarian'])
        self.lll.addWidget(self.librarian)
        self.librarian_label.setBuddy(self.librarian)
        self.l.addLayout(self.lll)

        self.llll = QHBoxLayout()
        self.library_uuid_label = QLabel('Library ID:')
        self.llll.addWidget(self.library_uuid_label)

        self.library_uuid = QLabel(self)
        self.library_uuid.setText(prefs['library_uuid'])
        self.llll.addWidget(self.library_uuid)
        self.library_uuid_label.setBuddy(self.library_uuid)
        self.l.addLayout(self.llll)

    def save_settings(self):
        prefs['lsb_server'] = unicode(self.lsb_server.text())
        prefs['server_prefix'] = unicode(self.server_prefix.text())
        prefs['librarian'] = unicode(self.librarian.text())
        prefs['library_uuid'] = prefs['library_uuid']
