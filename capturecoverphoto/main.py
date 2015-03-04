# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

import os

try:
    from PyQt4.Qt import (Qt,
                        QDialog,
                        QHBoxLayout,
                        QSizePolicy,
                        QVBoxLayout,
                        QWidget,
                        QUrl,
                        QWebView)
                        #SIGNAL)
except ImportError:
    from PyQt5.Qt import (Qt,
                        QDialog,
                        QHBoxLayout,
                        QSizePolicy,
                        QVBoxLayout,
                        QWidget,
                        QUrl,
                        QWebView)
                        #SIGNAL)

__license__   = 'GPL v3'
__copyright__ = '2015, Marcell Mars'
__docformat__ = 'restructuredtext en'

if False:
    get_icons = get_resources = None

#-----------------------------------------------------------------------------
#- logging -------------------------------------------------------------------
from calibre_plugins.capturecover.my_logger import get_logger
logger = get_logger('capturecover', disabled=True)


#-----------------------------------------------------------------------------
#- CapturePhotoCover is the main class of plugin ---------------------------------


class CapturePhotoCover(QDialog):
    def __init__(self, gui, icon, do_user_config, qaction, us):
        QDialog.__init__(self, gui)
        self.main_gui = gui
        self.do_user_config = do_user_config
        self.qaction = qaction
        self.us = us

        #- main UI layout -----------------------------------------------------
        self.ll = QVBoxLayout()

        self.l = QHBoxLayout()
        self.l.setSpacing(0)
        #self.l.setMargin(0) # not in Qt5
        self.w = QWidget()
        self.w.setLayout(self.l)

        self.setLayout(self.ll)
        self.setWindowIcon(icon)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        #- webkit -------------------------------------------------------------

        self.webview = QWebView()
        self.webview.setMaximumWidth(680)
        self.webview.setMaximumHeight(320)
        self.webview.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        # self.webview.load(QUrl.fromLocalFile(
        #     os.path.join(self.us.portable_directory,
        #                  "portable/kaliweb.html")))
        self.loadUrl()
        self.webview.page().networkAccessManager().sslErrors.connect(self.sslErrorHandler)
        #self.connect(self.webview.page().networkAccessManager(),
        #             SIGNAL("sslErrors (QNetworkReply *, \
        #                                       const QList<QSslError> &)"),
        #             self.sslErrorHandler)

        logger.info("KALIWEB PATH: {}".format(
                    os.path.join(self.us.portable_directory,
                                 "portable/kaliweb.html")))
        self.ll.addWidget(self.webview)

    def loadUrl(self):
        if self.us.initial:
            self.webview.page().mainFrame().load(QUrl("https://google.com"))
            self.us.initial = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    def sslErrorHandler(self, reply, errorList):
            reply.ignoreSslErrors()
            logger.debug("SSL ERRORS: {}".format(errorList))
            return

    def closeEvent(self, e):
        self.hide()
