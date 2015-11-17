#filter by from address

from messagefilter import *
from sqlalchemy import and_
from messagestore import Message

class MessageFilterFromAddress(MessageFilter):
    def __init__(self, fromaddress):
        self.fromaddress = fromaddress
        
    def getFilter(self):
        return Message.fromaddress == self.fromaddress

