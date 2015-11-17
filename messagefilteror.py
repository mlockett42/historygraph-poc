#combine two filters and return all messages that match wither

from messagefilter import *
from sqlalchemy import or_

class MessageFilterOr(MessageFilter):
    def __init__(self, filter1, filter2):
        self.filter1 = filter1
        self.filter2 = filter2
        
    def getFilter(self):
        return or_(self.filter1.getFilter(), self.filter2.getFilter())
