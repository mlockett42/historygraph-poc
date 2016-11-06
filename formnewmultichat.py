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
        vbox = QVBoxLayout()
        self.teEmailAddress = QTextEdit("")
        self.teEmailAddress.setMaximumHeight(27)
        vbox.addWidget(self.teEmailAddress)
        self.teChatName = QTextEdit("")
        self.teChatName.setMaximumHeight(27)
        vbox.addWidget(self.teChatName)

        self.bnOK = QPushButton("OK")
        vbox.addWidget(self.bnOK)

        self.bnOK.clicked.connect(self.OK)

        self.setLayout(vbox)

    def OK(self):
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



