import mysmtplib as smtplib
import mypoplib as poplib
import datetime
from messagestore import ContactStore, MessageStore, SettingsStore, Base, Message, Contact, CleanedEmailAddress
from Crypto.PublicKey import RSA
from Crypto import Random
from json import JSONEncoder, JSONDecoder
from Crypto.Hash import SHA256
import base64
from ImmutableObject import ImmutableObject
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Boolean
import uuid
import json
import utils

#A demux is a class that deals with receiving data from the email and routing it to the correct place
class Demux(object):
    database_file_name = 'livewire.db'

    def __init__(self, fromfile, **kwargs):
        self.database_file_name = fromfile
        filename = self.get_database_filename()
        engine = create_engine('sqlite:///' + filename, echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.contactstore = ContactStore(self)
        self.messagestore = MessageStore(self)
        self.settingsstore = SettingsStore(self)

        self.myemail = self.settingsstore.LoadSetting('myemail')
        self.smtpserver = self.settingsstore.LoadSetting('smtpserver')
        self.smtpport = self.settingsstore.LoadSettingInt('smtpport')
        self.smtpuser = self.settingsstore.LoadSetting('smtpuser')
        self.smtppass = self.settingsstore.LoadSetting('smtppass')
        self.popserver = self.settingsstore.LoadSetting('popserver')
        self.popuser = self.settingsstore.LoadSetting('popuser')
        self.poppass = self.settingsstore.LoadSetting('poppass')
        self.popport = self.settingsstore.LoadSettingInt('popport')
        if self.settingsstore.LoadSetting('key') != "":
            self.key = RSA.importKey(self.settingsstore.LoadSetting('key'))

        self.Init_Setting('myemail', kwargs)
        self.Init_Setting('smtpserver', kwargs)
        self.Init_Setting('smtpport', kwargs)
        self.Init_Setting('smtpuser', kwargs)
        self.Init_Setting('smtppass', kwargs)
        self.Init_Setting('popserver', kwargs)
        self.Init_Setting('popuser', kwargs)
        self.Init_Setting('poppass', kwargs)
        self.Init_Setting('popport', kwargs)
        self.Init_Setting('popport', kwargs)
        if 'key' not in kwargs and hasattr(self, 'key') == False:
            random_generator = Random.new().read
            self.key = RSA.generate(1024, random_generator)
        elif hasattr(self, 'key') == False:
            self.key = kwargs['key']
        self.settingsstore.SaveSetting('key', self.key.exportKey("PEM"))

        self.registeredapps = dict()


    def Init_Setting(self, settingname, init_kwargs):
        if settingname in init_kwargs:
            setattr(self, settingname, init_kwargs[settingname])
            self.settingsstore.SaveSetting(settingname, init_kwargs[settingname])

    def get_database_filename(self):
        return self.database_file_name
    
    def ProcessMessage(self, s):
        pass

    def RegisterApp(self, app):
        self.registeredapps[app.__class__.__name__] = app

    def SendPlainEmail(self, receivers, subject, message):
        if subject == "Livewire encoded message":
            pass
            #print "message = ",message
            #assert False
        #print "SendPlainEmail subject = ",subject," message = ",message
        smtpObj = smtplib.SMTP_SSL(self.smtpserver, self.smtpport)
        prcoessedmessage = "From: <" + self.myemail + ">\n" 
        receivers = ",".join(["<" + r + ">" for r in receivers])
        prcoessedmessage += "To: " + receivers + " \n"
        prcoessedmessage += "Date: " + datetime.datetime.now().strftime("%c") + """
Subject: """ + subject + """

Content-Type: text/plain

""" + message + """

================
Livewire enabled emailer http://wwww.livewirecommunicator.org (""" + self.myemail + """)
================
        """
        smtpObj.sendmail(self.myemail, receivers, prcoessedmessage)         

    def GetNumMessages(self):
        M = poplib.POP3_SSL(self.popserver, self.popport)
        M.user(self.popuser)
        M.pass_("")
        numMessages = len(M.list()[1])
        totalMessages = 0
        for i in range(numMessages):
            messages = M.retr(i+1)[1]
            totalMessages += len(messages)
        M.quit()
        return totalMessages


    def CheckEmail(self):
        M = poplib.POP3_SSL(self.popserver, self.popport)
        M.user(self.popuser)
        M.pass_(self.poppass)
        numMessages = len(M.list()[1])
        #print "CheckEmail numMessages = ",numMessages
        public_key = None
        #print "numMessages = ",numMessages
        for i in range(numMessages):
            lines = M.retr(i+1)[1]
            
            headers = list()
            body = list()
            inheader = True
            #print "Starting message"
            for line in lines:
                #print "line=",line
                if line == "":
                    inheader = False
                elif inheader:
                    #print "headers.append "
                    headers.append(line)
                else:
                    #print "body.append "
                    body.append(line)

            isencodedmessage = False
            for line in headers:
                if line[:8] == "Subject:":
                    isencodedmessage = line == "Subject: Livewire encoded message"
                if line[:6] == "From: ":
                    k = line.find("<")
                    if k > 0:
                        fromemail = line[k + 1:]
                        k = fromemail.find(">")
                        assert k > 0 # "> not found")
                        fromemail = fromemail[:k]
                    else:
                        fromemail = line[6:]
            
            if isencodedmessage:
                inlivewirearea = False
                wasinlivewirearea = False
                wasinendlivewirearea = False
                message = []
                for line in body:
                    if line == self.begin_livewire:
                        inlivewirearea = True
                        wasinlivewirearea = True
                    elif line == self.end_livewire:
                        inlivewirearea = False
                        wasinendlivewirearea = True
                    elif inlivewirearea:
                        message.append(line)

                message = "".join(message)
                line = base64.b64decode(message)
                line = JSONDecoder().decode(line)
                assert len(line) == 2 #"Message is not an iterable of length two") 
                l = line[0]
                sig = long(line[1])
                l2 = JSONDecoder().decode(l)
                assert len(l2) == 2 # "Message is not an iterable of length two"
                assert l2[0] == "XR1"# "Protocol version incorrect"
                d = l2[1]
                assert isinstance(d, dict) # "d must be a dict"
                if d["class"] == "identity": #An identity message identifies the other sender: Ie gives us their public key
                    utils.log_output("Receive identity message from ", d["email"])
                    assert len(d) == 4 #"d must contain 4 elements")
                    assert d["email"] == fromemail # "Source email must match the message")
                    public_key = RSA.importKey(d["key"])
                    
                    hash = SHA256.new(l).digest()
                    verified = public_key.verify(hash, (sig, ))
                    assert verified # "Signature not verified"
                        
                    l = [c for c in self.contactstore.GetContacts() if CleanedEmailAddress(c.emailaddress) == CleanedEmailAddress(fromemail)]
                    if len(l) == 0:
                        contact = Contact()
                        contact.name = d["email"]
                        assert fromemail[0] != '<'
                        assert fromemail[-1] != '>'
                        contact.emailaddress = fromemail
                        contact.publickey = d["key"]
                        contact.islivewire = True
                        self.contactstore.AddContact(contact)
                        #print "CheckEmail contact.public_key ",contact.publickey
                        utils.log_output("Sending confirmation email to ", d["email"])
                        self.SendConfirmationEmail(contact)
                    else:
                        contact = l[0]
                        if contact.publickey != '' and not self.is_verified(fromemail, l, sig):
                            return #Silently ignore unverified attempts to change keys
                        contact.publickey = d["key"]
                        contact.islivewire = True
                elif d["class"] == "createdocumentcollection": #An identity message identifies the other sender: Ie gives us their public key
                    if not self.is_verified(fromemail, l, sig):
                        return #Silently ignore unverified messages
                    dc = self.registeredapps[d["appname"]].CreateNewDocumentCollection(d["dcid"])
                    dc.LoadFromJSON(d["dcjson"])
                elif d["class"] == "edges": #Some edges we should apply
                    if not self.is_verified(fromemail, l, sig):
                        return #Silently ignore unverified edges
                    dc = self.registeredapps[d["appname"]].GetDocumentCollectionByID(d["dcid"])
                    dc.LoadFromJSON(d["edges"])
                elif d["class"] == "immutableobject": #immutableobject to create
                    if not self.is_verified(fromemail, l, sig):
                        return #Silently ignore unverified messages
                    dc = self.registeredapps[d["appname"]].GetDocumentCollectionByID(d["dcid"])
                    d2 = d["immutableobject"]
                    classname = d2["classname"]
                    theclass = dc.classes[classname]
                    assert issubclass(theclass, ImmutableObject)
                
                    thehash = d2["hash"]
                    del d2["classname"]
                    del d2["hash"]

                    io = theclass(**d2)
                    if io.GetHash() not in dc.objects[classname]:
                        dc.objects[classname][io.GetHash()] = io
                else:
                    assert False #Message type not implemented yet
            else:
                lines = [line for line in lines if line != "Content-Type: text/plain"]
                rawmessage = '\n'.join(lines)
                message2 = Message.fromrawbody(rawmessage)
                assert message2.fromaddress != ""
                self.messagestore.AddMessage(message2, None)
                self.ProcessBodyLivewireMessages(message2)
                l = [c for c in self.contactstore.GetContacts() if c.emailaddress == message2.fromaddress]

                send_confirmation_email = False
                if len(l) == 0:
                    contact = Contact()
                    contact.name = message2.fromaddress
                    assert message2.fromaddress[0] != '<'
                    assert message2.fromaddress[-1] != '>'
                    contact.emailaddress = message2.fromaddress
                    contact.islivewire = message2.senderislivewireenabled
                    self.contactstore.append(contact)
                    send_confirmation_email = contact.islivewire
                elif len(l) == 1:
                    if message2.senderislivewireenabled == True:
                        contact = l[0]
                        contact.islivewire = True
                        send_confirmation_email = True
                else:
                    assert False
                
                if send_confirmation_email:
                    self.SendConfirmationEmail(contact)
        M.dele(1)
        M.quit()

    def is_verified(self, fromemail, l, sig):
        contacts = [c for c in self.contactstore.GetContacts() if CleanedEmailAddress(c.emailaddress) == CleanedEmailAddress(fromemail)]
        if len(contacts) != 1:
            assert False
            return False
        contact = contacts[0]
        public_key = RSA.importKey(contact.publickey)
        hash = SHA256.new(l).digest()
        return public_key.verify(hash, (sig, ))

    begin_livewire = "-----BEGIN-LIVEWIRE-ENCODED-MESSAGE--------"
    end_livewire   = "-----END-LIVEWIRE-ENCODED-MESSAGE----------"

    def SendConfirmationEmail(self, contact):
        sender = self.myemail
        emailaddress = CleanedEmailAddress(contact.emailaddress)
        assert emailaddress[0] != '<'
        assert emailaddress[-1] != '>'
        assert emailaddress != ''
        receivers = [emailaddress]

        public_key = self.key.publickey().exportKey("PEM")        
    
        utils.log_output("Sending identitfy message to ", emailaddress)
        message = self.GetEncodedMessage({"id":str(uuid.uuid4()),"class":"identity","email": sender,"key":public_key})

        self.SendPlainEmail(receivers, "Livewire encoded message", message)

    def GetEncodedMessage(self, d):
        message = "\n\n" + self.begin_livewire + "\n"

        l = ["XR1", d]
        l = JSONEncoder().encode(l)
        hash = SHA256.new(l).digest()
        signature = self.key.sign(hash, '')
        l2 = [l, str(signature[0])]
        l2 = JSONEncoder().encode(l2)
        line = base64.b64encode(l2)
        n = 30
        lines = [line[i:i+n] for i in range(0, len(line), n)]
        message += '\n'.join(lines) + "\n"
        message += self.end_livewire + "\n\n"
        #print "SendConformEmail message = ",message

        #message += "=================================================\n"
        #message += "Livewire enabled emailer http://wwww.livewirecommunicator.org (" + self.myemail + ")\n"
        #message += "=================================================\n"

        return message
    def ProcessBodyLivewireMessages(self, message):
        #print "ProcessBodyLivewireMessages called"
        body = message.body

        k = body.find(self.begin_livewire)
        #print "body = ",body
        if k < 0:
            return
        #print "ProcessBodyLivewireMessages 1"
        body = body[k + len(self.begin_livewire)]

        k = body.find(self.end_livewire)
        assert k >= 0

        body = body[:k]

        json = base64.b64decode(body)

        print "ProcessBodyLivewireMessages json",json


        l2 = JSONEncoder().decode(json)

        assert l2[0] == "XR1"

        d = l2[1]

        assert d["class"] == "identity"
        messageid = d["id"]
        sender = d["email"]
        public_key = d["key"]
        
        l = [c for c in self.contactstore if c.email == sender]
        assert len(l) == 1

        for c in l:
            #print "public_key = ",public_key
            c.publickey = public_key
            s.save()







