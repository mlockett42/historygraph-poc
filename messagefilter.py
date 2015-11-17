#An email message filter

from messagestore import Message

class MessageFilter:
    def applyFilter(self, session):
        return session.query(Message).filter(self.getFilter())

    def getFilter(self):
        assert False
