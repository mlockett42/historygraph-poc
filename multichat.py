# The history graph based data model for a multi-user chat app
from Document import Document
from DocumentObject import DocumentObject
from FieldText import FieldText
from FieldIntRegister import FieldIntRegister
from FieldIntCounter import FieldIntCounter
from FieldList import FieldList
from FieldCollection import FieldCollection
from App import App
from ImmutableObject import ImmutableObject
from DocumentObject import DocumentObject
from Document import Document

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

