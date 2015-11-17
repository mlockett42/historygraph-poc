import sys
sys.path.insert(0, '/home/mark/code/livewirepy/doop')

import unittest
from Document import Document
from FieldInt import FieldInt
from DocumentObject import DocumentObject
from FieldList import FieldList
import uuid
from FieldText import FieldText
import DocumentCollection
from messagefilterdatetime import MessageFilterDateTime
from messagefiltersubject import MessageFilterSubject
from messagefilterbody import MessageFilterBody
from messagefilterand import MessageFilterAnd
from messagefilteror import MessageFilterOr
import datetime
from messagefilterfromaddress import MessageFilterFromAddress
from messagefiltertoaddress import MessageFilterByToAddress
from messagefilterccaddress import MessageFilterByCCAddress
from messagefilterbccaddress import MessageFilterByBCCAddress
from messagefiltertag import MessageFilterByTag
import mockpoplib
import mocksmtplib
from email.mime.text import MIMEText
from contactfilteremailaddress import ContactFilterEmailAddress
from messagestore import *

class Covers(Document):
    def __init__(self, id):
        super(Covers, self).__init__(id)
    covers = FieldInt()

class SimpleCoversTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        #Test merging together simple covers documents
        test = Covers(None)
        test.covers = 1
        #Test we can set a value
        self.assertEqual(test.covers, 1)
        test2 = Covers(test.id)
        test.history.Replay(test2)
        #Test we can rebuild a simple object by playing an edge
        self.assertEqual(test2.covers, 1)
        #Test these are just the same history object but it was actually copied
        assert test.history is not test2.history
        
        test3 = test2.Clone()
        #Test the clone is the same as the original. But not just refering to the same object
        self.assertEqual(test3.covers, test2.covers)
        assert test2 is not test3
        assert test2.history is not test3.history
        
        test = Covers(None)
        test.covers = 1
        test.covers = 2
        test2 = Covers(test.id)
        test.history.Replay(test2)
        self.assertEqual(test.covers, 2)
        assert test.history is not test2.history
        assert test is not test2
    
class MergeHistoryCoverTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        #Test merge together two simple covers objects
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        test.covers = 2
        test2.covers = 3
        test3 = test.Merge(test2)
        #In a merge conflict between two integers the greater one is the winner
        self.assertEqual(test3.covers, 3)

class TestPropertyOwner2(DocumentObject):
    cover = FieldInt()
    quantity = FieldInt()

class TestPropertyOwner1(Document):
    covers = FieldInt()
    propertyowner2s = FieldList(TestPropertyOwner2)
    def WasChanged(self, changetype, propertyowner, propertyname, propertyvalue, propertytype):
        super(TestPropertyOwner1, self).WasChanged(changetype, propertyowner, propertyname, propertyvalue, propertytype)
        self.bWasChanged = True

class ListItemChangeHistoryTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        #Test that various types of changes create was changed events
        test1 = TestPropertyOwner1(None)
        test1.bWasChanged = False
        test2 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(test2)
        self.assertTrue(test1.bWasChanged)
        test1.bWasChanged = False
        test2.cover = 1
        self.assertTrue(test1.bWasChanged)
        test1.bWasChanged = False
        test2.cover = 1
        self.assertTrue(test1.bWasChanged)
        test1.propertyowner2s.remove(test2.id)
        self.assertEqual(len(test1.propertyowner2s), 0)

class SimpleItemTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        test1 = TestPropertyOwner1(None)
        testitem = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem)
        testitem.cover = 1
        #Test semantics for retriving objects
        self.assertEqual(len(test1.propertyowner2s), 1)
        for po2 in test1.propertyowner2s:
            self.assertEqual(po2.__class__.__name__ , TestPropertyOwner2.__name__)
            self.assertEqual(po2.cover, 1)

        test1 = TestPropertyOwner1(None)
        testitem = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem)
        testitem.cover = 1
        test1.propertyowner2s.remove(testitem.id)

        test2 = TestPropertyOwner1(test1.id)
        test1.history.Replay(test2)

        #Check that replaying correctly removes the object
        self.assertEqual(len(test2.propertyowner2s), 0)

        test1 = TestPropertyOwner1(None)
        testitem = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem)
        testitem.cover = 1
        test2 = test1.Clone()
        
        self.assertEqual(len(test2.propertyowner2s), 1)
        for po2 in test2.propertyowner2s:
            self.assertEqual(po2.__class__.__name__, TestPropertyOwner2.__name__)
            self.assertEqual(po2.cover, 1)

class AdvancedItemTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        #Test changing them deleting a sub element
        test1 = TestPropertyOwner1(None)
        testitem1 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem1)
        testitem1.cover = 1
        test2 = test1.Clone()
        testitem2 = test2.GetDocumentObject(testitem1.id)
        testitem2.cover = 2
        test2.propertyowner2s.remove(testitem2.id)
        test3 = test1.Merge(test2)
        self.assertEqual(len(test3.propertyowner2s), 0)

        #Test changing them deleting a sub element. Test merging in the opposition order to previous test
        test1 = TestPropertyOwner1(None)
        testitem1 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem1)
        testitem1.cover = 1
        test2 = test1.Clone()
        testitem2 = test2.GetDocumentObject(testitem1.id)
        testitem2.cover = 2
        test2.propertyowner2s.remove(testitem2.id)
        test3 = test2.Merge(test1)
        self.assertEqual(len(test3.propertyowner2s), 0)

        #Test merging changes to different objects in the same document works
        test1 = TestPropertyOwner1(None)
        testitem1 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem1)
        test2 = test1.Clone()
        testitem1.cover = 3
        test2.covers=2
        test3 = test2.Merge(test1)
        self.assertEqual(len(test3.propertyowner2s), 1)
        for item1 in test3.propertyowner2s:
            self.assertEqual(item1.cover, 3)
        self.assertEqual(test3.covers, 2)

        #Test changing different objects on different branches works
        test1 = TestPropertyOwner1(None)
        testitem1 = TestPropertyOwner2(None)
        id1 = testitem1.id
        test1.propertyowner2s.add(testitem1)
        testitem2 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem2)
        id2 = testitem2.id
        test2 = test1.Clone()
        testitem2 = test2.GetDocumentObject(id2)
        testitem1.cover = 2
        testitem1.quantity = 3
        testitem2.cover = 3
        testitem2.quantity = 2
        test3 = test2.Merge(test1)
        testitem1 = test3.GetDocumentObject(id1)
        testitem2 = test3.GetDocumentObject(id2)
        self.assertEqual(testitem2.cover, 3)
        self.assertEqual(testitem2.quantity, 2)
        self.assertEqual(testitem1.cover, 2)
        self.assertEqual(testitem1.quantity, 3)
        
        #Test changing different objects on different branches works reverse merge of above
        test1 = TestPropertyOwner1(None)
        testitem1 = TestPropertyOwner2(None)
        id1 = testitem1.id
        test1.propertyowner2s.add(testitem1)
        testitem2 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem2)
        id2 = testitem2.id
        test2 = test1.Clone()
        testitem2 = test2.GetDocumentObject(id2)
        testitem1.cover = 2
        testitem1.quantity = 3
        testitem2.cover = 3
        testitem2.quantity = 2
        test3 = test1.Merge(test2)
        testitem1 = test3.GetDocumentObject(id1)
        testitem2 = test3.GetDocumentObject(id2)
        self.assertEqual(testitem2.cover, 3)
        self.assertEqual(testitem2.quantity, 2)
        self.assertEqual(testitem1.cover, 2)
        self.assertEqual(testitem1.quantity, 3)
    
class Comments(Document):
    def __init__(self, id):
        super(Comments, self).__init__(id)
    comment = FieldText()

class MergeHistoryCommentTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        #Test merge together two simple covers objects
        test = Comments(None)
        test.comment = "AAA"
        test2 = test.Clone()
        test.comment = "BBB"
        test2.comment = "CCC"
        test3 = test.Merge(test2)
        #In a merge conflict between two string the one that is sooner in alphabetical order is the winner
        self.assertEqual(test3.comment, "CCC")

        #Test merge together two simple covers objects
        test = Comments(None)
        test.comment = "AAA"
        test2 = test.Clone()
        test.comment = "CCC"
        test2.comment = "BBB"
        test3 = test.Merge(test2)
        #In a merge conflict between two string the one that is sooner in alphabetical order is the winner
        self.assertEqual(test3.comment, "CCC")

class StoreObjectsInDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

        #Test writing the history to a sql lite database
        test1 = TestPropertyOwner1(None)
        test1id = test1.id
        testitem1 = TestPropertyOwner2(None)
        testitem1id = testitem1.id
        test1.propertyowner2s.add(testitem1)
        test2 = test1.Clone()
        testitem1.cover = 3
        test2.covers=2        
        self.assertEqual(len(test1.propertyowner2s), 1)

        test3 = test2.Merge(test1)
        self.assertEqual(len(test3.propertyowner2s), 1)
        for item1 in test3.propertyowner2s:
            self.assertEqual(item1.cover, 3)
        self.assertEqual(test3.covers, 2)
        DocumentCollection.documentcollection.AddDocumentObject(test3)

        test1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)

        DocumentCollection.documentcollection.Save('test.history.db', 'test.content.db')

        matches = DocumentCollection.documentcollection.GetSQLObjects("SELECT id FROM TestPropertyOwner1 WHERE covers > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, TestPropertyOwner1)
        self.assertEqual(matches[0].id, test1id)
        matches = DocumentCollection.documentcollection.GetSQLObjects("SELECT id FROM TestPropertyOwner1 WHERE covers > 5")
        self.assertEqual(len(matches), 0)

        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

        DocumentCollection.documentcollection.Load('test.history.db', 'test.content.db')
        test1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        test1id = test1.id
        self.assertEqual(len(test1.propertyowner2s), 1)
        for testitem1 in test3.propertyowner2s:
            self.assertEqual(testitem1id, testitem1.id)
            self.assertEqual(testitem1.cover, 3)
        self.assertEqual(test1.covers, 2)

        matches = DocumentCollection.documentcollection.GetSQLObjects("SELECT id FROM TestPropertyOwner1 WHERE covers > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, TestPropertyOwner1)
        self.assertEqual(matches[0].id, test1id)
        matches = DocumentCollection.documentcollection.GetSQLObjects("SELECT id FROM TestPropertyOwner1 WHERE covers > 5")
        self.assertEqual(len(matches), 0)
    
class StoreObjectsInJSONTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

        #Test writing the history to a sql lite database
        test1 = TestPropertyOwner1(None)
        test1id = test1.id
        testitem1 = TestPropertyOwner2(None)
        testitem1id = testitem1.id
        test1.propertyowner2s.add(testitem1)
        test2 = test1.Clone()
        testitem1.cover = 3
        test2.covers=2        
        self.assertEqual(len(test1.propertyowner2s), 1)

        test3 = test2.Merge(test1)
        self.assertEqual(len(test3.propertyowner2s), 1)
        for item1 in test3.propertyowner2s:
            self.assertEqual(item1.cover, 3)
        self.assertEqual(test3.covers, 2)
        DocumentCollection.documentcollection.AddDocumentObject(test3)

        test1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)

        jsontext = DocumentCollection.documentcollection.asJSON()
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)
        DocumentCollection.documentcollection.LoadFromJSON(jsontext)
        test1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        test1id = test1.id
        self.assertEqual(len(test1.propertyowner2s), 1)
        for testitem1 in test3.propertyowner2s:
            self.assertEqual(testitem1id, testitem1.id)
            self.assertEqual(testitem1.cover, 3)
        self.assertEqual(test1.covers, 2)
    
class MergeChangesMadeInJSONTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()

    def runTest(self):
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

        #Create an object and set some values
        test1 = TestPropertyOwner1(None)
        test1id = test1.id
        testitem1 = TestPropertyOwner2(None)
        testitem1id = testitem1.id
        test1.propertyowner2s.add(testitem1)
        testitem1.cover = 3
        test1.covers=2        

        DocumentCollection.documentcollection.AddDocumentObject(test1)

        #Simulate sending the object to another user via conversion to JSON and emailing
        jsontext = DocumentCollection.documentcollection.asJSON()

        #Make some local changes
        test1.covers = 4

        #Simulate the other user (who received the email with the edges) getting the document and loading it into memory
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)
        DocumentCollection.documentcollection.LoadFromJSON(jsontext)
        tpo1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(tpo1s), 1)
        test2 = tpo1s[0]

        self.assertEqual(len(test2.propertyowner2s), 1)

        #The second user makes some changes and sends them back to the first
        for testitem2 in test2.propertyowner2s:
            testitem2.cover = 4

        test2.covers = 3
        
        jsontext = DocumentCollection.documentcollection.asJSON()
        
        #Simulate the first user received the second users changes
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)
        DocumentCollection.documentcollection.LoadFromJSON(jsontext)
        test2s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)
         
        #The first user merges the changes back with his own
        test3 = test2.Merge(test1)
        self.assertEqual(len(test3.propertyowner2s), 1)
        for testitem3 in test3.propertyowner2s:
            self.assertEqual(testitem3.cover, 4)
        self.assertEqual(test3.covers, 4)

    
class AddMessageToMessageStoreTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message = Message()
        message.fromaddress = "Mark_Lockett@hotmail.com"
        message.datetime = datetime.datetime(2013,10,31,12,0,0)
        GetGlobalMessageStore().AddMessage(message)

        assert GetGlobalMessageStore().GetMessages().count() == 1, "Not one message in messagestore"
        assert GetGlobalMessageStore().GetMessages().first().id == message.id, "Message id's don't match"
        assert GetGlobalContactStore().GetContacts().count() == 1, "Not one contact in contactstore"
        assert GetGlobalContactStore().GetContacts().first().emailaddress == message.fromaddress, "Contact email address not correct"

class FilterByDateTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.datetime = datetime.datetime(2013,11,1,12,0,0)
        message3 = Message()
        message3.datetime = datetime.datetime(2013,10,30,12,0,0)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)
        GetGlobalMessageStore().AddMessage(message3)

        f = MessageFilterDateTime(datetime.datetime(2013,10,31,0,0,0), datetime.datetime(2013,10,31,23,59,59))
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"

class FilterBySubjectCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.subject = "Hello1"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.subject = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message3 = Message()
        message3.subject = "Hello3"
        message3.datetime = datetime.datetime(2013,10,31,12,0,0)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)
        GetGlobalMessageStore().AddMessage(message3)

        f = MessageFilterSubject("Hello2")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message2.id, "Message id's don't match"

class FilterByBodyCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.body = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message3 = Message()
        message3.body = "Hello3"
        message3.datetime = datetime.datetime(2013,10,31,12,0,0)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)
        GetGlobalMessageStore().AddMessage(message3)

        f = MessageFilterBody("Hello2")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message2.id, "Message id's don't match"

class FilterAndCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        message1.subject = "blarg"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.body = "Hello2"
        message2.subject = "blarg"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message3 = Message()
        message3.body = "Hello3"
        message3.subject = "blarg"
        message3.datetime = datetime.datetime(2013,10,31,12,0,0)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)
        GetGlobalMessageStore().AddMessage(message3)

        f1 = MessageFilterBody("Hello2")
        f2 = MessageFilterSubject("blarg")
        f = MessageFilterAnd(f1, f2)
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message2.id, "Message id's don't match"

class FilterOrCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        message1.subject = "blarg1"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.body = "Hello2"
        message2.subject = "blarg2"
        message2.datetime = datetime.datetime(2013,11,1,12,0,0)
        message3 = Message()
        message3.body = "Hello3"
        message3.subject = "blarg3"
        message3.datetime = datetime.datetime(2013,1,2,12,0,0)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)
        GetGlobalMessageStore().AddMessage(message3)

        f1 = MessageFilterBody("Hello2")
        f2 = MessageFilterSubject("blarg1")
        f = MessageFilterOr(f1, f2)
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 2, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"
        assert l[1].id == message2.id, "Message id's don't match"

class FilterByFromAddressCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()
        
    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        message1.fromaddress = "mlockett@bigpond.com"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.body = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2.fromaddress = "no-one@example.com"
        message3 = Message()
        message3.body = "Hello3"
        message3.datetime = datetime.datetime(2013,10,31,12,0,0)
        message3.fromaddress = "hello@example.com"
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)
        GetGlobalMessageStore().AddMessage(message3)

        f = MessageFilterFromAddress("mlockett@bigpond.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"
        
class FilterByToAddressCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        addr1 = Address()
        addr1.email_address = "Mark_Lockett@hotmail.com"
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        message1.fromaddress = "mlockett@bigpond.com"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message1.addresses.append(addr1)
        message2 = Message()
        message2.body = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2.fromaddress = "no-one@example.com"
        addr2 = Address()
        addr2.email_address = "goblin@example.com"
        addr2.message_id = message2.id
        addr2.addresstype = "To"
        message2.addresses.append(addr2)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)

        f = MessageFilterByToAddress("Mark_Lockett@hotmail.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"
        
class FilterByCCAddressCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        addr1 = Address()
        addr1.email_address = "Mark_Lockett@hotmail.com"
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        addr3 = Address()
        addr3.email_address = "cc1@example.com"
        addr3.message_id = message1.id
        addr3.addresstype = "CC"
        message1.fromaddress = "mlockett@bigpond.com"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message1.addresses.append(addr1)
        message1.addresses.append(addr3)
        message2 = Message()
        message2.body = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2.fromaddress = "no-one@example.com"
        addr2 = Address()
        addr2.email_address = "goblin@example.com"
        addr2.message_id = message2.id
        addr2.addresstype = "To"
        message2.addresses.append(addr2)
        addr4 = Address()
        addr4.email_address = "tornado@example.com"
        addr4.message_id = message2.id
        addr4.addresstype = "CC"
        message2.addresses.append(addr4)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)

        f = MessageFilterByCCAddress("cc1@example.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"

        f = MessageFilterByCCAddress("goblin@example.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 0, "Not zero messages in messagestore"

class FilterByBCCAddressCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        addr1 = Address()
        addr1.email_address = "Mark_Lockett@hotmail.com"
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        addr3 = Address()
        addr3.email_address = "cc1@example.com"
        addr3.message_id = message1.id
        addr3.addresstype = "CC"
        addr5 = Address()
        addr5.email_address = "bcc1@example.com"
        addr5.message_id = message1.id
        addr5.addresstype = "BCC"
        message1.fromaddress = "mlockett@bigpond.com"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message1.addresses.append(addr1)
        message1.addresses.append(addr3)
        message1.addresses.append(addr5)
        message2 = Message()
        message2.body = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2.fromaddress = "no-one@example.com"
        addr2 = Address()
        addr2.email_address = "goblin@example.com"
        addr2.message_id = message2.id
        addr2.addresstype = "To"
        message2.addresses.append(addr2)
        addr4 = Address()
        addr4.email_address = "tornado@example.com"
        addr4.message_id = message2.id
        addr4.addresstype = "CC"
        message2.addresses.append(addr4)
        addr6 = Address()
        addr6.email_address = "wr@example.com"
        addr6.message_id = message2.id
        addr6.addresstype = "BCC"
        message2.addresses.append(addr4)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)

        f = MessageFilterByBCCAddress("bcc1@example.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"

        f = MessageFilterByBCCAddress("cc1@example.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 0, "Not zero messages in messagestore"

class AddContactToContactStoreTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "mlockett@bigpond.com"
        GetGlobalContactStore().AddContact(contact)

        assert GetGlobalContactStore().GetContacts().count() == 1, "Not one message in messagestore"
        assert GetGlobalContactStore().GetContacts().first().id == contact.id, "Message id's don't match"

class FilterContactsByEmailAddressCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        contact1 = Contact()
        contact1.name = "Mark Lockett"
        contact1.emailaddress = "mlockett@bigpond.com"
        contact2 = Contact()
        contact2.name = "Johnny Hello"
        contact2.emailaddress = "hello@example.com"
        GetGlobalContactStore().AddContact(contact1)
        GetGlobalContactStore().AddContact(contact2)

        f = ContactFilterEmailAddress("hello@example.com")
        l = GetGlobalContactStore().GetContactsByFilter(f)

        assert len(l) == 1, "Not one contact in contactstore"
        assert l[0].id == contact2.id, "Contact id's don't match"
        
class FilterByTagCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message1 = Message()
        message1.body = "Hello1"
        addr1 = Address()
        addr1.email_address = "Mark_Lockett@hotmail.com"
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        tag1 = Tag()
        tag1.tagname = "Awesome"
        message1.fromaddress = "mlockett@bigpond.com"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message1.addresses.append(addr1)
        message1.tags.append(tag1)
        message2 = Message()
        message2.body = "Hello2"
        message2.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2.fromaddress = "no-one@example.com"
        addr2 = Address()
        addr2.email_address = "goblin@example.com"
        addr2.message_id = message2.id
        addr2.addresstype = "To"
        message2.addresses.append(addr2)
        GetGlobalMessageStore().AddMessage(message1)
        GetGlobalMessageStore().AddMessage(message2)

        f = MessageFilterByTag("Awesome")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        assert len(l) == 1, "Not one message in messagestore"
        assert l[0].id == message1.id, "Message id's don't match"
        
class ReceiveEmailByPOPTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        pop = mockpoplib.POP3("mail.example.com", 0)
        pop.user("mlockett")
        pop.pass_("password")
        numMessages = len(pop.list()[1])
        assert numMessages == 1,"Not one message waiting on pop server"
        rawbody = pop.retr(1)[1]

        message = Message.fromrawbodytest(rawbody)

        assert message.subject == "Hello world", "Incorrect subject"
        assert message.body == """
test body
hello

""", "Incorrect body"
        assert message.senderislivewireenabled == False, "Sender not livewire enabled"
        
class SendEmailBySMTPTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        #Is this actually testing anything? Probably not
        message1 = Message()
        message1.body = "Hello1"
        message1.subject = "Test"
        addr1 = Address()
        addr1.email_address = "Mark_Lockett@hotmail.com"
        addr1.message_id = message1.id
        addr1.addresstype = "To"
        message1.fromaddress = "mlockett@bigpond.com"
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message1.addresses.append(addr1)

        msg = MIMEText(message1.body)
        msg['Subject'] = message1.subject
        msg['From'] = message1.fromaddress
        msg['To'] = addr1.email_address

        
        smtp = mocksmtplib.SMTP("mail.example.com")
        smtp.sendmail(message1.fromaddress, [addr1.email_address], msg.as_string())
        smtp.quit()

class AddMessageDoesNotDuplicateContacts(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "Mark_Lockett@hotmail.com"
        GetGlobalContactStore().AddContact(contact)

        message = Message()
        message.fromaddress = "Mark_Lockett@hotmail.com"
        message.datetime = datetime.datetime(2013,10,31,12,0,0)
        GetGlobalMessageStore().AddMessage(message)

        assert GetGlobalMessageStore().GetMessages().count() == 1, "Not one message in messagestore"
        assert GetGlobalMessageStore().GetMessages().first().id == message.id, "Message id's don't match"
        assert GetGlobalContactStore().GetContacts().count() == 1, "Not one contact in contactstore"
        assert GetGlobalContactStore().GetContacts().first().emailaddress == message.fromaddress, "Contact email address not correct"

class DetectsLivewireEnabledSender(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        pop = mockpoplib.POP3("mail.example.com", 1)
        pop.user("mlockett")
        pop.pass_("password")
        numMessages = len(pop.list()[1])
        assert numMessages == 1,"Not one message waiting on pop server"
        rawbody = pop.retr(1)[1]

        message = Message.fromrawbodytest(rawbody)
        GetGlobalMessageStore().AddMessage(message)

        assert message.senderislivewireenabled == True, "Sender not livewire enabled"
        assert GetGlobalContactStore().GetContacts().first().islivewire == True, "Contact not set up to be livewire"
        
class DetectsLivewireEnabledSenderExistingContact(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "mlockett42@gmail.com"
        GetGlobalContactStore().AddContact(contact)

        pop = mockpoplib.POP3("mail.example.com", 1)
        pop.user("mlockett")
        pop.pass_("password")
        numMessages = len(pop.list()[1])
        assert numMessages == 1,"Not one message waiting on pop server"
        rawbody = pop.retr(1)[1]

        message = Message.fromrawbodytest(rawbody)
        GetGlobalMessageStore().AddMessage(message)

        assert message.senderislivewireenabled == True, "Sender not livewire enabled"
        assert GetGlobalContactStore().GetContacts().first().islivewire == True, "Contact not set up to be livewire"
        
class AddSettingToSettingStoreTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        setting = Setting()
        setting.name = "TestMe"
        setting.value = "Test value"
        GetGlobalSettingStore().AddSetting(setting)

        setting2 = GetGlobalSettingStore().GetSetting("TestMe")
        assert setting2.value == "Test value", "Setting value didn't match"
        setting3 = GetGlobalSettingStore().GetSetting("TestMe2")
        assert setting3 == None, "Unknown setting returning incorrect value"

class FastSettingAccessFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        GetGlobalSettingStore().SaveSetting("TestMe2", "Blah")

        assert GetGlobalSettingStore().LoadSetting("TestMe2") == "Blah", "Setting value didn't match"
        assert GetGlobalSettingStore().LoadSetting("TestMe") == "", "Unknown setting returning incorrect value"

class FastSettingChangeValueTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        GetGlobalSettingStore().SaveSetting("TestMe2", "Blah")
        GetGlobalSettingStore().SaveSetting("TestMe2", "Blah2")

        assert GetGlobalSettingStore().LoadSetting("TestMe2") == "Blah2", "Setting value didn't match"

def suite():
    suite = unittest.TestSuite()
    suite.addTest(SimpleCoversTestCase())
    suite.addTest(MergeHistoryCoverTestCase())
    suite.addTest(ListItemChangeHistoryTestCase())
    suite.addTest(SimpleItemTestCase())
    suite.addTest(AdvancedItemTestCase())
    suite.addTest(MergeHistoryCommentTestCase())
    suite.addTest(StoreObjectsInDatabaseTestCase())
    suite.addTest(StoreObjectsInJSONTestCase())
    suite.addTest(MergeChangesMadeInJSONTestCase())

    suite.addTest(FastSettingChangeValueTestCase())
    suite.addTest(FastSettingAccessFunctionsTestCase())
    suite.addTest(AddSettingToSettingStoreTestCase())
    suite.addTest(DetectsLivewireEnabledSenderExistingContact())
    suite.addTest(DetectsLivewireEnabledSender())
    suite.addTest(AddMessageDoesNotDuplicateContacts())
    suite.addTest(SendEmailBySMTPTestCase())
    suite.addTest(ReceiveEmailByPOPTestCase())
    suite.addTest(FilterByTagCase())
    suite.addTest(FilterContactsByEmailAddressCase())
    suite.addTest(AddContactToContactStoreTestCase())
    suite.addTest(FilterByBCCAddressCase())
    suite.addTest(FilterByCCAddressCase())
    suite.addTest(FilterByToAddressCase())
    suite.addTest(FilterByFromAddressCase())
    suite.addTest(FilterOrCase())
    suite.addTest(FilterAndCase())
    suite.addTest(FilterByBodyCase())
    suite.addTest(FilterBySubjectCase())
    suite.addTest(FilterByDateTestCase())
    suite.addTest(AddMessageToMessageStoreTestCase())

    #suite.addTest(SendAndReceiveUnencryptedEmail())
    
    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
 
    
    

    
