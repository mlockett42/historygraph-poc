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
        self.setWindowTitle("New Message " + self.demux.myemail)

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
        #If the email matches a contact with encryption send encrypted otherwise don't
        contacts = self.demux.contactstore.GetContacts()
        for contact in contacts:
            if contact.ishistorygraph and CleanedEmailAddress(self.tetoaddress.toPlainText()) == CleanedEmailAddress(contact.emailaddress):
                self.demux.SendEncryptedEmail(contact, subject = self.tesubject.toPlainText(), message=self.teBody.toPlainText())
                #self.demux.SendPlainEmail(receivers = [self.tetoaddress.toPlainText()], subject = self.tesubject.toPlainText(), message=self.teBody.toPlainText())
                return
        self.demux.SendPlainEmail(receivers = [self.tetoaddress.toPlainText()], subject = self.tesubject.toPlainText(), message=self.teBody.toPlainText())


        self.close()
