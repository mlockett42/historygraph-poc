#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *
from formnewmultichat import FormNewMultiChat
import utils
from multichat import MultiChatChat
from formeditmultichat import FormEditMultiChat

class FormManageMultiChat(QDialog):
    def __init__(self, parent, demux):
        super(FormManageMultiChat, self).__init__(parent)
        self.demux = demux
        self.multichatapp = parent.multichatapp

        self.setWindowTitle("Manage Multichats " + self.demux.myemail)

        vbox = QVBoxLayout()
        self.setLayout(vbox)
        self.multichats = QTableWidget(0,1)
        self.multichats.verticalHeader().setVisible(False)
        self.multichats.horizontalHeader().setVisible(False)
        self.multichats.setMinimumWidth(200)
        self.multichats.setMaximumWidth(200)
        self.multichats.setMinimumHeight(400)
        self.multichats.setColumnWidth(0,self.multichats.width())
        self.multichats.setRowCount(0)
        vbox.addWidget(self.multichats)
        self.bnNewMultiChat = QPushButton("New Mutli Chat")
        vbox.addWidget(self.bnNewMultiChat)
        self.bnEditMultiChat = QPushButton("Edit Multi Chat")
        vbox.addWidget(self.bnEditMultiChat)
        self.refresh_multichats_list()

        self.bnNewMultiChat.clicked.connect(self.newmultichat)
        self.bnEditMultiChat.clicked.connect(self.editmultichat)

    def newmultichat(self):
        self.form_new_multi_chat = FormNewMultiChat(self, self.demux)
        self.form_new_multi_chat.show()

    def editmultichat(self):
        selecteditems = self.multichats.selectedItems()
        if len(selecteditems) == 0:
            return
        dc = None
        dcid = selecteditems[0].data(1)
        for dc2 in self.multichatapp.GetDocumentCollections():
            if dc2.id == dcid:
                dc = dc2
        multichats = dc2.GetByClass(MultiChatChat)
        assert len(multichats) == 1
        multichat = multichats[0]
        #utils.log_output("FormManageTrello board.shares = ",list(board.shares), " self.demux.myemail=",self.demux.myemail)
        for share in multichat.shares:
            if share.email != self.demux.myemail:
                #utils.log_output("sharing to ", share.email, " dc2.id=",dc2.id)
                self.multichatapp.Share(dc2, share.email)

        self.form_edit_multi_chat = FormEditMultiChat(self, self.demux, dc, multichat, self.multichatapp)
        self.form_edit_multi_chat.show()

    def refresh_multichats_list(self):
        self.multichats.setRowCount(0)
        dcs = self.multichatapp.GetDocumentCollections()
        for dc in dcs:
            multichats = dc.GetByClass(MultiChatChat)
            for multichat in multichats:
                self.multichats.setRowCount(self.multichats.rowCount() + 1)
                row = self.multichats.rowCount() - 1
                
                wi = QTableWidgetItem(multichat.name)
                wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
                wi.setData(1, dc.id)
                self.multichats.setItem(row,0, wi)


