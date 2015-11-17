#View a received message
from PySide.QtCore import *
from PySide.QtGui import *
from messagestore import *

class FormViewMessage(QDialog):
    def __init__(self, message, parent = None):
        super(FormViewMessage, self).__init__(parent)
        self.setWindowTitle("View Message")
        self.message = message

        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        vbox.addLayout(hbox)

        vboxLeft = QVBoxLayout()
        hbox.addLayout(vboxLeft)

        vboxRight = QVBoxLayout()
        hbox.addLayout(vboxRight)
        
        l = QLabel("Date")
        vboxLeft.addWidget(l)
        
        l = QLabel(str(self.message.datetime))
        vboxRight.addWidget(l)
        
        l = QLabel("From")
        vboxLeft.addWidget(l)
        
        l = QLabel(self.message.fromaddress)
        vboxRight.addWidget(l)
        
        l = QLabel("Subject")
        vboxLeft.addWidget(l)
        
        l = QLabel(self.message.subject)
        vboxRight.addWidget(l)
        
        teBody = QTextEdit(message.body)
        vbox.addWidget(teBody)

        self.setLayout(vbox)
        
