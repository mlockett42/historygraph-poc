#The history graph based model of a checkers game
#Licence Apache 2.0
import sys
from Document import Document
from DocumentObject import DocumentObject
from FieldText import FieldText
from FieldIntRegister import FieldIntRegister
from FieldIntCounter import FieldIntCounter
from FieldList import FieldList
from App import App

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

class CheckersGame(Document):
    name = FieldText()
    turn = FieldIntCounter() # Even = white's turn odd = black's
    pieces = FieldList(CheckersPiece)

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
                    piece.x = x
                    piece.y = y
                    piece.pieceside = s[0]
                    piece.piecetype = s[1:]
                    self.pieces.add(piece)
                x = x + 1
            y = y + 1

    def GetPieceAt(self, x, y):
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                return piece
        return None

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
            assert type(l) == list
            assert len(l) == 8
            x = 0
            for s in l:
                assert isinstance(s, basestring)
                assert s in {"W", "B", "WK", "BK", ""}
                assert s == "" or self.GetSquareColour(x, y) == "B"
                p = self.GetPieceAt(x,y)
                if s == "":
                    assert p is None
                else:
                    assert p.pieceside == s[0]
                    assert p.piecetype == s[1:]
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

