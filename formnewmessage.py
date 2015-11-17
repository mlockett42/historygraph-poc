#Form to send a new message
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
from email.mime.text import MIMEText
import smtplib
import datetime

class FormNewMessage(QDialog):
    def __init__(self, parent = None):
        super(FormNewMessage, self).__init__(parent)
        self.setWindowTitle("New Message")

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        vbox.addLayout(hbox)

        vboxLeft = QVBoxLayout()
        hbox.addLayout(vboxLeft)

        vboxRight = QVBoxLayout()
        hbox.addLayout(vboxRight)
        
        l = QLabel("To")
        vboxLeft.addWidget(l)
        
        self.tetoaddress = QTextEdit("")
        self.tetoaddress.setMaximumHeight(27)
        vboxRight.addWidget(self.tetoaddress)
        
        l = QLabel("Subject")
        vboxLeft.addWidget(l)
        
        self.tesubject = QTextEdit("")
        self.tesubject.setMaximumHeight(27)
        vboxRight.addWidget(self.tesubject)
        
        self.teBody = QTextEdit("")
        vbox.addWidget(self.teBody)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(0)
        vbox.addLayout(hbox2)

        bnOK = QPushButton("OK")
        hbox2.addWidget(bnOK)

        bnCancel = QPushButton("Cancel")
        hbox2.addWidget(bnCancel)

        bnCancel.clicked.connect(self.close)

        bnOK.clicked.connect(self.OK)

        self.setLayout(vbox)

        
    def OK(self):
        message1 = Message()
        message1.body = self.teBody.toPlainText() + """\n=========================================================================================\n
Livewire enabled emailer http://wwww.livewirecommunicator.org (""" + GetGlobalSettingStore().LoadSetting("EmailAddress") + """)\n
=========================================================================================\n"""

        message1.subject = self.tesubject.toPlainText() 
        addr1 = Address()
        addr1.email_address = self.tetoaddress.toPlainText() 
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        message1.fromaddress = GetGlobalSettingStore().LoadSetting("EmailAddress")
        message1.datetime = datetime.datetime.now()
        message1.addresses.append(addr1)

        msg = MIMEText(message1.body)
        msg['Subject'] = message1.subject
        msg['From'] = message1.fromaddress
        msg['To'] = addr1.email_address

        
        smtp = smtplib.SMTP_SSL(GetGlobalSettingStore().LoadSetting("SMTPServerName"), int(GetGlobalSettingStore().LoadSetting("SMTPServerPort")))
        smtp.login(GetGlobalSettingStore().LoadSetting("SMTPUserName"), GetGlobalSettingStore().LoadSetting("SMTPPassword"))
        smtp.sendmail(message1.fromaddress, [addr1.email_address], msg.as_string())
        smtp.quit()

        self.close()
