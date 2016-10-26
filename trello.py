# The history graph based data model for the trello app
from Document import Document
from DocumentObject import DocumentObject
from FieldText import FieldText
from FieldIntRegister import FieldIntRegister
from FieldIntCounter import FieldIntCounter
from FieldList import FieldList
from FieldCollection import FieldCollection
from App import App

class TrelloItem(DocumentObject):
    content = FieldText()

class TrelloList(Document):
    name = FieldText()
    items = FieldList(TrelloItem)

class TrelloListLink(DocumentObject):
    list_id = FieldText()

class TrelloShare(DocumentObject):
    email = FieldText()

class TrelloBoard(Document):
    name = FieldText()
    lists = FieldList(TrelloListLink)
    shares = FieldCollection(TrelloShare)

    def CreateDefaultStartBoard(self):
        assert len(self.lists) == 0
        tl = TrelloList(None)
        self.dc.AddDocumentObject(tl)
        tl.name = 'List 1'
        tll = TrelloListLink(None)
        self.lists.insert(0, tll)
        tll.list_id = tl.id
        
        

class TrelloApp(App):
    def MessageReceived(s):
        pass

    def CreateNewDocumentCollection(self, dcid):
        dc = super(TrelloApp, self).CreateNewDocumentCollection(dcid)
        dc.Register(TrelloItem)
        dc.Register(TrelloList)
        dc.Register(TrelloListLink)
        dc.Register(TrelloBoard)
        dc.Register(TrelloShare)
        return dc

