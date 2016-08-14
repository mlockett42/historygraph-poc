#Display a settings dialog

from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *

class FormSettings(QDialog):
    def __init__(self, demux, parent = None):
        super(FormSettings, self).__init__(parent)

        self.demux = demux

        hbox = QHBoxLayout()
        hbox.addStretch(0)

        vboxLeft = QVBoxLayout()
        hbox.addLayout(vboxLeft)

        vboxRight = QVBoxLayout()
        hbox.addLayout(vboxRight)
        
        l = QLabel("Email address")
        vboxLeft.addWidget(l)

        self.teEmailAddress = QTextEdit(self.demux.settingsstore.LoadSetting("EmailAddress"))
        self.teEmailAddress.setMaximumHeight(27)
        vboxRight.addWidget(self.teEmailAddress)
        
        l = QLabel("POP Server")
        vboxLeft.addWidget(l)

        self.tePOPServerName = QTextEdit(self.demux.settingsstore.LoadSetting("POPServerName"))
        self.tePOPServerName.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPServerName)
        
        l = QLabel("POP Server Port")
        vboxLeft.addWidget(l)

        self.tePOPServerPort = QTextEdit(self.demux.settingsstore.LoadSetting("POPServerPort"))
        self.tePOPServerPort.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPServerPort)
        
        l = QLabel("POP User Name")
        vboxLeft.addWidget(l)

        self.tePOPUserName = QTextEdit(self.demux.settingsstore.LoadSetting("POPUserName"))
        self.tePOPUserName.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPUserName)
        
        l = QLabel("POP Password")
        vboxLeft.addWidget(l)

        self.tePOPPassword = QTextEdit(self.demux.settingsstore.LoadSetting("POPPassword"))
        self.tePOPPassword.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPPassword)

        
        l = QLabel("SMTP Server")
        vboxLeft.addWidget(l)

        self.teSMTPServerName = QTextEdit(self.demux.settingsstore.LoadSetting("SMTPServerName"))
        self.teSMTPServerName.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPServerName)
        
        l = QLabel("SMTP Server Port")
        vboxLeft.addWidget(l)

        self.teSMTPServerPort = QTextEdit(self.demux.settingsstore.LoadSetting("SMTPServerPort"))
        self.teSMTPServerPort.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPServerPort)
        
        l = QLabel("SMTP User Name")
        vboxLeft.addWidget(l)

        self.teSMTPUserName = QTextEdit(self.demux.settingsstore.LoadSetting("SMTPUserName"))
        self.teSMTPUserName.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPUserName)
        
        l = QLabel("SMTP Password")
        vboxLeft.addWidget(l)

        self.teSMTPPassword = QTextEdit(self.demux.settingsstore.LoadSetting("SMTPPassword"))
        self.teSMTPPassword.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPPassword)

        bnOK = QPushButton("OK")
        vboxLeft.addWidget(bnOK)

        bnCancel = QPushButton("Cancel")
        vboxRight.addWidget(bnCancel)

        bnCancel.clicked.connect(self.close)

        bnOK.clicked.connect(self.OK)

        self.setLayout(hbox)


    def OK(self):
        self.demux.settingsstore.SaveSetting("POPServerPort", self.tePOPServerPort.toPlainText())
        self.demux.settingsstore.SaveSetting("POPServerName", self.tePOPServerName.toPlainText())
        self.demux.settingsstore.SaveSetting("POPUserName", self.tePOPUserName.toPlainText())
        self.demux.settingsstore.SaveSetting("POPPassword", self.tePOPPassword.toPlainText())
        self.demux.settingsstore.SaveSetting("SMTPServerName", self.teSMTPServerName.toPlainText())
        self.demux.settingsstore.SaveSetting("SMTPServerPort", self.teSMTPServerPort.toPlainText())
        self.demux.settingsstore.SaveSetting("SMTPUserName", self.teSMTPUserName.toPlainText())
        self.demux.settingsstore.SaveSetting("SMTPPassword", self.teSMTPPassword.toPlainText())
        self.demux.settingsstore.SaveSetting("EmailAddress", self.teEmailAddress.toPlainText())
        self.close()

        
        
