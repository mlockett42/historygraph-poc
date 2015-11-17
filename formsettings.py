#Display a settings dialog

from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *

class FormSettings(QDialog):
    def __init__(self, parent = None):
        super(FormSettings, self).__init__(parent)

        hbox = QHBoxLayout()
        hbox.addStretch(0)

        vboxLeft = QVBoxLayout()
        hbox.addLayout(vboxLeft)

        vboxRight = QVBoxLayout()
        hbox.addLayout(vboxRight)
        
        l = QLabel("Email address")
        vboxLeft.addWidget(l)

        self.teEmailAddress = QTextEdit(GetGlobalSettingStore().LoadSetting("EmailAddress"))
        self.teEmailAddress.setMaximumHeight(27)
        vboxRight.addWidget(self.teEmailAddress)
        
        l = QLabel("POP Server")
        vboxLeft.addWidget(l)

        self.tePOPServerName = QTextEdit(GetGlobalSettingStore().LoadSetting("POPServerName"))
        self.tePOPServerName.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPServerName)
        
        l = QLabel("POP Server Port")
        vboxLeft.addWidget(l)

        self.tePOPServerPort = QTextEdit(GetGlobalSettingStore().LoadSetting("POPServerPort"))
        self.tePOPServerPort.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPServerPort)
        
        l = QLabel("POP User Name")
        vboxLeft.addWidget(l)

        self.tePOPUserName = QTextEdit(GetGlobalSettingStore().LoadSetting("POPUserName"))
        self.tePOPUserName.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPUserName)
        
        l = QLabel("POP Password")
        vboxLeft.addWidget(l)

        self.tePOPPassword = QTextEdit(GetGlobalSettingStore().LoadSetting("POPPassword"))
        self.tePOPPassword.setMaximumHeight(27)
        vboxRight.addWidget(self.tePOPPassword)

        
        l = QLabel("SMTP Server")
        vboxLeft.addWidget(l)

        self.teSMTPServerName = QTextEdit(GetGlobalSettingStore().LoadSetting("SMTPServerName"))
        self.teSMTPServerName.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPServerName)
        
        l = QLabel("SMTP Server Port")
        vboxLeft.addWidget(l)

        self.teSMTPServerPort = QTextEdit(GetGlobalSettingStore().LoadSetting("SMTPServerPort"))
        self.teSMTPServerPort.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPServerPort)
        
        l = QLabel("SMTP User Name")
        vboxLeft.addWidget(l)

        self.teSMTPUserName = QTextEdit(GetGlobalSettingStore().LoadSetting("SMTPUserName"))
        self.teSMTPUserName.setMaximumHeight(27)
        vboxRight.addWidget(self.teSMTPUserName)
        
        l = QLabel("SMTP Password")
        vboxLeft.addWidget(l)

        self.teSMTPPassword = QTextEdit(GetGlobalSettingStore().LoadSetting("SMTPPassword"))
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
        GetGlobalSettingStore().SaveSetting("POPServerPort", self.tePOPServerPort.toPlainText())
        GetGlobalSettingStore().SaveSetting("POPServerName", self.tePOPServerName.toPlainText())
        GetGlobalSettingStore().SaveSetting("POPUserName", self.tePOPUserName.toPlainText())
        GetGlobalSettingStore().SaveSetting("POPPassword", self.tePOPPassword.toPlainText())
        GetGlobalSettingStore().SaveSetting("SMTPServerName", self.teSMTPServerName.toPlainText())
        GetGlobalSettingStore().SaveSetting("SMTPServerPort", self.teSMTPServerPort.toPlainText())
        GetGlobalSettingStore().SaveSetting("SMTPUserName", self.teSMTPUserName.toPlainText())
        GetGlobalSettingStore().SaveSetting("SMTPPassword", self.teSMTPPassword.toPlainText())
        GetGlobalSettingStore().SaveSetting("EmailAddress", self.teEmailAddress.toPlainText())
        self.close()

        
        
