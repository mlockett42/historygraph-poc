#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
import utils
from checkers import CheckersGame

class FormNewsCheckersGames(QDialog):
    def __init__(self, parent, demux):
        super(FormNewsCheckersGames, self).__init__(parent)
        self.demux = demux
        self.setWindowTitle("New checkers game " + self.demux.myemail)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Email address'))
        self.teEmailAddress = QTextEdit("")
        self.teEmailAddress.setMaximumHeight(27)
        hbox.addWidget(self.teEmailAddress)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Checkers Board name'))
        self.teGameName = QTextEdit("")
        self.teGameName.setMaximumHeight(27)
        hbox.addWidget(self.teGameName)
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
        dc = self.parent().checkersapp.CreateNewDocumentCollection(None)
        #self.parent().checkersapp.SaveDC(dc, "/run/shm/demux1")
        self.parent().checkersapp.Share(dc, self.teEmailAddress.toPlainText())
        checkersgame = CheckersGame(None)
        dc.AddDocumentObject(checkersgame)
        checkersgame.name = self.teGameName.toPlainText()
        checkersgame.player_w = self.demux.myemail
        checkersgame.player_b = self.teEmailAddress.toPlainText()
        checkersgame.CreateDefaultStartBoard()
        self.parent().checkersapp.SaveDC(dc, self.demux.appdir)
        
        self.parent().refresh_game_list()
        self.close()



