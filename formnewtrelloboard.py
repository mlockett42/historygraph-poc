#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
import utils
from trello import TrelloBoard, TrelloShare

class FormNewTrelloBoard(QDialog):
    def __init__(self, parent, demux):
        super(FormNewTrelloBoard, self).__init__(parent)
        self.demux = demux
        vbox = QVBoxLayout()
        self.teEmailAddress = QTextEdit("")
        self.teEmailAddress.setMaximumHeight(27)
        vbox.addWidget(self.teEmailAddress)
        self.teBoardName = QTextEdit("")
        self.teBoardName.setMaximumHeight(27)
        vbox.addWidget(self.teBoardName)

        self.bnOK = QPushButton("OK")
        vbox.addWidget(self.bnOK)

        self.bnOK.clicked.connect(self.OK)

        self.setLayout(vbox)

    def OK(self):
        dc = self.parent().trelloapp.CreateNewDocumentCollection(None)
        self.parent().trelloapp.Share(dc, self.teEmailAddress.toPlainText())
        trelloboard = TrelloBoard(None)
        dc.AddDocumentObject(trelloboard)
        trelloboard.name = self.teBoardName.toPlainText()
        ts = TrelloShare(None)
        trelloboard.shares.add(ts)
        ts.email = self.teEmailAddress.toPlainText()
        ts = TrelloShare(None)
        trelloboard.shares.add(ts)
        ts.email = self.demux.myemail
        trelloboard.CreateDefaultStartBoard()
        self.parent().trelloapp.SaveDC(dc, self.demux.appdir)
        
        self.parent().refresh_board_list()
        self.close()



