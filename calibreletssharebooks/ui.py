from __future__ import (unicode_literals, division, absolute_import, print_function)
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.letssharebooks.main import LetsShareBooksDialog
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon
from calibre_plugins.letssharebooks import LetsShareBooks as lsb
from PyQt4.Qt import QWidgetAction, QToolButton, QMenu, QObject
from PyQt4 import QtCore
import urllib2, tempfile, os, sys

__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

if False:

    get_icons = get_resources = None

#- set up logging ------------------------------------------------------------
LOGGER_DISABLED = True
#LOGGER_DISABLED = False

import logging
from logging import handlers

logger = logging.getLogger('letssharebooks.ui')
#logger.setLevel(logging.CRITICAL)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s: %(filename)s >> %(levelname)s - %(message)s')

if sys.platform == "win32":
    logging_handler = handlers.TimedRotatingFileHandler("debug_win.log",
                                                        when='h',
                                                        interval=1,
                                                        backupCount=1)
else:
    logging_handler = handlers.TimedRotatingFileHandler("debug.log",
                                                        when='h',
                                                        interval=1,
                                                        backupCount=1)

logging_handler.setFormatter(formatter)
logger.addHandler(logging_handler)

logger.disabled = LOGGER_DISABLED
logger.debug("LOGGING ON")

#-----------------------------------------------------------------------------


PLUGIN_ICONS = ['images/icon.png', 'images/icon_connected.png']
PORTABLE_RESOURCES = [
'portable/jquery-1.10.2.min.js',
'portable/jquery.ba-bbq.min.js',
'portable/jquery.mockjax.js',
'portable/jquery-ui-1.10.3.custom.min.css',
'portable/jquery-ui-1.10.3.custom.min.js',
'portable/json2.js',
'portable/libraries.js',
'portable/BROWSE_LIBRARY.html',
'portable/portable.js',
'portable/portable_win.js',
'portable/style.css',
'portable/underscore-min.js']

class UnitedStates(QObject):
    library_changed = QtCore.pyqtSignal()
    def __init__(self):
        QObject.__init__(self)
        self.portable_directory = tempfile.mkdtemp()
        self.plugin_url = "https://github.com/marcellmars/letssharebooks/raw/master/calibreletssharebooks/letssharebooks_calibre.zip"
        self.running_version = ".".join(map(str, lsb.version))
        try:
            self.latest_version = urllib2.urlopen('https://raw.github.com/marcellmars/letssharebooks/master/calibreletssharebooks/_version').read()[:-1].encode("utf-8")
        except:
            self.latest_version = "0.0.0"

    def library_changed_emit(self):
        self.library_changed.emit()

class LetsShareBooksUI(InterfaceAction):

    name = "Let's share books"
    action_spec = ("Let's share books", None, 'Share your library at http://www.memoryoftheworld.org', None)
    action_add_menu = True

    def genesis(self):
        icon_resources = self.load_resources(PLUGIN_ICONS)
        set_plugin_icon_resources(self.name, icon_resources)

        self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]))
        self.old_actions_unique_map = {}
        self.us = UnitedStates()

        res = self.load_resources(PORTABLE_RESOURCES)
        os.makedirs(os.path.join(self.us.portable_directory, 'portable'))
        for resource in res.keys():
            logger.debug("RESOURCE KEY: {}".format(resource))
            if sys.platform == "win32" and resource == "portable/portable_win.js":
                logger.debug("WIN_RESOURCE KEY: {}".format(resource))
                with open(os.path.join(self.us.portable_directory, 'portable/portable.js'), 'w') as portable:
                    portable.write(res[resource])
            elif sys.platform == "win32" and resource == "portable/portable.js":
                logger.debug("IGNORE PORTABLE.JS ON WINDOWS ({})".format(resource))
            else:
                with open(os.path.join(self.us.portable_directory, resource), 'w') as portable:
                    portable.write(res[resource])

        self.popup_type = QToolButton.InstantPopup
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config

        d = LetsShareBooksDialog(self.gui, self.qaction.icon(), do_user_config, self.qaction, self.us)
        m = QMenu(self.gui)
        self.qaction.setMenu(m)
        a = QWidgetAction(m)
        a.setDefaultWidget(d)
        m.addAction(a)

    def library_changed(self, db):
        self.us.library_changed_emit()
        print("library_change: {}".format(db.library_id))

    def apply_settings(self):
        from calibre_plugins.letssharebooks.config import prefs
        prefs
