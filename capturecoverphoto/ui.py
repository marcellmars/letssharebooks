from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import urllib
import webbrowser

try:
    from PyQt4.Qt import (QWidgetAction,
                          pyqtSignal,
                          QObject,
                          QToolButton,
                          QMenu,
                          Qt)
    QT_RUNNING = 4
except ImportError:
    from PyQt5.Qt import (QWidgetAction,
                          pyqtSignal,
                          QObject,
                          QToolButton,
                          QMenu,
                          Qt)
    QT_RUNNING = 5

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.capturecover.common_utils import (set_plugin_icon_resources,
                                                       get_icon,
                                                       create_menu_action_unique)
from calibre_plugins.capturecover.config import prefs
from calibre.gui2 import error_dialog

__license__   = 'GPL v3'
__copyright__ = '2014, Marcell Mars'
__docformat__ = 'restructuredtext en'

if False:
    get_icons = get_resources = None

#-----------------------------------------------------------------------------
#- logging -------------------------------------------------------------------
#from calibre_plugins.capturecover.my_logger import get_logger
#logger = get_logger('capturecover', disabled=True)


PLUGIN_ICONS = ['images/camera.png', 'images/camera_working.png']
PORTABLE_RESOURCES = [
    'portable/capturecover.html',
    'portable/capturecover.png']


class UnitedStates(QObject):
    library_changed = pyqtSignal()

    def __init__(self):
        QObject.__init__(self)
        self.initial = True


class CapturePhotoCoverUI(InterfaceAction):

    name = "Set cover for the book"
    action_spec = ('Cover photo',
                   'images/camera.png',
                   'Capture photo and make the cover for the book',
                   'Ctrl+Shift+F5')

    def genesis(self):
        icon_resources = self.load_resources(PLUGIN_ICONS)
        set_plugin_icon_resources(self.name, icon_resources)

        self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]))
        self.old_actions_unique_map = {}

        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config

        self.menu = QMenu(self.gui)
        self.qaction.setMenu(self.menu)
        #self.qaction.triggered.connect(self.capture_cover)

    def initialization_complete(self):
        self.rebuild_menus()

    def rebuild_menus(self):
        m = self.menu
        m.clear()
        self.actions_unique_map = {}
        self.add_item = create_menu_action_unique(self,
                                                  m,
                                                  _('Capture cover!'),
                                                  None,
                                                  shortcut=False,
                                                  triggered=self.capture_cover)
        self.add_item = create_menu_action_unique(self,
                                                  m,
                                                  _('Open preview page'),
                                                  None,
                                                  shortcut=False,
                                                  triggered=self.open_preview)

        m.addSeparator()
        self.add_item = create_menu_action_unique(self,
                                                  m,
                                                  _('Settings'),
                                                  None,
                                                  shortcut=False,
                                                  triggered=self.show_configuration)
       
        for menu_id, unique_name in self.old_actions_unique_map.iteritems():
            if menu_id not in self.actions_unique_map:
                self.gui.keyboard.unregister_shortcut(unique_name)
        self.old_actions_unique_map = self.actions_unique_map
        self.gui.keyboard.finalize()
        
        from calibre.gui2 import gprefs
        
        if self.name not in gprefs['action-layout-context-menu']:
            gprefs['action-layout-context-menu'] += (self.name, )
        if self.name not in gprefs['action-layout-toolbar']:
            gprefs['action-layout-toolbar'] += (self.name, )

        for x in (self.gui.preferences_action, self.qaction):
            x.triggered.connect(self.capture_cover)

    def create_menu_item_ex(self, parent_menu, menu_text,
                            image=None, tooltip=None, shortcut=None,
                            triggered=None, is_checked=None,
                            shortcut_name=None, unique_name=None):
        ac = create_menu_action_unique(self,
                                       parent_menu, menu_text, image, tooltip,
                                       shortcut, triggered, is_checked,
                                       shortcut_name, unique_name)
        self.actions_unique_map[ac.calibre_shortcut_unique_name] = ac.calibre_shortcut_unique_name
        return ac
    
    def show_configuration(self):
        self.interface_action_base_plugin.do_user_config(self.gui)
        self.rebuild_menus()
    
    def capture_cover(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui,
                                'Cannot update metadata',
                                'No books selected',
                                show=True)
        
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        local_cover = '/tmp/kvr.jpg'
        self.qaction.setIcon(get_icon('images/camera.png'))
        urllib.urlretrieve("{0}/capture".format(prefs['gphoto2_server'],
                           local_cover))
        self.qaction.setIcon(get_icon('images/camera_working.png'))
        for book_id in ids:
            from calibre.gui2.ui import get_gui
            get_gui().current_db.new_api.set_cover({book_id: open(local_cover)})
        
        get_gui().db_images.reset()
        get_gui().tags_view.recount()
            
    def open_preview(self):
        webbrowser.open("{0}/live".format(prefs['gphoto2_server']))
    def apply_settings(self):
        from calibre_plugins.capturecover.config import prefs
        prefs
