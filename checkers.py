#The history graph based model of a checkers game
#Licence Apache 2.0
import sys
from historygraph import Document
from historygraph import DocumentObject
from historygraph import FieldText
from historygraph import FieldIntRegister
from historygraph import FieldIntCounter
from historygraph import FieldCollection
from App import App
import utils


class CheckersPiece(DocumentObject):
    pieceside = FieldText() # W or B
    piecetype = FieldText() # K for king or blank for pawn
    x = FieldIntRegister()
    y = FieldIntRegister()

    def FilterOffBoardCoords(self, s):
        # Return a set of coord with off board corrds removed
        return set([(x,y) for (x,y) in s if x >= 0 and x <= 7 and y >= 0 and y <= 7])

    def GetValidNonCaptureMoves(self):
        if self.pieceside == "W" and self.piecetype == "":
            ret = {(self.x - 1, self.y + 1),(self.x + 1, self.y + 1)}
        elif self.pieceside == "B" and self.piecetype == "":
            ret = {(self.x - 1, self.y - 1),(self.x + 1, self.y - 1)}
        if self.pieceside == "W" and self.piecetype == "K":
            ret = {(self.x - 1, self.y + 1),(self.x + 1, self.y + 1),(self.x - 1, self.y - 1),(self.x + 1, self.y - 1)}
        if self.pieceside == "B" and self.piecetype == "K":
            ret = {(self.x - 1, self.y + 1),(self.x + 1, self.y + 1),(self.x - 1, self.y - 1),(self.x + 1, self.y - 1)}
        #Filter off board coordinates
        ret = self.FilterOffBoardCoords(ret)
        return ret

    def GetValidMoves(self):
        ret = self.GetValidNonCaptureMoves()
        #Filter out occupied squares
        checkersgame = self.parent.parent
        ret = ret - checkersgame.GetOccupiedSquares()
        return ret | self.GetValidCaptures()[0]

    def GetValidCaptures(self):
        validmoves = self.GetValidNonCaptureMoves()
        checkersgame = self.parent.parent
        # Get list of square occupied by enemy pieces
        occupiedsquares = checkersgame.GetOccupiedSquares()
        enemyoccupiedsquares = set([(x,y) for (x,y) in occupiedsquares if checkersgame.GetPieceAt(x,y).pieceside != self.pieceside])
        # figure out pieces we can capture
        capturablepieces = validmoves & enemyoccupiedsquares
        # figure out the squares we need to move to to do the capture
        capturingmoveslist = [((2*(x-self.x)+self.x,2*(y-self.y)+self.y), (x,y)) for (x,y) in capturablepieces]            
        capturingmoves = set([cm[0] for cm in capturingmoveslist])
        capturingmovesdict = dict(capturingmoveslist)
        # remove occupied squares and return the result
        return (self.FilterOffBoardCoords(capturingmoves - occupiedsquares), capturingmovesdict)

    def MoveTo(self, x, y):
        assert self.parent.parent.GetTurnColour() == self.pieceside
        assert (x, y) in self.GetValidMoves()
        capturingmovesdict = self.GetValidCaptures()[1]
        if (x,y) in capturingmovesdict:
            captured_piece_position = capturingmovesdict[(x,y)]
            self.parent.remove(self.parent.parent.GetPieceAt(captured_piece_position[0],captured_piece_position[1]).id)
        self.x = x
        self.y = y
        #Should this piece be made into a king?
        backrow = 7 if self.pieceside == 'W' else 0 # Which row is the back row depends on which colour we are
        if y == backrow:
            # If the piece was made it to the back row it should be made a king
            self.piecetype = 'K'
        

class CheckersGame(Document):
    name = FieldText()
    turn = FieldIntCounter() # Even = white's turn odd = black's
    player_w = FieldText()
    player_b = FieldText()
    pieces = FieldCollection(CheckersPiece)

    def GetSquareColour(self, x, y):
        return "W" if ((x + y) % 2 == 0) else "B"

    def CreateBoard(self, ll):
        # ll = a list of 8 lists. Each of those lists consists of 8 strings:
        # Blank = no piece "W" or "B" = white or black pawn
        # "WK" or "BK" = white or black king
        assert len(self.pieces) == 0
        assert type(ll) == list
        assert len(ll) == 8
        y = 0
        for l in ll:
            assert type(l) == list
            assert len(l) == 8
            x = 0
            for s in l:
                assert isinstance(s, basestring)
                assert s in {"W", "B", "WK", "BK", ""}
                assert s == "" or self.GetSquareColour(x, y) == "B"
                if s != "":
                    piece = CheckersPiece(None)
                    self.pieces.add(piece)
                    piece.x = x
                    piece.y = y
                    piece.pieceside = s[0]
                    piece.piecetype = s[1:]
                x = x + 1
            y = y + 1

    def GetPieceAt(self, x, y):
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece
        return None

    def GetCurrentPieces(self):
        #Return a dict of positions and the piece (if any at them)
        return dict([((piece.x, piece.y), piece) for piece in self.pieces])

    def CreateDefaultStartBoard(self):
        return self.CreateBoard(
                           [['','W','','W','','W','','W'],
                            ['W','','W','','W','','W',''],
                            ['','W','','W','','W','','W'],
                            ['','','','','','','',''],
                            ['','','','','','','',''],
                            ['B','','B','','B','','B',''],
                            ['','B','','B','','B','','B'],
                            ['B','','B','','B','','B',''],
                            ])

    def GetOccupiedSquares(self):
        return set([(piece.x, piece.y) for piece in self.pieces])

    def assertBoardEquals(self, ll):
        # ll = a list of 8 lists. Each of those lists consists of 8 strings:
        # Blank = no piece "W" or "B" = white or black pawn
        # "WK" or "BK" = white or black king
        assert type(ll) == list
        assert len(ll) == 8
        y = 0
        for l in ll:
            assert type(l) == list, "l = " + str(l)
            assert len(l) == 8, "l = " + str(l)
            x = 0
            for s in l:
                #print "assertBoardEquals x = " + str(x) + ", y = " + str(y)
                assert isinstance(s, basestring), "x = " + str(x) + ", y = " + str(y)
                assert s in {"W", "B", "WK", "BK", ""}, "x = " + str(x) + ", y = " + str(y)
                assert s == "" or self.GetSquareColour(x, y) == "B", "x = " + str(x) + ", y = " + str(y)
                p = self.GetPieceAt(x,y)
                if s == "":
                    assert p is None, "x = " + str(x) + ", y = " + str(y)
                else:
                    assert p is not None, "x = " + str(x) + ", y = " + str(y)
                    assert p.pieceside == s[0], "x = " + str(x) + ", y = " + str(y)
                    assert p.piecetype == s[1:], "x = " + str(x) + ", y = " + str(y)
                x = x + 1
            y = y + 1

    def GetTurnColour(self):
        return "W" if (self.turn.get() % 2 == 0) else "B"

    def GetOppositeColour(self, side):
        assert side in {"W", "B"}
        return "W" if side == "B" else "B"

    def HasPlayerWon(self, player):
        # A player has won if the other player has no valid moves left. including if the 
        for p in self.pieces:
            if p.pieceside == self.GetOppositeColour(player):
                if len(p.GetValidMoves()) > 0:
                    return False
        return True

class CheckersApp(App):
    def MessageReceived(s):
        pass

    def CreateNewDocumentCollection(self, dcid):
        dc = super(CheckersApp, self).CreateNewDocumentCollection(dcid)
        dc.Register(CheckersPiece)
        dc.Register(CheckersGame)
        return dc

