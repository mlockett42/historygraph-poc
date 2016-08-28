# Message store is a collection of all of our
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from email.parser import Parser
from sqlalchemy.types import Boolean
import re
from dateutil import parser
	
#An email message
import uuid
import time
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import datetime

Base = declarative_base()

#message object
class Message(Base):
    __tablename__ = 'messages'

    id = Column(String, primary_key=True)
    body = Column(String)
    subject = Column(String)
    fromaddress = Column(String)
    datetime = Column(DateTime)
    senderislivewireenabled = Column(Boolean)

    addresses = relationship("Address", order_by="Address.id", backref="messages")
    tags = relationship("Tag", order_by="Tag.id", backref="messages")
    
    def __init__(self):
        self.id = str(uuid.uuid1())
        #self.direction = "None"
        #self.to = list()
        self.fromaddress = ""
        #self.replyto = list()
        #self.cc = list()
        #self.bcc = list()
        self.body = ""
        self.subject = ""
        self.datetime = datetime.datetime.now()
        self.senderislivewireenabled = False

    @staticmethod
    def fromrawbody(rawbody):
        emailmsg = Parser().parsestr(rawbody)
        ret = Message()
        ret.subject = emailmsg["subject"]
        ret.fromaddress = emailmsg["From"]
        toaddress = Address()
        toaddress.email_address = emailmsg["to"]
        toaddress.message_id = ret.id
        toaddress.addresstype = "To"
        ret.addresses.append(toaddress)
        ret.datetime = parser.parse(emailmsg["Date"])
        if emailmsg.is_multipart() == False:
            ret.body = emailmsg.get_payload()
        else:
            for part in emailmsg.walk():
                if part.get_content_type() == "text/plain":
                    ret.body = part.get_payload()
        lines = ret.body.split("\n")
        foundfirstsigline = False
        foundsecondsigline = False
        foundthirdsigline = False
        for line in lines:
            if line[:2] != "--":
                if foundfirstsigline == False and foundsecondsigline == False \
                    and foundthirdsigline == False:
                    if re.match("^=+$", line) is not None:
                        foundfirstsigline = True
                elif foundfirstsigline == True and foundsecondsigline == False \
                    and foundthirdsigline == False:
                    if re.match("^Livewire enabled emailer http://wwww.livewirecommunicator.org \([a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\)$", line):
                        foundsecondsigline = True
                    else:
                        foundfirstsigline = False
                elif foundfirstsigline == True and foundsecondsigline == True \
                    and foundthirdsigline == False:
                    if re.match("^=+$", line) is not None:
                        ret.senderislivewireenabled = True
                    foundfirstsigline = False
                    foundsecondsigline = False
        return ret

class Address(Base):
        __tablename__ = 'addresses'
        id = Column(String, primary_key=True)
        email_address = Column(String, nullable=False)
        message_id = Column(String, ForeignKey('messages.id'))
        addresstype = Column(String, nullable=False) #Can be To, CC or BCC
   
        #message = relationship("Message", backref=backref('addresses', order_by=id))
   
        def __init__(self):
            self.id = str(uuid.uuid1())
            
        def __repr__(self):
            return "<Address(email_address='%s')>" % self.email_address

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(String, primary_key=True)
    name = Column(String)
    emailaddress = Column(String)
    islivewire = Column(Boolean)
    publickey = Column(String)


    def __init__(self):
        self.id = str(uuid.uuid1())
        self.name = ""
        self.emailaddress = ""
        self.islivewire = False
        self.publickey = ""

def CleanedEmailAddress(emailaddress):
    i = emailaddress.find('<')
    if i == -1:
        return emailaddress
    j = emailaddress.find('>')
    if j <= i:
        return emailaddress
    return emailaddress[i+1:j]

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(String, primary_key=True)
    tagname = Column(String)
    message_id = Column(String, ForeignKey('messages.id'))

    def __init__(self):
        self.id = str(uuid.uuid1())
        self.tagname = ""

class ContactStore:
    def GetContactsByFilter(self, filter):
        return filter.applyFilter(self.demux.session).all()

    def AddContact(self, contact):
        self.demux.session.add(contact)
        self.demux.session.commit()

    def GetContacts(self):
        #Return all contacts unfiltered
        return self.demux.session.query(Contact)

    def GetContactsByEmailAddress(self, emailaddress):
        return self.demux.session.query(Contact).filter(Contact.emailaddress.like(emailaddress))

    def __init__(self, demux):
        self.demux = demux

class MessageStore:
    def GetMessagesByFilter(self, filter):
        return sorted(filter.applyFilter(self.demux.session), key=lambda message: message.datetime)

    def AddMessage(self, message, makelivewirehandler):
        self.demux.session.add(message)
        self.demux.session.commit()

        l = self.demux.contactstore.GetContactsByEmailAddress(message.fromaddress)

        if l.count() == 0:
            contact = Contact()
            contact.name = message.fromaddress
            contact.emailaddress = message.fromaddress
            contact.islivewire = message.senderislivewireenabled
            self.demux.contactstore.AddContact(contact)
            if makelivewirehandler:
                makelivewirehandler(contact)
        elif l.count() == 1:
            if message.senderislivewireenabled == True:
                contact = l.first()
                contact.islivewire = True
                self.demux.contactstore.AddContact(contact)
                if makelivewirehandler:
                    makelivewirehandler(contact)
        else:
            assert False

    def GetMessages(self):
        #Return all messages unfiltered
        return self.demux.session.query(Message)

    def __init__(self, demux):
        self.demux = demux

#message object
class Setting(Base):
    __tablename__ = 'settings'

    name = Column(String, primary_key=True)
    value = Column(String)
    
    def __init__(self):
        self.name = ""
        self.value = ""

class SettingsStore:
    def AddSetting(self, setting):
        self.demux.session.add(setting)
        self.demux.session.commit()

    def GetSetting(self, searchname):
        l = self.demux.session.query(Setting).filter(Setting.name == searchname)
        if l.count > 0:
            return l.first()
        else:
            return None

    def SaveSetting(self, name, value):
        setting = self.GetSetting(name)
        if setting == None:
            setting = Setting()
        setting.name = name
        setting.value = value
        self.AddSetting(setting)

    def LoadSetting(self, name):
        setting = self.GetSetting(name)
        if setting == None:
            return ""
        else:
            return setting.value

    def LoadSettingInt(self, name):
        setting = self.GetSetting(name)
        if setting == None:
            return 0
        else:
            return int(setting.value)

    def __init__(self, demux):
        self.demux = demux




