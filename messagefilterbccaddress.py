#filter by from address

from messagefilter import *
from sqlalchemy import and_
from messagestore import Message
from messagestore import Address

class MessageFilterByBCCAddress(MessageFilter):
    def __init__(self, toaddress):
        self.toaddress = toaddress
        
    def applyFilter(self, session):
        return session.query(Message).join(Address). \
               filter(Address.email_address == self.toaddress).filter(Address.addresstype == "BCC")

    def getFilter(self):
        assert False

