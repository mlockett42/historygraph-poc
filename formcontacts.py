#View all contacts
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *

class FormContacts(QDialog):
    def __init__(self, parent, demux):
        super(FormContacts, self).__init__(parent)
        self.demux = demux

        vbox = QVBoxLayout()
        vbox.addStretch(1)

        self.setWindowTitle("Contacts")

        self.contacts = QTableWidget(0,2)
        self.contacts.verticalHeader().setVisible(False)
        self.contacts.horizontalHeader().setVisible(False)
        self.contacts.setMinimumWidth(630)
        #self.contacts.setMaximumWidth(200)
        self.contacts.setMinimumHeight(600)
        self.contacts.setColumnWidth(0,300)
        self.contacts.setColumnWidth(1,300)
        self.contacts.setRowCount(0)
        vbox.addWidget(self.contacts)
        self.bnClose = QPushButton("Close")
        vbox.addWidget(self.bnClose)

        self.bnClose.clicked.connect(self.close)

        self.setLayout(vbox)

        for contact in self.demux.contactstore.GetContacts():
            self.contacts.setRowCount(self.contacts.rowCount() + 1)
            row = self.contacts.rowCount() - 1
            
            wi = QTableWidgetItem(contact.emailaddress)
            wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi.setData(1, contact)
            self.contacts.setItem(row,0, wi)

            wi = QTableWidgetItem('Is encrypted' if contact.ishistorygraph and contact.publickey != '' else 'Not encrypted')
            wi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled )
            wi.setData(1, contact)
            self.contacts.setItem(row,1, wi)
        


