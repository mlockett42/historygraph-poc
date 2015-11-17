#combine to filter and return all messages that match both

from messagefilter import *
from sqlalchemy import and_

class MessageFilterAnd(MessageFilter):
    def __init__(self, filter1, filter2):
        self.filter1 = filter1
        self.filter2 = filter2
        
    def getFilter(self):
        return and_(self.filter1.getFilter(), self.filter2.getFilter())
