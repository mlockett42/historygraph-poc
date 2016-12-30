# Add a new multi chat session
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
import utils
from multichat import MultiChatChat, MultiChatShare

class FormNewMultiChat(QDialog):
    def __init__(self, parent, demux):
        super(FormNewMultiChat, self).__init__(parent)
        self.demux = demux

        self.setWindowTitle("New Multichats " + self.demux.myemail)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Email address'))
        self.teEmailAddress = QTextEdit("")
        self.teEmailAddress.setMaximumHeight(27)
        hbox.addWidget(self.teEmailAddress)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Chat name'))
        self.teChatName = QTextEdit("")
        self.teChatName.setMaximumHeight(27)
        hbox.addWidget(self.teChatName)
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        self.bnOK = QPushButton("OK")
        hbox.addWidget(self.bnOK)
        bnCancel = QPushButton("Cancel")
        hbox.addWidget(bnCancel)

        vbox.addLayout(hbox)
        self.bnOK.clicked.connect(self.OK)
        bnCancel.clicked.connect(self.close)

        self.setLayout(vbox)

    def OK(self):
        self.bnOK.clicked.disconnect()
        dc = self.parent().multichatapp.CreateNewDocumentCollection(None)
        self.parent().multichatapp.Share(dc, self.teEmailAddress.toPlainText())
        multichat = MultiChatChat(None)
        dc.AddDocumentObject(multichat)
        multichat.name = self.teChatName.toPlainText()
        share = MultiChatShare(None)
        multichat.shares.add(share)
        share.email = self.teEmailAddress.toPlainText()
        share = MultiChatShare(None)
        multichat.shares.add(share)
        share.email = self.demux.myemail
        self.parent().multichatapp.SaveDC(dc, self.demux.appdir)
        
        self.parent().refresh_multichats_list()
        self.close()



