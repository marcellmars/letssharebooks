from PyQt4 import QtCore, QtGui
import sys

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

        self.machine = QtCore.QStateMachine()

        self.on = QtCore.QState()
        self.on.assignProperty(self.button, 'text', 'Start')

        self.calibreWebServer = QtCore.QState()
        self.calibreWebServer.setObjectName("calibreWebServer")
        self.calibreWebServer.entered.connect(self.trigger)
        self.calibreWebServer.assignProperty(self.button, 'text', 'Stop')
        self.calibreWebServer.assignProperty(self.label, 'text', 'Starting Calibre web server...')

        self.ssh = QtCore.QState()
        self.sshServer = QtCore.QState(self.ssh)
        self.sshServer.assignProperty(self.label, 'text', 'Establishing SSH tunnel...')
        self.ssh.setInitialState(self.sshServer)

        self.sshServerEstablished = QtCore.QState(self.ssh)
        self.sshServerEstablished.assignProperty(self.label, 'text', 'Established SSH tunnel...')

        self.off = QtCore.QState()
        self.off.assignProperty(self.label, 'text', 'Start again...')

        self.on.addTransition(self.button.clicked, self.calibreWebServer)
        self.calibreWebServer.addTransition(self.button.clicked, self.off)
        self.calibreWebServer.addTransition(self.startedCalibreWebServer, self.sshServer)
        self.ssh.addTransition(self.button.clicked, self.off)
        self.ssh.addTransition(self.lostCalibreWebServer, self.off)
        self.sshServer.addTransition(self.establishedSSHTunnel, self.sshServerEstablished)
        self.sshServerEstablished.addTransition(self.lostRemoteWebServer, self.off)

        self.off.addTransition(self.on)

        self.machine.addState(self.on)
        self.machine.addState(self.calibreWebServer)
        self.machine.addState(self.ssh)
        self.machine.addState(self.off)

        self.machine.setInitialState(self.on)

        self.machine.start()

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

app = QtGui.QApplication(sys.argv)
window = Window()
window.show()
app.exec_()
