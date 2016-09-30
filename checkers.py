#A checkers game to introduce Python programming concepts
#Licence Apache 2.0
import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtNetwork import *

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

class Form(QDialog):
   
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Checkers")
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
        #A set of allowed moves
        self.allowed_moves = None 
        #The selected piece ie the one we are moving
        self.selected_piece = None
        #The next player either "W" or "B". White starts
        self.next_player = "W"

        self.InitialBoardSetup()

    def InitialBoardSetup(self):
        #A dict of board positions (stored as tuples) mapping to the underlying game pieces. The game piece 
        #is stored as a string. First character W or B for white or black. Optional second character if it
        #is a king
        self.boardPieces = dict() 

        for i in range(8):
            for j in range(8):
                #Position the initial pieces
                if (i + j) % 2 != 0:
                    #Piece can only go on a black square
                    if i <= 2:
                        #White pieces at the top
                        self.boardPieces[(i,j)] = "W"
                    if i >= 5:
                        #Black pieces at the bottom
                        self.boardPieces[(i,j)] = "B"
        self.LayoutBoard()  
        self.DisplayCurrentPlayer()      
        
    def LayoutBoard(self):
        for i in range(8):
            for j in range(8):
                if (i,j) not in self.boardPieces:
                    if (i + j) % 2 == 0:
                        self.boardScreen.setCellWidget(i,j, ImgWhiteSquare(self, (i,j)))
                    else:
                        self.boardScreen.setCellWidget(i,j, ImgBlackSquare(self, (i,j)))
                elif self.boardPieces[(i,j)] == "W":
                    self.boardScreen.setCellWidget(i,j, ImgWhiteOnBlack(self, (i,j)))
                elif self.boardPieces[(i,j)] == "B":
                    self.boardScreen.setCellWidget(i,j, ImgBlackOnBlack(self, (i,j)))
                elif self.boardPieces[(i,j)] == "WK":
                    self.boardScreen.setCellWidget(i,j, ImgWhiteKingOnBlack(self, (i,j)))
                elif self.boardPieces[(i,j)] == "BK":
                    self.boardScreen.setCellWidget(i,j, ImgBlackKingOnBlack(self, (i,j)))
                else:
                    assert False

        self.setLayout(self.gridlayout)

    def DisplayCurrentPlayer(self):
        self.labelCurrentPlayer.setText("Current Player: " + ("White" if self.next_player == "W" else "Black"))

    def UpdateStatus(self, message):
        self.labelStatus.setText(message)

    def LabelClicked(self, location):
        if self.selected_piece is None:
            #If nothing is selected choose a piece to move
            if location not in self.boardPieces:
                #No piece on that square
                return
            if self.next_player != self.boardPieces[location][0]:
                #Not the current player piece
                return
            self.CalcAllowedMoves(location)
            if len(self.allowed_moves) == 0:
                #If there are no allowed moves this piece cannot be selected
                self.allowed_moves = None
                return
            self.selected_piece = location
            self.UpdateStatus("Selected piece at " + str(location))
        else:
            if location not in self.allowed_moves:
                return
            captured_piece = self.allowed_moves[location]
            self.boardPieces[location] = self.boardPieces[self.selected_piece]
            del self.boardPieces[self.selected_piece]
            status = "Piece moved from " + str(self.selected_piece) + " to " + str(location)
            if captured_piece is not None:
                del self.boardPieces[captured_piece]
                status += " piece captured at " + str(captured_piece)
                #Test to see if more captures are possible
                self.allowed_moves = dict()
                self.CalcAllowedCaptureMoves(location)
            else:
                self.allowed_moves = None
            self.UpdateStatus(status)
            if self.allowed_moves is None or len(self.allowed_moves) == 0:
                #Check to see if we should make this piece into a king
                (row, col) = location
                final_row = 7 if self.next_player == "W" else 0
                if len(self.boardPieces[location]) == 1 and row == final_row:
                    #If the piece in question is not a king (ie only one character) and has been placed onto the final row make it a king
                    self.boardPieces[location] += "K"
                #Only move to the next player if more captures are impossible
                self.next_player = self.GetOppositeColour()
                self.selected_piece = None
                self.buttonEndTurn.setVisible(False)
            else:
                self.selected_piece = location
                self.buttonEndTurn.setVisible(True)
            self.DisplayCurrentPlayer()
            self.LayoutBoard()
            self.CheckForWinner()

    def GetDirection(self):
        return 1 if self.next_player == "W" else -1

    def EndTurn(self):
        #In certain circumstances we can manually end our turn
        self.next_player = self.GetOppositeColour()
        self.selected_piece = None
        self.DisplayCurrentPlayer()
        self.buttonEndTurn.setVisible(False)

    def GetOppositeColour(self):
        #Return the opposite colour of the next player
        return "W" if self.next_player == "B" else "B"
    
    def CalcAllowedMoves(self, location):
        (row, col) = location
        #Create the allowed moves dict a dict mapping locations we can move to to pieces
        #we can capture
        self.allowed_moves = dict()
        #White pieces move down black pieces move up
        direction = self.GetDirection()
        if col > 0:
            if (row + direction, col - 1) not in self.boardPieces:
                #If there is no piece in that position we may move there
                self.allowed_moves[(row + direction, col - 1)] = None
        if col < 7:
            if (row + direction, col + 1) not in self.boardPieces:
                #If there is no piece in that position we may move there
                self.allowed_moves[(row + direction, col + 1)] = None
        if self.boardPieces[location][-1] == "K":
            #If the piece is a king it can move backwards
            if col > 0:
                if (row - direction, col - 1) not in self.boardPieces:
                    #If there is no piece in that position we may move there
                    self.allowed_moves[(row - direction, col - 1)] = None
            if col < 7:
                if (row - direction, col + 1) not in self.boardPieces:
                    #If there is no piece in that position we may move there
                    self.allowed_moves[(row - direction, col + 1)] = None
        self.CalcAllowedCaptureMoves(location)

    def CalcAllowedCaptureMoves(self, location):
        (row, col) = location
        #Create the allowed moves dict a dict mapping locations we can move to to pieces
        #we can capture
        #White pieces move down black pieces move up
        direction = self.GetDirection()
        if col > 1:
            if (row + direction, col - 1) in self.boardPieces and \
                self.boardPieces[(row + direction, col - 1)][0] == self.GetOppositeColour() and \
                (row + 2 * direction, col - 2) not in self.boardPieces:
                #If we can capture a piece allow that move
                self.allowed_moves[(row + 2 * direction, col - 2)] = (row + direction, col - 1)
        if col < 6:
            if (row + direction, col + 1) in self.boardPieces and \
                self.boardPieces[(row + direction, col + 1)][0] == self.GetOppositeColour() and \
                (row + 2 * direction, col + 2) not in self.boardPieces:
                #If we can capture a piece allow that move
                self.allowed_moves[(row + 2 * direction, col + 2)] = (row + direction, col + 1)
        if self.boardPieces[location][-1] == "K":
            #If the piece is a king it can move backwards
            if col > 1:
                if (row - direction, col - 1) in self.boardPieces and \
                    self.boardPieces[(row - direction, col - 1)][0] == self.GetOppositeColour() and \
                    (row - 2 * direction, col - 2) not in self.boardPieces:
                    #If we can capture a piece allow that move
                    self.allowed_moves[(row - 2 * direction, col - 2)] = (row - direction, col - 1)
            if col < 6:
                if (row - direction, col + 1) in self.boardPieces and \
                    self.boardPieces[(row - direction, col + 1)][0] == self.GetOppositeColour() and \
                    (row - 2 * direction, col + 2) not in self.boardPieces:
                    #If we can capture a piece allow that move
                    self.allowed_moves[(row - 2 * direction, col + 2)] = (row - direction, col + 1)

    def CheckForWinner(self):
        #Build a list of our pieces. If it is empty the other player has won
        remaining_pieces = list()
        #Loop over the board and add the co ordinates of every piece of our
        for i in range(8):
            for j in range(8):
                if (i,j) in self.boardPieces:
                    if self.boardPieces[(i,j)][0] == self.next_player:
                        remaining_pieces.append((i,j))
        if len(remaining_pieces) == 0:
            #If we have no pieces the other player has won
            self.UpdateStatus(("White" if self.next_player == "B" else "Black") + " has won")
            
        
if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())
