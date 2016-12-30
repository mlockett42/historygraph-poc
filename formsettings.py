#Display a settings dialog

from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *

class FormSettings(QDialog):
    def __init__(self, parent, demux):
        super(FormSettings, self).__init__(parent)

        self.demux = demux

        self.setWindowTitle("Settings " + self.demux.myemail)

        hbox = QHBoxLayout()
        hbox.addStretch(0)

        vboxLeft = QVBoxLayout()
        hbox.addLayout(vboxLeft)

        vboxRight = QVBoxLayout()
        hbox.addLayout(vboxRight)
        
        l = QLabel("Email address")
        vboxLeft.addWidget(l)

        self.teEmailAddress = QTextEdit(self.demux.settingsstore.LoadSetting("myemail"))
        self.teEmailAddress.setMaximumHeight(27)
        vboxRight.addWidget(self.teEmailAddress)
        
        l = QLabel("POP Server")
        vboxLeft.addWidget(l)

        self.tePOPServerName = QTextEdit(self.demux.settingsstore.LoadSetting("popserver"))
        self.tePOPServerName.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPServerName)
        
        l = QLabel("POP Server Port")
        vboxLeft.addWidget(l)

        self.tePOPServerPort = QTextEdit(self.demux.settingsstore.LoadSetting("popport"))
        self.tePOPServerPort.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPServerPort)
        
        l = QLabel("POP User Name")
        vboxLeft.addWidget(l)

        self.tePOPUserName = QTextEdit(self.demux.settingsstore.LoadSetting("popuser"))
        self.tePOPUserName.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPUserName)
        
        l = QLabel("POP Password")
        vboxLeft.addWidget(l)

        self.tePOPPassword = QTextEdit(self.demux.settingsstore.LoadSetting("poppass"))
        self.tePOPPassword.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPPassword)

        
        l = QLabel("SMTP Server")
        vboxLeft.addWidget(l)

        self.teSMTPServerName = QTextEdit(self.demux.settingsstore.LoadSetting("smtpserver"))
        self.teSMTPServerName.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPServerName)
        
        l = QLabel("SMTP Server Port")
        vboxLeft.addWidget(l)

        self.teSMTPServerPort = QTextEdit(self.demux.settingsstore.LoadSetting("smtpport"))
        self.teSMTPServerPort.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPServerPort)
        
        l = QLabel("SMTP User Name")
        vboxLeft.addWidget(l)

        self.teSMTPUserName = QTextEdit(self.demux.settingsstore.LoadSetting("smtpuser"))
        self.teSMTPUserName.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPUserName)
        
        l = QLabel("SMTP Password")
        vboxLeft.addWidget(l)

        self.teSMTPPassword = QTextEdit(self.demux.settingsstore.LoadSetting("smtppass"))
        self.teSMTPPassword.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPPassword)

        self.bnOK = QPushButton("OK")
        vboxLeft.addWidget(self.bnOK)

        self.bnCancel = QPushButton("Cancel")
        vboxRight.addWidget(self.bnCancel)

        self.bnCancel.clicked.connect(self.close)

        self.bnOK.clicked.connect(self.OK)

        self.setLayout(hbox)


    def OK(self):
        self.demux.settingsstore.SaveSetting("popport", self.tePOPServerPort.toPlainText())
        self.demux.settingsstore.SaveSetting("popserver", self.tePOPServerName.toPlainText())
        self.demux.settingsstore.SaveSetting("popuser", self.tePOPUserName.toPlainText())
        self.demux.settingsstore.SaveSetting("poppass", self.tePOPPassword.toPlainText())
        self.demux.settingsstore.SaveSetting("smtpserver", self.teSMTPServerName.toPlainText())
        self.demux.settingsstore.SaveSetting("smtpport", self.teSMTPServerPort.toPlainText())
        self.demux.settingsstore.SaveSetting("smtpuser", self.teSMTPUserName.toPlainText())
        self.demux.settingsstore.SaveSetting("smtppass", self.teSMTPPassword.toPlainText())
        self.demux.settingsstore.SaveSetting("myemail", self.teEmailAddress.toPlainText())

        self.demux.myemail = self.teEmailAddress.toPlainText()
        self.demux.popport = int(self.tePOPServerPort.toPlainText())
        self.demux.popserver = self.tePOPServerName.toPlainText()
        self.demux.popuser = self.tePOPUserName.toPlainText()
        self.demux.poppass = self.tePOPPassword.toPlainText()
        self.demux.smtpserver = self.teSMTPServerName.toPlainText()
        self.demux.smtpport = int(self.teSMTPServerPort.toPlainText())
        self.demux.smtpuser = self.teSMTPUserName.toPlainText()
        self.demux.smtppass = self.teSMTPPassword.toPlainText()
        self.close()

        
        
