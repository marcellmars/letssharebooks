from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import urllib2
import tempfile
import os
import shutil
import datetime

try:
    from PyQt4.Qt import (QWidgetAction,
                          QToolButton,
                          QMenu,
                          QObject,
                          pyqtSignal)
except ImportError:
    from PyQt5.Qt import (QWidgetAction,
                          QToolButton,
                          QMenu,
                          QObject,
                          pyqtSignal)

from calibre_plugins.letssharebooks.config import prefs
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.letssharebooks.main import LetsShareBooksDialog
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon
from calibre_plugins.letssharebooks import LetsShareBooks as lsb

__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

if False:
    get_icons = get_resources = None

#- set up logging ------------------------------------------------------------
# logger = MyLogger(file_name="/tmp/letssharebooks_ui.log",
#                   enabled=False)
#-----------------------------------------------------------------------------


PLUGIN_ICONS = ['images/icon.png', 'images/icon_connected.png']
PORTABLE_RESOURCES = [
    # html
    'portable/BROWSE_LIBRARY.html',
    'portable/favicon.html',
    # js
    'portable/jquery-1.10.2.min.js',
    'portable/jquery.ba-bbq.min.js',
    'portable/jquery-migrate-1.2.1.js',
    'portable/underscore-min.js',
    'portable/bootstrap/js/bootstrap.min.js',
    'portable/typeahead.bundle.min.js',
    'portable/hammer.min.js',
    'portable/portable.js',
    'portable/common.js',
    'portable/libraries.js',
    'portable/json2.js',
    'portable/local_calibre.js',
    # css
    'portable/bootstrap/css/bootstrap.min.css',
    'portable/style.css',
    'portable/favicon.css',
    # images
    'portable/favicon.svg',
    'portable/motw.ico',
    'portable/lodestone.png',
    'portable/lodestone_modal.png',
    # fonts
    'portable/bootstrap/fonts/glyphicons-halflings-regular.eot',
    'portable/bootstrap/fonts/glyphicons-halflings-regular.svg',
    'portable/bootstrap/fonts/glyphicons-halflings-regular.ttf',
    'portable/bootstrap/fonts/glyphicons-halflings-regular.woff',
    'portable/bootstrap/fonts/glyphicons-halflings-regular.woff2',
    # other
    # 'portable/ca-bundle.crt',
    'portable/lsbtunnel.exe',
]


class UnitedStates(QObject):
    library_changed = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.edit_stamp = datetime.datetime(2013, 1, 11, 0, 0, 0, 0)
        self.portable_directory = tempfile.mkdtemp()
        # self.portable_directory = "windows_logs"
        self.plugin_url = ('https://github.com/marcellmars/'
                           'letssharebooks/raw/master/calibreletssharebooks/'
                           'letssharebooks_calibre.zip')
        self.running_version = ".".join(map(str, lsb.version))
        try:
            self.latest_version = urllib2.urlopen(
                'https://raw.github.com/marcellmars/letssharebooks/master/'
                'calibreletssharebooks/_version').read()[:-1].encode("utf-8")
        except:
            self.latest_version = "0.0.0"

    def library_changed_emit(self):
        self.library_changed.emit()


class LetsShareBooksUI(InterfaceAction):

    name = "[let's share books]"
    action_spec = ("[let's share books]",
                   'images/icon.png',
                   'Share your library at https://library.{}'
                   .format(prefs['lsb_server']),
                   None)
    action_add_menu = True

    def genesis(self):
        icon_resources = self.load_resources(PLUGIN_ICONS)
        set_plugin_icon_resources(self.name, icon_resources)

        self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]))
        self.old_actions_unique_map = {}
        self.us = UnitedStates()

        res = self.load_resources(PORTABLE_RESOURCES)

        os.makedirs(os.path.join(self.us.portable_directory,
                                 'portable'))
        os.makedirs(os.path.join(self.us.portable_directory,
                                 'portable/bootstrap'))
        os.makedirs(os.path.join(self.us.portable_directory,
                                 'portable/bootstrap/css'))
        os.makedirs(os.path.join(self.us.portable_directory,
                                 'portable/bootstrap/js'))
        os.makedirs(os.path.join(self.us.portable_directory,
                                 'portable/bootstrap/fonts'))

        for resource in res.keys():
            if resource == "portable/libraries.js":
                lib_lines = res[resource].split(os.linesep)
                lib_lines.insert(4, "var PORTABLE = true;{}".format(os.linesep))
                with open(os.path.join(self.us.portable_directory,
                                       'portable/libraries.js'), "w") as lib:
                    lib.writelines(os.linesep.join(lib_lines))
            else:
                with open(os.path.join(self.us.portable_directory,
                                       resource), 'wb') as portable:
                    portable.write(res[resource])

        self.popup_type = QToolButton.InstantPopup
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config

        self.d = LetsShareBooksDialog(self.gui,
                                      self.qaction.icon(),
                                      do_user_config,
                                      self.qaction, self.us)
        m = QMenu(self.gui)
        self.qaction.setMenu(m)
        a = QWidgetAction(m)
        a.setDefaultWidget(self.d)
        m.addAction(a)

    def library_changed(self, db):
        self.us.library_changed_emit()
        print("library_change: {}".format(db.library_id))

    def apply_settings(self):
        # logger.info("PREFS: {}".format(prefs))
        prefs

    def shutting_down(self):
        #logger.info("SHUTTING_DOWN... {}".format(self.us.portable_directory))
        if self.disconnect_all():
            shutil.rmtree(os.path.join(self.us.portable_directory))
            #logger.info("DISCONNECT_ALL SUCCEEDED!")
            return True
        else:
            #logger.info("DISCONNECT_ALL FAILED!")
            return False
