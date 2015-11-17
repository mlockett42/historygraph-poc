#filter by body

from messagefilter import *
from messagestore import Message

class MessageFilterBody(MessageFilter):
    def __init__(self, searchterm):
        self.searchterm = searchterm
        
    def getFilter(self):
        return Message.body.like('%' + self.searchterm + '%')

