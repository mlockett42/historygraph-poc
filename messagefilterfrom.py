#filter by from address

import MessageFilter

class MessageFilterFrom(MessageFilter):
    def __init__(self, fromaddress):
        self.fromaddress = fromaddress
        
    def applyFilter(self, l):
        ret = list()
        for m in l:
            if m.fromaddress == self.fromaddress:
                ret.append(m)
        return ret

