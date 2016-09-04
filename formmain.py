#This is the main screen for livewire communicator
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
from formsettings import *
import poplib
import string
from formviewmessage import FormViewMessage
from formnewmessage import FormNewMessage

class FormMain(QMainWindow):
    def __init__(self, parent, demux):
        super(FormMain, self).__init__(parent)
        self.demux = demux
        self.setWindowTitle("Livewire Communicator")
        
        hbox = QHBoxLayout()
        hbox.addStretch(0)

        lblSearch = QLabel("Search")
        hbox.addWidget(lblSearch)
        teSearch = QTextEdit("")
        teSearch.setMaximumHeight(27)
        hbox.addWidget(teSearch)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        
        tagnames = QTableWidget(0,1)
        tagnames.verticalHeader().setVisible(False)
        tagnames.horizontalHeader().setVisible(False)
        tagnames.setMinimumWidth(200)
        tagnames.setMaximumWidth(200)
        tagnames.setMinimumHeight(400)
        tagnames.setColumnWidth(0,tagnames.width())
        tagnames.setRowCount(0)
        hbox2.addWidget(tagnames)

        self.messageheaders = QTableWidget(0,3)
        self.messageheaders.verticalHeader().setVisible(False)
        self.messageheaders.horizontalHeader().setVisible(False)
        self.messageheaders.setMinimumWidth(600)
        self.messageheaders.setMinimumHeight(400)
        self.messageheaders.setColumnWidth(0,200)
        self.messageheaders.setColumnWidth(1,200)
        self.messageheaders.setColumnWidth(2,200)
        #self.messageheaders.resizeColumnsToContents()
        self.messageheaders.setRowCount(0)
        self.DisplayMessages()
        hbox2.addWidget(self.messageheaders)
        self.messageheaders.doubleClicked.connect(self.messagedoubleclicked)

        vbox.addLayout(hbox2)

        main_widget = QWidget(self)
        main_widget.setLayout(vbox)

        self.setCentralWidget(main_widget)

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        settingsAction = QAction('&Settings', self)
        settingsAction.setStatusTip('Change settings')
        settingsAction.triggered.connect(self.DisplaySettings)

        sendreceiverAction = QAction('&Send/Receive', self)
        sendreceiverAction.setShortcut('F5')
        sendreceiverAction.setStatusTip('Send and receive messages')
        sendreceiverAction.triggered.connect(self.sendreceive)

        newmessageAction = QAction('&New Message', self)
        newmessageAction.setShortcut('Ctrl+N')
        newmessageAction.setStatusTip('New Message')
        newmessageAction.triggered.connect(self.newmessage)

        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(newmessageAction)
        fileMenu.addAction(sendreceiverAction)
        fileMenu.addAction(exitAction)
        
        optionsMenu = self.menubar.addMenu('&Options')
        optionsMenu.addAction(settingsAction)


    def DisplaySettings(self):
        self.formsettings = FormSettings(self, self.demux)
        self.formsettings.show()

    def sendreceive(self):
        pop = poplib.POP3_SSL(GetGlobalSettingStore().LoadSetting("POPServerName"), int(GetGlobalSettingStore().LoadSetting("POPServerPort")))
        pop.user(GetGlobalSettingStore().LoadSetting("POPUserName")) 
        pop.pass_(GetGlobalSettingStore().LoadSetting("POPPassword"))

        (numMsgs, totalSize) = pop.stat()

        for number in range(numMsgs):
            (server_msg, body, octets) = pop.retr(number + 1)
            body = string.join(body, "\n")

            message = Message.fromrawbody(body)

            GetGlobalMessageStore().AddMessage(message)

        self.DisplayMessages()

    def DisplayMessages(self):
        self.messageheaders.setRowCount(0)
        for message in self.demux.messagestore.GetMessages():
            self.messageheaders.setRowCount(self.messageheaders.rowCount() + 1)
            row = self.messageheaders.rowCount() - 1
            
            wi = QTableWidgetItem(message.fromaddress)
            wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi.setData(1, message)
            self.messageheaders.setItem(row,0, wi)
            
            wi2 = QTableWidgetItem(message.subject)
            wi2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi2.setData(1, message)
            self.messageheaders.setItem(row, 1, wi2)
            
            wi3 = QTableWidgetItem(str(message.datetime))
            wi3.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi3.setData(1, message)
            self.messageheaders.setItem(row, 2, wi3)

    def messagedoubleclicked(self, mi):
        row = mi.row()
        column = mi.column()
        message = self.messageheaders.item(row,column).data(1)
        formviewmessage = FormViewMessage(message, self)
        formviewmessage.show()
        
    def newmessage(self):
        form = FormNewMessage(self)
        form.show()
    
