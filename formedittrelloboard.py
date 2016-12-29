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
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            hbox = QHBoxLayout()
            self.teContent =  QTextEdit(trellolist.name)
            self.teContent.setSizePolicy(sizePolicy)
            self.teContent.setMaximumHeight(50)
            self.teContent.setMaximumWidth(300)
            self.teContent.setMinimumHeight(50)
            self.teContent.setMinimumWidth(300)
            hbox.addWidget(self.teContent)
            self.bnSave = QPushButton("Save")
            self.bnSave.setSizePolicy(sizePolicy)
            self.bnSave.setMaximumHeight(25)
            self.bnSave.setMaximumWidth(80)
            self.bnSave.setMinimumHeight(25)
            self.bnSave.setMinimumWidth(80)
            self.bnSave.clicked.connect(self.save_list_name)
            hbox.addWidget(self.bnSave)
            self.bnAddItem = QPushButton("Add Item")
            self.bnAddItem.setSizePolicy(sizePolicy)
            self.bnAddItem.setMaximumHeight(25)
            self.bnAddItem.setMaximumWidth(80)
            self.bnAddItem.setMinimumHeight(25)
            self.bnAddItem.setMinimumWidth(80)
            hbox.addWidget(self.bnAddItem)
            self.bnAddItem.clicked.connect(self.add_item)
            self.bnMoveRight = QPushButton("Move Right")
            self.bnMoveRight.setSizePolicy(sizePolicy)
            self.bnMoveRight.setMaximumHeight(25)
            self.bnMoveRight.setMaximumWidth(80)
            self.bnMoveRight.setMinimumHeight(25)
            self.bnMoveRight.setMinimumWidth(80)
            hbox.addWidget(self.bnMoveRight)
            #self.setSizePolicy(sizePolicy)
            #self.setMaximumWidth(100)
            #self.setMaximumHeight(50)

            sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            widget = QWidget()
            widget.setLayout(hbox)
            widget.setSizePolicy(sizePolicy)
            self.addWidget(widget)

   
        def save_list_name(self):
            trellolist = self.dc.objects[TrelloList.__name__][self.trellolistlink.list_id]
            #utils.log_output('trellolist.name=',trellolist.name)
            trellolist.name = self.teContent.toPlainText()
            #utils.log_output('trellolist.name=',trellolist.name)
            self.owner.RefreshGrid()
            self.owner.demux.SaveAllDCs()
            self.trelloapp.UpdateShares()

        def add_item(self):
            #utils.log_output("add_item pressed")
            trellolist = self.dc.objects[TrelloList.__name__][self.trellolistlink.list_id]

            ti = TrelloItem(None)
            print "ListHeaderCell before len(trellolist.items)=",len(trellolist.items)
            trellolist.items.insert(len(trellolist.items), ti)
            print "ListHeaderCell after len(trellolist.items)=",len(trellolist.items)
            ti.content = "Item 1"

            self.owner.RefreshGrid()
            self.owner.demux.SaveAllDCs()
            self.trelloapp.UpdateShares()



    class ListContentCell(QHBoxLayout):
        def __init__(self, dc, trelloitem, owner):
            super(FormEditTrelloBoard.ListContentCell, self).__init__()
            self.trelloitem = trelloitem
            self.owner = owner
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            hbox = QHBoxLayout()
            self.teContent =  QTextEdit(trelloitem.content)
            self.teContent.setSizePolicy(sizePolicy)
            self.teContent.setMaximumHeight(50)
            self.teContent.setMaximumWidth(300)
            self.teContent.setMinimumHeight(50)
            self.teContent.setMinimumWidth(300)
            hbox.addWidget(self.teContent)
            self.bnSave = QPushButton("Save")
            self.bnSave.setSizePolicy(sizePolicy)
            self.bnSave.setMaximumHeight(25)
            self.bnSave.setMaximumWidth(80)
            self.bnSave.setMinimumHeight(25)
            self.bnSave.setMinimumWidth(80)
            self.bnSave.clicked.connect(self.save_content)
            hbox.addWidget(self.bnSave)
            sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            #self.setSizePolicy(sizePolicy)

            sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            widget = QWidget()
            widget.setLayout(hbox)
            widget.setSizePolicy(sizePolicy)
            self.addWidget(widget)

        def save_content(self):
            self.trelloitem.content = self.teContent.toPlainText()
            self.owner.RefreshGrid()
            utils.log_output("ListContentCell saving content - updating shares")
            self.owner.demux.SaveAllDCs()
            self.owner.trelloapp.UpdateShares()

    class AddListCell(QHBoxLayout):
        def __init__(self, owner, trelloboard):
            super(FormEditTrelloBoard.AddListCell, self).__init__()
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            self.bnAddList = QPushButton("Add List")
            self.bnAddList.setSizePolicy(sizePolicy)
            self.bnAddList.setMaximumHeight(25)
            self.bnAddList.setMaximumWidth(80)
            self.bnAddList.setMinimumHeight(25)
            self.bnAddList.setMinimumWidth(80)
            self.bnAddList.clicked.connect(owner.addlist)
            self.addWidget(self.bnAddList)
            sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            #self.setSizePolicy(sizePolicy)
            
   
    class DummyContentCell(QHBoxLayout):
        def __init__(self):
            super(FormEditTrelloBoard.DummyContentCell, self).__init__()
            sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            self.label =  QLabel('')
            self.label.setSizePolicy(sizePolicy)
            self.label.setMaximumHeight(50)
            self.label.setMaximumWidth(300)
            self.label.setMinimumHeight(50)
            self.label.setMinimumWidth(300)
            self.addWidget(self.label)



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
        maxrow = 0
        for tll in self.board.lists:
            #utils.log_output("LayoutGrid column ", column)
            cell = FormEditTrelloBoard.ListHeaderCell(self.dc, self.trelloapp, tll, self)
            self.gridlayout.addLayout(cell, 0, column)
            self.cells[(0, column)] = cell
            row = 1
            trellolist = self.dc.objects[TrelloList.__name__][tll.list_id]
            #utils.log_output("LayoutGrid len(trellolist.items)= ", len(trellolist.items))
            print "FormEditTrelloBoard LayoutGrid column = ",column," len( trellolist.items) =", len(trellolist.items)
            for ti in trellolist.items:
                cell = FormEditTrelloBoard.ListContentCell(self.dc, ti, self)
                self.gridlayout.addLayout(cell, row, column)
                self.cells[(row, column)] = cell
                #utils.log_output("LayoutGrid cell at ", (row, column), " = ", cell)
                row = row + 1
                maxrow = max(maxrow, row)
            column = column + 1

        cell = FormEditTrelloBoard.AddListCell(self, self.board)
        self.cells[(0, len(self.board.lists))] = cell
        self.gridlayout.addLayout(cell, 0, len(self.board.lists))

        for i in range(12 - maxrow):
            self.gridlayout.addLayout(FormEditTrelloBoard.DummyContentCell(), i, 0)

        #for i in range(column + 1):
        #    self.gridlayout.setColumnStretch(i, 0)

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
        self.dc = self.trelloapp.GetDocumentCollectionByID(dc.id)
        self.RefreshGrid()


