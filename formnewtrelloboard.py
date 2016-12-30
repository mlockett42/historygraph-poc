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
        self.setWindowTitle("New trello board " + self.demux.myemail)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Email address'))
        self.teEmailAddress = QTextEdit("")
        self.teEmailAddress.setMaximumHeight(27)
        hbox.addWidget(self.teEmailAddress)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Trello Board name'))
        self.teBoardName = QTextEdit("")
        self.teBoardName.setMaximumHeight(27)
        hbox.addWidget(self.teBoardName)
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



