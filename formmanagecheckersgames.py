#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
from formnewscheckersgames import FormNewsCheckersGames
import utils
from checkers import CheckersGame
from formcheckers import FormCheckers

class FormManageCheckersGames(QDialog):
    def __init__(self, parent, demux):
        super(FormManageCheckersGames, self).__init__(parent)
        self.demux = demux
        self.checkersapp = parent.checkersapp

        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.games = QTableWidget(0,1)
        self.games.verticalHeader().setVisible(False)
        self.games.horizontalHeader().setVisible(False)
        self.games.setMinimumWidth(200)
        self.games.setMaximumWidth(200)
        self.games.setMinimumHeight(400)
        self.games.setColumnWidth(0,self.games.width())
        self.refresh_game_list()
        self.games.setRowCount(0)
        vbox.addWidget(self.games)
        self.bnNewGame = QPushButton("New Game")
        vbox.addWidget(self.bnNewGame)
        self.bnPlayGame = QPushButton("Play Game")
        vbox.addWidget(self.bnPlayGame)

        self.bnNewGame.clicked.connect(self.newgame)
        self.bnPlayGame.clicked.connect(self.playgame)

    def newgame(self):
        self.form_new_checkers_game = FormNewsCheckersGames(self, self.demux)
        self.form_new_checkers_game.show()

    def playgame(self):
        selecteditems = self.games.selectedItems()
        if len(selecteditems) == 0:
            return
        self.form_play_checkers = FormCheckers(self, self.demux, self.checkersapp.GetDocumentCollections()[0], selecteditems[0].data(1))
        self.form_play_checkers.show()

    def refresh_game_list(self):
        self.games.setRowCount(0)
        dc = self.checkersapp.GetDocumentCollections()[0]
        games = dc.GetByClass(CheckersGame)
        for game in games:
            self.games.setRowCount(self.games.rowCount() + 1)
            row = self.games.rowCount() - 1
            
            wi = QTableWidgetItem(game.name)
            wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi.setData(1, game)
            self.games.setItem(row,0, wi)

