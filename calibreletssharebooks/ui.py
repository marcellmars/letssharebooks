from __future__ import (unicode_literals, division, absolute_import, print_function)
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.letssharebooks.main import LetsShareBooksDialog
from calibre_plugins.letssharebooks.common_utils import set_plugin_icon_resources, get_icon, create_menu_action_unique
from calibre_plugins.letssharebooks import LetsShareBooks as lsb

import urllib2

__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

if False:

    get_icons = get_resources = None

PLUGIN_ICONS = ['images/icon.png', 'images/icon_connected.png']

class UnitedStates:
    def __init__(self):
        self.plugin_url = "https://github.com/marcellmars/letssharebooks/raw/master/calibreletssharebooks/letssharebooks_calibre.zip"
        self.running_version = ".".join(map(str, lsb.version))
        try:
            self.latest_version = urllib2.urlopen('https://raw.github.com/marcellmars/letssharebooks/master/calibreletssharebooks/_version').read()[:-1].encode("utf-8")
        except:
            self.latest_version = "0.0.0"
        
        self.window_title = "Let's share books"
        self.share_button_text = "Start sharing"
        self.lsb_url_text = 'Be a librarian. Share your library.'
        self.url_label_tooltip = '<<<< Be a librarian. Click on Start sharing button.<<<<'
        self.button_state = "start"
        self.connecting = False
        self.disconnecting = False
        self.check_finished = True
        self.kill_finished = False
        self.lsb_url = 'nourl'
        self.urllib_result = ""
        self.http_error = None
        self.ssh_proc = None
        self.lost_connection = False
        self.debug_item = None
        self.debug_counter = 1
        self.connecting_now = None
        self.found_url = None
        self.counter = 0
        self.port = 0

class LetsShareBooksUI(InterfaceAction):

    name = "Let's share books"
    action_spec = ("Let's share books", None, 'Share your library at http://www.memoryoftheworld.org', None)

    def genesis(self):
        icon_resources = self.load_resources(PLUGIN_ICONS)
        set_plugin_icon_resources(self.name, icon_resources)
        #icon = get_icons(['images/icon.png', 'images/icon_c.png')

        self.qaction.setIcon(get_icon(PLUGIN_ICONS[0]))
        #self.menu = QMenu(self.gui)
        self.old_actions_unique_map = {}
        #self.qaction.setMenu(self.menu)
        self.us = UnitedStates()
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = LetsShareBooksDialog(self.gui, self.qaction.icon(), do_user_config, self.qaction, self.us)
        d.show()

    def apply_settings(self):
        from calibre_plugins.letssharebooks.config import prefs
        prefs
