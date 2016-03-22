from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2013, Marcell Mars <ki.ber@kom.uni.st>'
__docformat__ = 'restructuredtext en'

# The class that all Interface Action plugin wrappers must inherit from
from calibre.customize import InterfaceActionBase


class LetsShareBooks(InterfaceActionBase):
    name                = "[let's share books]"
    description         = 'Share your Calibre library at http://www.memoryoftheworld.org'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Marcell Mars'
    version             = (4, 0, 6)
    minimum_calibre_version = (0, 9, 30)
    actual_plugin       = 'calibre_plugins.letssharebooks.ui:LetsShareBooksUI'

    def is_customizable(self):
        return True

    def config_widget(self):
        # It is important to put this import statement here rather than at the
        # top of the module as importing the config class will also cause the
        # GUI libraries to be loaded, which we do not want when using calibre
        # from the command line
        from calibre_plugins.letssharebooks.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()

        # Apply the changes
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
