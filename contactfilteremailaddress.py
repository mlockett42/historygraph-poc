#A contact message filter
from messagestore import Contact
from messagestore import Message

class ContactFilterEmailAddress:
    def __init__(self, searchterm):
        self.searchterm = searchterm

    def applyFilter(self, session):
        return session.query(Contact).filter(self.getFilter())

    def getFilter(self):
        return Contact.emailaddress.like(self.searchterm)


