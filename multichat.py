# The history graph based data model for a multi-user chat app
from historygraph import Document
from historygraph import DocumentObject
from historygraph import FieldText
from historygraph import FieldIntRegister
from historygraph import FieldIntCounter
from historygraph import FieldList
from historygraph import FieldCollection
from App import App
from historygraph import ImmutableObject
from historygraph import DocumentObject
from historygraph import Document

class MultiChatItem(ImmutableObject):
    content = FieldText()
    eventtime = FieldIntRegister()

class MultiChatShare(ImmutableObject):
    email = FieldText()

class MultiChatShare(DocumentObject):
    email = FieldText()

class MultiChatChat(Document):
    name = FieldText()
    shares = FieldCollection(MultiChatShare)

class MultiChatApp(App):
    def MessageReceived(s):
        pass

    def CreateNewDocumentCollection(self, dcid):
        dc = super(MultiChatApp, self).CreateNewDocumentCollection(dcid)
        dc.Register(MultiChatItem)
        dc.Register(MultiChatShare)
        dc.Register(MultiChatChat)
        return dc

