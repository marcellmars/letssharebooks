from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import tempfile
import os
import shutil
import urllib

try:
    from PyQt4.Qt import (QWidgetAction, pyqtSignal, QObject, QToolButton, QMenu)
except ImportError:
    from PyQt5.Qt import (QWidgetAction, pyqtSignal, QObject, QToolButton, QMenu)

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.capturecover.main import CapturePhotoCover
from calibre_plugins.capturecover.common_utils import (set_plugin_icon_resources,
                                                  get_icon)


__license__   = 'GPL v3'
__copyright__ = '2014, Marcell Mars'
__docformat__ = 'restructuredtext en'

if False:

    get_icons = get_resources = None

#-----------------------------------------------------------------------------
#- logging -------------------------------------------------------------------
from calibre_plugins.capturecover.my_logger import get_logger
logger = get_logger('capturecover', disabled=True)


PLUGIN_ICONS = ['images/icon.png', 'images/icon_connected.png']
PORTABLE_RESOURCES = [
    'portable/capturecover.html',
    'portable/capturecover.png']


class UnitedStates(QObject):
    library_changed = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.portable_directory = tempfile.mkdtemp()
        self.initial = True

    def library_changed_emit(self):
        self.library_changed.emit()


class CapturePhotoCoverUI(InterfaceAction):

    name = "Set cover for the book"
    action_spec = ("Capture photo and make the cover for the book",
                   'images/icon.png',
                   'Cover photo',
                   'Ctrl+Shift+F5')
    #action_add_menu = True
    #dont_remove_from = frozenset(['toolbar', 'toolbar-device'])

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
            with open(os.path.join(self.us.portable_directory,
                                   resource), 'wb') as portable:
                portable.write(res[resource])

        self.popup_type = QToolButton.InstantPopup

        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config

        self.qaction.triggered.connect(self.capture_cover)

    def capture_cover(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata',
                             'No books selected', show=True)
        
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        urllib.urlretrieve("http://localhost:7711/capture", "/tmp/kvr.jpg")
        
        for book_id in ids:
            from calibre.gui2.ui import get_gui
            get_gui().current_db.new_api.set_cover({book_id:open("/tmp/kvr.jpg")})
            get_gui().library_view.model().books_added(1)
            #mi.set_cover(d)
        
    def library_changed(self, db):
        self.us.library_changed_emit()
        print("library_change: {}".format(db.library_id))

    def apply_settings(self):
        from calibre_plugins.kaliweb.config import prefs
        prefs

    def shutting_down(self):
        logger.info("SHUTTING_DOWN... {}".format(self.us.portable_directory))
        if self.d.disconnect_all():
            shutil.rmtree(os.path.join(self.us.portable_directory))
            logger.info("DISCONNECT_ALL SUCCEEDED!")
            return True
        else:
            logger.info("DISCONNECT_ALL FAILED!")
            return False
