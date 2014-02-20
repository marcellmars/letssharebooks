from PyQt4 import QtCore, QtGui
import sys

#def debug_trace():
#    '''Set a tracepoint in the Python debugger that works with Qt'''
#    from PyQt4.QtCore import pyqtRemoveInputHook
#    from pdb import set_trace
#    pyqtRemoveInputHook()
#    set_trace()

class UnitedStatesMachine(QtCore.QStateMachine):
    def __init__(self, parent):
        QtCore.QStateMachine.__init__(self)

        self.parent = parent

        self.on = QtCore.QState()
        self.on.assignProperty(parent.button, 'text', 'Start')

        self.calibreWebServer = QtCore.QState()
        self.calibreWebServer.setObjectName("calibreWebServer")
        self.calibreWebServer.entered.connect(parent.trigger)
        self.calibreWebServer.assignProperty(parent.button, 'text', 'Stop')
        self.calibreWebServer.assignProperty(parent.label, 'text', 'Starting Calibre web server...')

        self.ssh = QtCore.QState()
        self.sshServer = QtCore.QState(self.ssh)
        self.sshServer.assignProperty(parent.label, 'text', 'Establishing SSH tunnel...')
        self.ssh.setInitialState(self.sshServer)

        self.sshServerEstablished = QtCore.QState(self.ssh)
        self.sshServerEstablished.assignProperty(parent.label, 'text', 'Established SSH tunnel...')

        self.off = QtCore.QState()
        self.off.assignProperty(parent.label, 'text', 'Start again...')

        self.on.addTransition(parent.button.clicked, self.calibreWebServer)
        self.calibreWebServer.addTransition(parent.button.clicked, self.off)
        self.calibreWebServer.addTransition(parent.startedCalibreWebServer, self.sshServer)
        self.ssh.addTransition(parent.button.clicked, self.off)
        self.ssh.addTransition(parent.lostCalibreWebServer, self.off)
        self.sshServer.addTransition(parent.establishedSSHTunnel, self.sshServerEstablished)
        self.sshServerEstablished.addTransition(parent.lostRemoteWebServer, self.off)

        self.off.addTransition(self.on)

        self.addState(self.on)
        self.addState(self.calibreWebServer)
        self.addState(self.ssh)
        self.addState(self.off)

        self.setInitialState(self.on)
        self.start()

class Window(QtGui.QWidget):
    startedCalibreWebServer = QtCore.pyqtSignal()
    establishedSSHTunnel = QtCore.pyqtSignal()
    lostCalibreWebServer = QtCore.pyqtSignal()
    lostRemoteWebServer = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.edit = QtGui.QLineEdit(self)
        self.edit.textChanged.connect(self.handleTextChanged)

        self.button = QtGui.QPushButton()
        self.label = QtGui.QLabel()
        self.babel = QtGui.QLabel()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        layout.addWidget(self.babel)

        self.machine = UnitedStatesMachine(self)
        #self.machine.start()

    def handleTextChanged(self, text):
        if text == 'calibre':
            self.startedCalibreWebServer.emit()
        if text == 'ssh':
            self.establishedSSHTunnel.emit()
        if text == 'lost_calibre':
            self.lostCalibreWebServer.emit()
        if text == 'lost_ssh':
            self.lostRemoteWebServer.emit()

    def trigger(self):
        self.babel.setText("triggered")
        for c in self.machine.configuration():
            print type(c)
            print c.objectName()
        self.startedCalibreWebServer.emit()

#debug_trace()
app = QtGui.QApplication(sys.argv)
window = Window()
window.show()
app.exec_()
