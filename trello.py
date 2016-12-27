# The history graph based data model for the trello app
from historygraph import Document
from historygraph import DocumentObject
from historygraph import FieldText
from historygraph import FieldIntRegister
from historygraph import FieldIntCounter
from historygraph import FieldList
from historygraph import FieldCollection
from App import App

class TrelloItem(DocumentObject):
    content = FieldText()

class TrelloList(DocumentObject):
    name = FieldText()
    items = FieldList(TrelloItem)

#class TrelloListLink(DocumentObject):
#    list_id = FieldText()

class TrelloShare(DocumentObject):
    email = FieldText()

class TrelloBoard(Document):
    name = FieldText()
    lists = FieldList(TrelloList)
    shares = FieldCollection(TrelloShare)

    def CreateDefaultStartBoard(self):
        assert len(self.lists) == 0
        tl = TrelloList(None)
        self.dc.AddDocumentObject(tl)
        tl.name = 'List 1'
        self.lists.insert(0, tl)
        
        

class TrelloApp(App):
    def MessageReceived(s):
        pass

    def CreateNewDocumentCollection(self, dcid):
        dc = super(TrelloApp, self).CreateNewDocumentCollection(dcid)
        dc.Register(TrelloItem)
        dc.Register(TrelloList)
        #dc.Register(TrelloListLink)
        dc.Register(TrelloBoard)
        dc.Register(TrelloShare)
        return dc

