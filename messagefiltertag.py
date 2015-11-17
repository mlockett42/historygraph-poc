#filter by tag name

from messagefilter import *
from sqlalchemy import and_
from messagestore import Message
from messagestore import Tag

class MessageFilterByTag(MessageFilter):
    def __init__(self, tagname):
        self.tagname = tagname
        
    def applyFilter(self, session):
        return session.query(Message).join(Tag). \
               filter(Tag.tagname == self.tagname)

    def getFilter(self):
        assert False

