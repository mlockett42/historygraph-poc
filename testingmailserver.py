# From http://flylib.com/books/en/2.407.1.60/1/
from twisted.mail import smtp, maildir
from zope.interface import implements
from twisted.internet import protocol, reactor, defer
import os
from email.Header import Header
from threading import Thread
from collections import defaultdict

validDomain = None
validMailnames = None
mailDict = None

class DictMessageWriter(object):
    implements(smtp.IMessage)

    def __init__(self, username):
        self.username = username
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        # message is complete, store it
        print "Message data complete."
        self.lines.append('') # add a trailing newline
        messageData = '\n'.join(self.lines)
        global mailDict
        mailDict[self.username].append(messageData)

    def connectionLost(self):
        print "Connection lost unexpectedly!"
        # unexpected loss of connection; don't save
        del(self.lines)

class LocalDelivery(object):
    implements(smtp.IMessageDelivery)

    def __init__(self):
        pass

    def receivedHeader(self, helo, origin, recipients):
        myHostname, clientIP = helo
        headerValue = "by %s from %s with ESMTP ; %s" % (
            myHostname, clientIP, smtp.rfc822date( ))
        # email.Header.Header used for automatic wrapping of long lines
        return "Received: %s" % Header(headerValue)

    def validateTo(self, user):
        global validDomain
        global validMailnames
        if user.dest.domain != validDomain:
            raise smtp.SMTPBadRcpt(user)
        if user.dest.local not in validMailnames:
            raise smtp.SMTPBadRcpt(user)
        print "Accepting mail for %s..." % user.dest
        return lambda: DictMessageWriter(user.dest))

    def validateFrom(self, helo, originAddress):
        # accept mail from anywhere. To reject an address, raise
        # smtp.SMTPBadSender here.
        return originAddress

class SMTPFactory(protocol.ServerFactory):
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        delivery = LocalDelivery()
        smtpProtocol = smtp.SMTP(delivery)
        smtpProtocol.factory = self
        return smtpProtocol

def StartTestingMailServer(domain, mailnames):
    #This function starts the mail server reactor up in a seperate thread
    #domain = the internet domain to accept mail for a serve mail for
    #mailnames = a set of allowed mail names
    #only one email server can be run inside our program at a time because the reactor is a global variable
    global validDomain
    global validMailnames
    validDomain = domain
    validMailnames = mailnames
    mailDict = defaultdict(list)
    reactor.listenTCP(10025, SMTPFactory())
    from twisted.internet import ssl
    # SSL stuff here... and certificates...
    Thread(target=reactor.run, args=(False,)).start()

def StopTestingMailServer():
    reactor.callFromThread(reactor.stop)




















#Twisted pop3 client to merge in with the SMTP server above
#From: http://pepijndevos.nl/twisted-pop3-example-server/
"""
An example pop3 server
"""

from twisted.application import internet, service
from twisted.cred.portal import Portal, IRealm
from twisted.internet.protocol import ServerFactory
from twisted.mail import pop3
from twisted.mail.pop3 import IMailbox
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from zope.interface import implements
from itertools import repeat
from hashlib import md5
from StringIO import StringIO

class SimpleMailbox:
    implements(IMailbox)

    def __init__(self):
        message = """From: me
To: you
Subject: A test mail

Hello world!"""
        self.messages = [m for m in repeat(message, 20)]


    def listMessages(self, index=None):
        if index != None:
            return len(self.messages[index])
        else:
            return [len(m) for m in self.messages]

    def getMessage(self, index):
        return StringIO(self.messages[index])

    def getUidl(self, index):
        return md5(self.messages[index]).hexdigest()

    def deleteMessage(self, index):
        pass

    def undeleteMessages(self):
        pass

    def sync(self):
        pass


class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IMailbox in interfaces:
            return IMailbox, SimpleMailbox(), lambda: None
        else:
            raise NotImplementedError()

portal = Portal(SimpleRealm())

checker = InMemoryUsernamePasswordDatabaseDontUse()
checker.addUser("guest", "password")
portal.registerChecker(checker)

application = service.Application("example pop3 server")

f = ServerFactory()
f.protocol = pop3.POP3
f.protocol.portal = portal
internet.TCPServer(1230, f).setServiceParent(application)



















