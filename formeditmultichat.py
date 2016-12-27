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
            self.lContent =  QLabel(item.content)
            self.addWidget(self.lContent)
             
   
    def __init__(self, parent, demux, dc, multichat, multichatapp):
        super(FormEditMultiChat, self).__init__(parent)
        self.multichat = multichat
        self.multichatapp = multichatapp
        self.dc = dc
        self.demux = demux
        self.setWindowTitle(multichat.name)
        self.showMaximized()

        vbox2 = QVBoxLayout()
        self.bnNewMessage = QPushButton("New Message")
        vbox2.addWidget(self.bnNewMessage)
        self.bnNewMessage.clicked.connect(self.newmessage)

        self.vbox = QVBoxLayout()
        vbox2.addLayout(self.vbox)
        self.setLayout(vbox2)

        self.LayoutGrid()

    def LayoutGrid(self):
        self.gridlayout = QGridLayout()
        self.cells = dict()
        items = self.dc.GetByClass(MultiChatItem)
        items = sorted(items, key=lambda item:item.GetHash())
        items = sorted(items, key=attrgetter('eventtime'))
        row = 0
        for item in items:
            cell = FormEditMultiChat.ChatCell(self.dc, self.multichatapp, item, self)
            self.gridlayout.addLayout(cell, row, 0)
            self.cells[(row, 0)] = cell
            row = row + 1

        scrollablearea = QScrollArea()
        self.vbox.addWidget(scrollablearea)
        scrollablearea.setLayout(self.gridlayout)

    def prompt_user_for_message(self):
        return QInputDialog.getText(self, "Multi Chat", "Message")

    def newmessage(self):
        text = self.prompt_user_for_message()
        if text != "":
            i = MultiChatItem(content=text, eventtime=time.time())
            self.dc.AddImmutableObject(i)
            self.multichatapp.UpdateShares()
            self.RefreshGrid()

    def RefreshGrid(self):
        for i in reversed(range(self.vbox.count())): 
            self.vbox.itemAt(i).widget().setParent(None)

        self.LayoutGrid()
        


