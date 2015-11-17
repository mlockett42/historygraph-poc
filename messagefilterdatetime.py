#filter by date

from messagefilter import MessageFilter
from sqlalchemy import and_
from messagestore import Message

class MessageFilterDateTime(MessageFilter):
    def __init__(self, starttime, endtime):
        self.starttime = starttime
        self.endtime = endtime
        
    def getFilter(self):
        return and_(Message.datetime >= self.starttime, \
                    Message.datetime <= self.endtime)

