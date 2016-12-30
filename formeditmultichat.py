#A mutlichat app

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtNetwork import *
import utils
from multichat import MultiChatItem, MultiChatChat
import time
from operator import itemgetter, attrgetter, methodcaller

class FormEditMultiChat(QDialog):
    class ChatCell(QHBoxLayout):
        def __init__(self, dc, multichatapp, item, owner):
            super(FormEditMultiChat.ChatCell, self).__init__()
            self.multichatapp = multichatapp
            self.dc = dc
            self.owner = owner
            #print 'ChatCell item.content=',item.content
            self.lContent =  QLabel(item.content)
            self.lContent.setMinimumHeight(300)
            self.lContent.setMaximumHeight(300)
            self.addWidget(self.lContent)
             
   
    def __init__(self, parent, demux, dc, multichat, multichatapp):
        super(FormEditMultiChat, self).__init__(parent)
        self.multichat = multichat
        self.multichatapp = multichatapp
        self.dc = dc
        self.demux = demux
        self.setWindowTitle("Multichat " + multichat.name + " " + self.demux.myemail)
        self.showMaximized()

        vbox2 = QVBoxLayout()
        self.bnNewMessage = QPushButton("New Message")
        vbox2.addWidget(self.bnNewMessage)
        self.bnNewMessage.clicked.connect(self.newmessage)

        self.vbox = QVBoxLayout()
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

        vbox2.addLayout(self.vbox)
        self.setLayout(vbox2)

        self.messagegrid = QTableWidget(0,1)
        self.vbox.addWidget(self.messagegrid)

        self.LayoutGrid()

    def LayoutGrid(self):
        self.messagegrid.verticalHeader().setVisible(False)
        self.messagegrid.horizontalHeader().setVisible(False)
        self.messagegrid.setMinimumWidth(800)
        self.messagegrid.setMinimumHeight(750)
        self.messagegrid.setColumnWidth(0,800)
        #self.messageheaders.resizeColumnsToContents()
        self.messagegrid.setRowCount(0)

        #self.gridlayout = QGridLayout()
        self.cells = dict()
        items = self.dc.GetByClass(MultiChatItem)
        items = sorted(items, key=lambda item:item.GetHash())
        items = sorted(items, key=attrgetter('eventtime'))
        row = 0
        for item in items:
            #cell = FormEditMultiChat.ChatCell(self.dc, self.multichatapp, item, self)
            #self.gridlayout.addLayout(cell, row, 0)
            self.messagegrid.setRowCount(self.messagegrid.rowCount() + 1)
            row = self.messagegrid.rowCount() - 1
            
            #print "LayoutGrid item.content=",item.content
            wi = QTableWidgetItem(item.content)
            wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi.setData(1, item)
            self.messagegrid.setItem(row,0, wi)

            self.cells[(row, 0)] = item.content
            row = row + 1

        #scrollablearea = QScrollArea()
        #self.vbox.addWidget(scrollablearea)
        #scrollablearea.setLayout(self.gridlayout)

    def prompt_user_for_message(self):
        return QInputDialog.getText(self, "Multi Chat", "Message")[0]

    def newmessage(self):
        text = self.prompt_user_for_message()
        if text != "":
            i = MultiChatItem(content=text, eventtime=time.time())
            self.dc.AddImmutableObject(i)
            self.multichatapp.SaveDC(self.dc, self.demux.appdir)
            self.multichatapp.UpdateShares()
            self.RefreshGrid()

    def RefreshGrid(self):
        #for i in reversed(range(self.vbox.count())): 
        #    self.vbox.itemAt(i).widget().setParent(None)

        self.LayoutGrid()
        
    def sendreceive(self):
        self.demux.CheckEmail()
        self.demux.SaveAllDCs()
        #self.multichatapp.LoadDocumentCollectionFromDisk(self.demux.appdir)
        #self.dc = self.multichatapp.GetDocumentCollectionByID(dc.id)
        self.RefreshGrid()

