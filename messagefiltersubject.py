#filter by subject

from messagefilter import *
from messagestore import Message

class MessageFilterSubject(MessageFilter):
    def __init__(self, searchterm):
        self.searchterm = searchterm
        
    def getFilter(self):
        return Message.subject.like('%' + self.searchterm + '%')

