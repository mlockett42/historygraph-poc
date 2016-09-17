#Form to send a new message
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
from email.mime.text import MIMEText
#import mysmtplib as smtplib
import datetime
import utils

class FormNewMessage(QDialog):
    def __init__(self, parent, demux):
        super(FormNewMessage, self).__init__(parent)
        self.demux = demux
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

        self.bnOK = QPushButton("OK")
        hbox2.addWidget(self.bnOK)

        bnCancel = QPushButton("Cancel")
        hbox2.addWidget(bnCancel)

        bnCancel.clicked.connect(self.close)

        self.bnOK.clicked.connect(self.OK)

        self.setLayout(vbox)


    def OK(self):
        """
        message1 = Message()
        message1.body = self.teBody.toPlainText() + "\n=========================================================================================
Livewire enabled emailer http://wwww.livewirecommunicator.org (" + self.demux.myemail + ")
=========================================================================================\n"

        message1.subject = self.tesubject.toPlainText() 
        addr1 = Address()
        addr1.email_address = self.tetoaddress.toPlainText() 
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        message1.fromaddress = self.demux.myemail
        message1.datetime = datetime.datetime.now()
        message1.addresses.append(addr1)

        msg = MIMEText(message1.body)
        msg['Subject'] = message1.subject
        msg['From'] = message1.fromaddress
        msg['To'] = addr1.email_address

        
        smtp = smtplib.SMTP(self.demux.smtpserver, int(self.demux.smtpport))
        if self.demux.smtpserver != "localhost":
            smtp.login(self.demux.smtpuser, self.demux.smtppass)
        smtp.sendmail(message1.fromaddress, [addr1.email_address], msg.as_string())
        smtp.quit()
"""
        self.demux.SendPlainEmail(receivers = [self.tetoaddress.toPlainText()], subject = self.tesubject.toPlainText(), message=self.teBody.toPlainText())


        self.close()
