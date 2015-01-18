from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import urllib2
import tempfile
import os
import sys
import shutil

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
#from calibre_plugins.letssharebooks.my_#logger.import get_logger
##logger.= get_#logger.'letssharebooks', disabled=True)

#-----------------------------------------------------------------------------


PLUGIN_ICONS = ['images/icon.png', 'images/icon_connected.png']
PORTABLE_RESOURCES = [
    'portable/jquery-1.10.2.min.js',
    'portable/jquery.ba-bbq.min.js',
    'portable/jquery.mockjax.js',
    'portable/jquery-migrate-1.2.1.js',
    'portable/jquery-ui-1.10.3.custom.min.css',
    'portable/jquery-ui-1.10.3.custom.min.js',
    'portable/json2.js',
    'portable/libraries.js',
    'portable/BROWSE_LIBRARY.html',
    'portable/portable.js',
    'portable/portable_win.js',
    'portable/style.css',
    'portable/underscore-min.js',
    'portable/favicon.html',
    'portable/ca-bundle.crt',
    'portable/lsbtunnel.exe',
    'portable/favicon.svg']


class UnitedStates(QObject):
    library_changed = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.portable_directory = tempfile.mkdtemp()
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
                   'Share your library at https://library.memoryoftheworld.org',
                   None)
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
            #logger.debug("RESOURCE KEY: {}".format(resource))
            if sys.platform == "win32" and resource == "portable/portable_win.js":
                #logger.debug("WIN_RESOURCE KEY: {}".format(resource))
                with open(os.path.join(self.us.portable_directory,
                                       'portable/portable.js'), 'w') as portable:
                    portable.write(res[resource])
            elif sys.platform == "win32" and resource == "portable/portable.js":
                #logger.debug("IGNORE {} ON WINDOWS".format(resource))
                pass
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
        from calibre_plugins.letssharebooks.config import prefs
        prefs

    def shutting_down(self):
        #logger.info("SHUTTING_DOWN... {}".format(self.us.portable_directory))
        if self.d.disconnect_all():
            shutil.rmtree(os.path.join(self.us.portable_directory))
            #logger.info("DISCONNECT_ALL SUCCEEDED!")
            return True
        else:
            #logger.info("DISCONNECT_ALL FAILED!")
            return False
