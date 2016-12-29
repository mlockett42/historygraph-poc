#A trello board app

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtNetwork import *
import utils
from trello import TrelloList, TrelloListLink, TrelloItem


class FormEditTrelloBoard(QDialog):
    class ListHeaderCell(QHBoxLayout):
        def __init__(self, dc, trelloapp, trellolistlink, owner):
            super(FormEditTrelloBoard.ListHeaderCell, self).__init__()
            self.trelloapp = trelloapp
            self.dc = dc
            self.owner = owner
            self.trellolistlink = trellolistlink
            trellolist = dc.objects[TrelloList.__name__][trellolistlink.list_id]
            self.teContent =  QTextEdit(trellolist.name)
            self.addWidget(self.teContent)
            self.bnSave = QPushButton("Save")
            self.bnSave.clicked.connect(self.save_list_name)
            self.addWidget(self.bnSave)
            self.bnAddItem = QPushButton("Add Item")
            self.addWidget(self.bnAddItem)
            self.bnAddItem.clicked.connect(self.add_item)
            self.bnMoveRight = QPushButton("Move Right")
            self.addWidget(self.bnMoveRight)
   
        def save_list_name(self):
            trellolist = self.dc.objects[TrelloList.__name__][self.trellolistlink.list_id]
            #utils.log_output('trellolist.name=',trellolist.name)
            trellolist.name = self.teContent.toPlainText()
            #utils.log_output('trellolist.name=',trellolist.name)
            self.owner.RefreshGrid()
            self.trelloapp.UpdateShares()

        def add_item(self):
            #utils.log_output("add_item pressed")
            trellolist = self.dc.objects[TrelloList.__name__][self.trellolistlink.list_id]

            ti = TrelloItem(None)
            trellolist.items.insert(len(trellolist.items), ti)
            ti.content = "Item 1"

            self.owner.RefreshGrid()
            self.owner.demux.SaveAllDCs()
            self.trelloapp.UpdateShares()



    class ListContentCell(QHBoxLayout):
        def __init__(self, dc, trelloitem, owner):
            super(FormEditTrelloBoard.ListContentCell, self).__init__()
            self.trelloitem = trelloitem
            self.owner = owner
            self.teContent =  QTextEdit(trelloitem.content)
            self.addWidget(self.teContent)
            self.bnSave = QPushButton("Save")
            self.bnSave.clicked.connect(self.save_content)
            self.addWidget(self.bnSave)

        def save_content(self):
            self.trelloitem.content = self.teContent.toPlainText()
            self.owner.RefreshGrid()
            utils.log_output("ListContentCell saving content - updating shares")
            #self.owner.demux.SaveAllDCs()
            self.owner.trelloapp.UpdateShares()

    class AddListCell(QHBoxLayout):
        def __init__(self, owner, trelloboard):
            super(FormEditTrelloBoard.AddListCell, self).__init__()
            self.bnAddList = QPushButton("Add List")
            self.bnAddList.clicked.connect(owner.addlist)
            self.addWidget(self.bnAddList)
            
   
    def __init__(self, parent, demux, dc, board, trelloapp):
        super(FormEditTrelloBoard, self).__init__(parent)
        self.board = board
        self.trelloapp = trelloapp
        self.dc = dc
        self.demux = demux
        self.setWindowTitle(board.name)
        self.showMaximized()

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        sendreceiverAction = QAction('&Send/Receive', self)
        sendreceiverAction.setShortcut('F5')
        sendreceiverAction.setStatusTip('Send and receive messages')
        sendreceiverAction.triggered.connect(self.sendreceive)

        closeAction = QAction('&Close', self)
        closeAction.setStatusTip('Close')
        closeAction.triggered.connect(self.close)

        self.menubar = QMenuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(sendreceiverAction)
        fileMenu.addAction(closeAction)

        self.vbox.setMenuBar(self.menubar)

        self.LayoutGrid()

    def LayoutGrid(self):
        self.gridlayout = QGridLayout()
        #utils.log_output("LayoutGrid started")
        self.cells = dict()
        column = 0    
        for tll in self.board.lists:
            #utils.log_output("LayoutGrid column ", column)
            cell = FormEditTrelloBoard.ListHeaderCell(self.dc, self.trelloapp, tll, self)
            self.gridlayout.addLayout(cell, 0, column)
            self.cells[(0, column)] = cell
            row = 1
            trellolist = self.dc.objects[TrelloList.__name__][tll.list_id]
            #utils.log_output("LayoutGrid len(trellolist.items)= ", len(trellolist.items))
            for ti in trellolist.items:
                cell = FormEditTrelloBoard.ListContentCell(self.dc, ti, self)
                self.gridlayout.addLayout(cell, row, column)
                self.cells[(row, column)] = cell
                #utils.log_output("LayoutGrid cell at ", (row, column), " = ", cell)
                row = row + 1
            column = column + 1

        cell = FormEditTrelloBoard.AddListCell(self, self.board)
        self.cells[(0, len(self.board.lists))] = cell

        scrollablearea = QScrollArea()
        self.vbox.addWidget(scrollablearea)
        scrollablearea.setLayout(self.gridlayout)

        #utils.log_output("LayoutGrid finished")

    def addlist(self):
        #utils.log_output("addlist started")

        trelloboard = self.board

        tl = TrelloList(None)
        trelloboard.dc.AddDocumentObject(tl)
        tl.name = 'List 2'

        tll = TrelloListLink(None)
        trelloboard.lists.insert(len(trelloboard.lists), tll)
        tll.list_id = tl.id

        self.demux.SaveAllDCs()
        self.trelloapp.UpdateShares()

        #utils.log_output("self.board.lists=",self.board.lists)
        #utils.log_output("trelloboard.lists=",trelloboard.lists)
        #utils.log_output("len(self.board.lists)=",len(self.board.lists))
        #utils.log_output("len(trelloboard.lists)=",len(trelloboard.lists))

        self.RefreshGrid()

    def RefreshGrid(self):
        for i in reversed(range(self.vbox.count())): 
            self.vbox.itemAt(i).widget().setParent(None)

        self.LayoutGrid()
        
        
    def sendreceive(self):
        self.demux.CheckEmail()
        self.demux.SaveAllDCs()
        self.trelloapp.LoadDocumentCollectionFromDisk(self.demux.appdir)
        self.RefreshGrid()


