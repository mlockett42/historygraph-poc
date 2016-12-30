#A checkers game to introduce Python programming concepts
#Licence Apache 2.0
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtNetwork import *
import utils

class ClickableImageLabel(QLabel):
    def __init__(self, parent, location):
        super(ClickableImageLabel, self).__init__(parent)
        self.form = parent
        self.location = location
        pic = QPixmap(self.image_location)
        self.setPixmap(pic)
    def mouseReleaseEvent(self, ev):
        self.form.LabelClicked(self.location)

class ImgWhiteOnBlack(ClickableImageLabel):
    image_location = "images/whiteonblack.png"

class ImgBlackOnBlack(ClickableImageLabel):
    image_location = "images/blackonblack.png"

class ImgWhiteKingOnBlack(ClickableImageLabel):
    image_location = "images/whitekingonblack.png"

class ImgBlackKingOnBlack(ClickableImageLabel):
    image_location = "images/blackkingonblack.png"

class ImgBlackSquare(ClickableImageLabel):
    image_location = "images/blacksquare.png"

class ImgWhiteSquare(ClickableImageLabel):
    image_location = "images/whitesquare.png"

class FormCheckers(QDialog):
   
    def __init__(self, parent, demux, dc, game):
        super(FormCheckers, self).__init__(parent)
        self.game = game
        self.dc = dc
        self.demux = demux
        self.setWindowTitle("Play Checkers: " + game.name + " " + self.demux.myemail)
        self.showMaximized()
        self.gridlayout = QGridLayout()
        self.boardScreen = QTableWidget(8,8)
        self.gridlayout.addWidget(self.boardScreen, 0, 0)
        self.labelCurrentPlayer = QLabel("Current Player")
        self.gridlayout.addWidget(self.labelCurrentPlayer, 1, 0)
        self.labelStatus = QLabel("Status")
        self.gridlayout.addWidget(self.labelStatus, 2, 0)
        self.buttonEndTurn = QPushButton("End Turn")
        self.buttonEndTurn.setVisible(False)
        self.buttonEndTurn.clicked.connect(self.EndTurn)
        self.gridlayout.addWidget(self.buttonEndTurn, 3, 0)
        self.boardScreen.verticalHeader().setVisible(False)
        self.boardScreen.horizontalHeader().setVisible(False)
        for i in range(8):
            self.boardScreen.setColumnWidth(i, 100)
        for i in range(8):
            self.boardScreen.setRowHeight(i, 100)
        #The selected piece ie the one we are moving
        self.selected_piece = None

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

        self.gridlayout.setMenuBar(self.menubar)

        self.LayoutBoard()  
        self.DisplayCurrentPlayer()      

    def LayoutBoard(self):
        boardPieces = self.game.GetCurrentPieces()
        for y in range(8):
            for x in range(8):
                if (x,y) not in boardPieces:
                    if (x + y) % 2 == 0:
                        self.boardScreen.setCellWidget(y,x, ImgWhiteSquare(self, (x,y)))
                    else:
                        self.boardScreen.setCellWidget(y,x, ImgBlackSquare(self, (x,y)))
                elif boardPieces[(x,y)].pieceside == "W" and boardPieces[(x,y)].piecetype == "":
                    self.boardScreen.setCellWidget(y,x, ImgWhiteOnBlack(self, (x,y)))
                elif boardPieces[(x,y)].pieceside == "B" and boardPieces[(x,y)].piecetype == "":
                    self.boardScreen.setCellWidget(y,x, ImgBlackOnBlack(self, (x,y)))
                elif boardPieces[(x,y)].pieceside == "W" and boardPieces[(x,y)].piecetype == "K":
                    self.boardScreen.setCellWidget(y,x, ImgWhiteKingOnBlack(self, (x,y)))
                elif boardPieces[(x,y)].pieceside == "B" and boardPieces[(x,y)].piecetype == "K":
                    self.boardScreen.setCellWidget(y,z, ImgBlackKingOnBlack(self, (x,y)))
                else:
                    assert False

        self.setLayout(self.gridlayout)

    def GetMyColour(self):
        # Return the colour of the current user
        if self.demux.myemail == self.game.player_w:
            return 'W'
        elif self.demux.myemail == self.game.player_b:
            return 'B'
        else:
            assert False

    def DisplayCurrentPlayer(self):
        label_text = "Current Player: " + ("White" if self.game.GetTurnColour() == "W" else "Black") + \
            " You are: " + ("White" if self.GetMyColour() == "W" else "Black")
        print "label_text=",label_text
        self.labelCurrentPlayer.setText(label_text)

    def UpdateStatus(self, message):
        self.labelStatus.setText(message)

    def LabelClicked(self, location):
        boardPieces = self.game.GetCurrentPieces()
        if self.selected_piece is None:
            #If nothing is selected choose a piece to move
            if location not in boardPieces:
                #No piece on that square
                return
            if self.game.GetTurnColour() != boardPieces[location].pieceside:
                #Not the current player piece
                return
            if self.game.GetTurnColour() != self.GetMyColour():
                #Not my turn
                return
            allowed_moves = boardPieces[location].GetValidMoves()
            if len(allowed_moves) == 0:
                #If there are no allowed moves this piece cannot be selected
                return
            self.selected_piece = location
            self.UpdateStatus("Selected piece at " + str(location))
        else:
            piece = boardPieces[self.selected_piece]
            if location not in piece.GetValidMoves():
                self.UpdateStatus("Invalid move.")
                self.selected_piece = None
                return
            x = location[0]
            y = location[1]
            piece.MoveTo(x, y)
            status = "Piece moved from " + str(self.selected_piece) + " to " + str(location)
            if len(piece.GetValidCaptures()[0]) == 0:
                #utils.log_output("LabelClicked incrementing turn")
                self.game.turn.add(1)
                self.selected_piece = None
            else:
                self.buttonEndTurn.setVisible(True)
                self.selected_piece = location
            #utils.log_output("LabelClicked updating shares")
            self.parent().checkersapp.UpdateShares()
            #self.parent().checkersapp.SaveDC(self.dc, self.demux.appdir)
            self.demux.SaveAllDCs()

            self.UpdateStatus(status)
            self.DisplayCurrentPlayer()
            self.LayoutBoard()
            self.CheckForWinner()

    def EndTurn(self):
        #In certain circumstances we can manually end our turn
        self.next_player = self.GetOppositeColour()
        self.selected_piece = None
        self.DisplayCurrentPlayer()
        self.buttonEndTurn.setVisible(False)

    def CheckForWinner(self):
        if self.game.HasPlayerWon(self.game.GetTurnColour()):
            self.UpdateStatus(("White" if self.game.GetTurnColour() == "W" else "Black") + " has won")
            
        
    def sendreceive(self):
        self.demux.CheckEmail()
        self.demux.SaveAllDCs()
        #self.parent().checkersapp.LoadDocumentCollectionFromDisk(self.demux.appdir)
        self.selected_piece = None
        self.UpdateStatus("Send/Receive complete")
        self.DisplayCurrentPlayer()
        self.LayoutBoard()

