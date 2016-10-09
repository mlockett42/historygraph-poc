#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
import utils
from checkers import CheckersGame

class FormNewsCheckersGames(QDialog):
    def __init__(self, parent, demux):
        super(FormNewsCheckersGames, self).__init__(parent)
        vbox = QVBoxLayout()
        self.teEmailAddress = QTextEdit("")
        self.teEmailAddress.setMaximumHeight(27)
        vbox.addWidget(self.teEmailAddress)
        self.teGameName = QTextEdit("")
        self.teGameName.setMaximumHeight(27)
        vbox.addWidget(self.teGameName)

        self.bnOK = QPushButton("OK")
        vbox.addWidget(self.bnOK)

        self.bnOK.clicked.connect(self.OK)

        self.setLayout(vbox)

    def OK(self):
        checkersgame = CheckersGame(None)
        checkersgame.name = self.teGameName.toPlainText()
        checkersgame.CreateDefaultStartBoard()
        self.parent().checkersapp.GetDocumentCollections()[0].AddDocumentObject(checkersgame)
        self.parent().refresh_game_list()
        self.close()



