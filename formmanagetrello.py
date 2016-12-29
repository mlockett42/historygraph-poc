#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
from formnewtrelloboard import FormNewTrelloBoard
import utils
from checkers import CheckersGame
from formcheckers import FormCheckers
from trello import TrelloBoard
from formedittrelloboard import FormEditTrelloBoard

class FormManageTrello(QDialog):
    def __init__(self, parent, demux):
        super(FormManageTrello, self).__init__(parent)
        self.demux = demux
        self.trelloapp = parent.trelloapp

        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.boards = QTableWidget(0,1)
        self.boards.verticalHeader().setVisible(False)
        self.boards.horizontalHeader().setVisible(False)
        self.boards.setMinimumWidth(200)
        self.boards.setMaximumWidth(200)
        self.boards.setMinimumHeight(400)
        self.boards.setColumnWidth(0,self.boards.width())
        self.boards.setRowCount(0)
        vbox.addWidget(self.boards)
        self.bnNewBoard = QPushButton("New Board")
        vbox.addWidget(self.bnNewBoard)
        self.bnEditBoard = QPushButton("Edit Board")
        vbox.addWidget(self.bnEditBoard)
        self.refresh_board_list()

        self.bnNewBoard.clicked.connect(self.newboard)
        self.bnEditBoard.clicked.connect(self.editboard)

    def newboard(self):
        self.form_new_trello_board = FormNewTrelloBoard(self, self.demux)
        self.form_new_trello_board.show()

    def editboard(self):
        selecteditems = self.boards.selectedItems()
        if len(selecteditems) == 0:
            return
        dc = None
        dcid = selecteditems[0].data(1)
        for dc2 in self.trelloapp.GetDocumentCollections():
            if dc2.id == dcid:
                dc = dc2
        boards = dc2.GetByClass(TrelloBoard)
        assert len(boards) == 1
        board = boards[0]
        #utils.log_output("FormManageTrello board.shares = ",list(board.shares), " self.demux.myemail=",self.demux.myemail)
        for share in board.shares:
            if share.email != self.demux.myemail:
                print "sharing to ", share.email, " dc2.id=",dc2.id
                self.trelloapp.Share(dc2, share.email)

        self.form_edit_board = FormEditTrelloBoard(self, self.demux, dc, board, self.trelloapp)
        self.form_edit_board.show()

    def refresh_board_list(self):
        self.boards.setRowCount(0)
        dcs = self.trelloapp.GetDocumentCollections()
        for dc in dcs:
            boards = dc.GetByClass(TrelloBoard)
            for board in boards:
                self.boards.setRowCount(self.boards.rowCount() + 1)
                row = self.boards.rowCount() - 1
                
                wi = QTableWidgetItem(board.name)
                wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
                wi.setData(1, dc.id)
                self.boards.setItem(row,0, wi)

