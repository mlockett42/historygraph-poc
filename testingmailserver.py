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
deletedmessages = None

class DictMessageWriter(object):
    implements(smtp.IMessage)

    def __init__(self, username):
        self.username = username.local
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        # message is complete, store it
        self.lines.append('') # add a trailing newline
        messageData = '\n'.join(self.lines)
        #print "eomReceived messageData = ",messageData
        global mailDict
        mailDict[self.username].append(messageData)
        #print "eomReceived mailDict[self.username] = ",mailDict[self.username]
        return defer.succeed(None)

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
        return lambda: DictMessageWriter(user.dest)

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




















#Twisted pop3 client to merge in with the SMTP server above
#From http://www.siafoo.net/snippet/331
# Copyright (c) 2010 David Isaacson <david@icapsid.net>
# Portions from 'twimapd' copyright (c) 2010 Dav Glass <davglass@gmail.com>
# New BSD License

import StringIO
from md5 import md5
from twisted.cred import checkers, credentials, portal
from twisted.cred.error import *
from twisted.internet import defer, reactor, protocol
from twisted.mail import pop3
from zope.interface import implements

def authenticate(username, password):
    if username not in validMailnames:
        return False
    if validMailnames[username] == password:
        return username
    else:
        return False

class WallMailbox(object):
    ''' an avatar representing a per-user mailbox '''
    
    implements(pop3.IMailbox)
    
    def __init__(self,id,cache):
        self.id = id
        self.cache = cache
        global deletedmessages
        deletedmessages = []
    
    def listMessages(self, i=None):
        global mailDict
        if i is None:
            return [self.listMessages(i) for i in range(len(mailDict[self.id]))]
        elif i >= len(mailDict[self.id]):
            raise ValueError
        return len(mailDict[self.id])
    
    def getMessage(self, i):
        global mailDict
        if i >= len(mailDict[self.id]):
            raise ValueError
        #print "getMessage mailDict[self.id] = ",mailDict[self.id]
        s = mailDict[self.id][i]
        #print "getMessage s = ",s
        return StringIO.StringIO(s)
    
    def getUidl(self, i):
        global mailDict
        if i >= len(mailDict[self.id]):
            raise ValueError
        return md5(mailDict[self.id][i]).hexdigest()
    
    def deleteMessage(self,i):
        #Not quite correct these deletion should only be carried out when quitting
        global deletedmessages
        deletedmessages.append((self.id,i))
        #print 'Add message ' + str(i) + ' to delete queue id = ' + self.id
    
    def undeleteMessage(self):
        pass
    
    def sync(self):
        global mailDict
        global deletedmessages
        messages_to_delete = list()
        for (id, i) in deletedmessages:
            if i < len(mailDict[id]):
                messages_to_delete.append(mailDict[id][i])
                #print 'Prepare delete message ' + str(i) + ' from delete queue id = ' + self.id

        for message_to_delete in messages_to_delete:
            #print 'Deleting message'
            mailDict[id].remove(message_to_delete)

class WallCredentialsChecker(object):
    
    ''' authentication: given credentials, returns an avatar id (a reference to a
        particular user and possibly their mailbox)'''

    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    def __init__(self, cache):
        self.cache = cache

    def requestAvatarId(self, creds):
        # do authentication here with creds.username, creds.password
        user_id = authenticate(creds.username, creds.password)
        if not user_id:
             return defer.fail(UnauthorizedLogin("Bad username or password"))
        return defer.succeed(user_id)

class WallUserRealm(object):
    ''' given an interface (type of avatar) and an avatar id (a reference to a user),
        returns the correct sort of avatar for the correct user'''
    
    implements(portal.IRealm)
    avatarInterfaces = {
        pop3.IMailbox: WallMailbox,
    }

    def __init__(self, cache):
        self.cache = cache

    def requestAvatar(self, avatarId, mind, *interfaces):
        for requestedInterface in interfaces:
            if self.avatarInterfaces.has_key(requestedInterface):
                # return an instance of the correct class
                avatarClass = self.avatarInterfaces[requestedInterface]
                avatar = avatarClass(avatarId, self.cache)
                # null logout function: take no arguments and do nothing
                logout = lambda: None
                return defer.succeed((requestedInterface, avatar, logout))

            # none of the requested interfaces was supported
        raise KeyError("None of the requested interfaces is supported")
    

class POP3Debug(pop3.POP3):
    ''' the server '''
    
    def connectionMade(self):
        return pop3.POP3.connectionMade(self)
    
    
class POP3Factory(protocol.Factory):
    ''' creates and initializes the server '''
    
    protocol = POP3Debug
    portal = None # placeholder

    def buildProtocol(self, address):
        p = self.protocol()
        p.portal = self.portal
        p.factory = self
        return p

class ObjCache(object):
    def __init__(self):
        self.cache = {}

    def get(self, item):
        return self.cache[item]

    def set(self, item, value):
        self.cache[item] = value














#Because we are not running full async in the server is run in a seperate tread

def StartTestingMailServer(domain, mailnames):
    #This function starts the mail server reactor up in a seperate thread
    #domain = the internet domain to accept mail for a serve mail for
    #mailnames = a dict of allowed mail names and passwords. k = mail name, v = password
    #only one email server can be run inside our program at a time because the reactor is a global variable
    global validDomain
    global validMailnames
    global mailDict
    #Set up the SMTP server
    validDomain = domain
    validMailnames = mailnames
    mailDict = defaultdict(list)
    reactor.listenTCP(10025, SMTPFactory())

    #Setup up the POP server
    cache = ObjCache() #just a simple way to have 'global' variables for now

    portal1 = portal.Portal(WallUserRealm(cache))
    portal1.registerChecker(WallCredentialsChecker(cache))

    factory = POP3Factory()
    factory.portal = portal1

    reactor.listenTCP(10026, factory)

    from twisted.internet import ssl
    # SSL stuff here... and certificates...
    thread = Thread(target=reactor.run, args=(False,))
    thread.daemon=True
    thread.start()

def StopTestingMailServer():
    reactor.callFromThread(reactor.stop)

def ResetMailDict():
    assert False
    global mailDict
    mailDict = defaultdict(list)
    global deletedmessages
    deletedmessages = []

def GetEmailCountByAccount(accountname):
    global mailDict
    #Warning this is not exactly thread staff
    return len(mailDict[accountname])


def GetTotalEmailCount():
    global mailDict
    #Warning this is not exactly thread staff
    return sum([len(mailDict[accountname]) for accountname in mailDict])


