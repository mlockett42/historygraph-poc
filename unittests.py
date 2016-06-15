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
import testingmailserver
import smtplib
import poplib
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import time
from json import JSONEncoder, JSONDecoder
from Crypto.Hash import SHA256
import DocumentCollectionHelper
import hashlib
from HistoryEdgeNull import HistoryEdgeNull

class Covers(Document):
    def __init__(self, id):
        super(Covers, self).__init__(id)
    covers = FieldInt()

class SimpleCoversTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

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

class MergeHistorySendEdgeCoverTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(Covers)

    def runTest(self):
        #Test merging together by receiving an edge
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        test.covers = 2
        test2.covers = 3
        edge = test2.history.edgesbyendnode[test2.currentnode]
        history = test.history.Clone()
        history.AddEdge(edge)
        test3 = Covers(test.id)
        history.Replay(test3)
        #In a merge conflict between two integers the greater one is the winner
        self.assertEqual(test3.covers, 3)

        #Test the behaviour of receiving edges out of order
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        test.covers = 2
        test5 = test2.Clone()
        test6 = test2.Clone()
        test2.covers = 3
        test2.covers = 4
        edge4 = test2.history.edgesbyendnode[test2.currentnode]
        edge3 = test2.history.edgesbyendnode[list(edge4.startnodes)[0]]
        history = test.history.Clone()
        history.AddEdge(edge4)
        test3 = Covers(test.id)
        history.Replay(test3)
        #edge4 should be orphaned and not played
        self.assertEqual(test3.covers, 2)
        #Once edge3 is added we should replay automatically to 4
        history.AddEdge(edge3)
        test4 = Covers(test.id)
        history.Replay(test4)
        #edge4 should be orphaned and not played
        self.assertEqual(test4.covers, 4)

        #Test live adding of edges
        test5.AddEdge(edge3)
        self.assertEqual(test5.covers, 3)
        
        #Test live adding of orphaned edges
        test6.AddEdge(edge4)
        self.assertEqual(test6.covers, 1)
        test6.AddEdge(edge3)
        self.assertEqual(test6.covers, 4)

        #Test adding a Null edge where we don't  have one of the start nodes.
        #In the old way        
        dummysha = hashlib.sha256('Invalid node').hexdigest()
        history = test.history.Clone()
        edgenull = HistoryEdgeNull({test6.currentnode, dummysha}, "", "", "", "", test6.id, test6.__class__.__name__)
        history.AddEdge(edgenull)
        test6 = Covers(test.id)
        history.Replay(test6)
        self.assertEqual(test6.covers, 2)

        #In the new way
        test6 = test.Clone()
        oldnode = test6.currentnode
        edgenull = HistoryEdgeNull({test6.currentnode, dummysha}, "", "", "", "", test6.id, test6.__class__.__name__)
        test6.AddEdge(edgenull)
        self.assertEqual(test6.covers, 2)
        self.assertEqual(test6.currentnode, oldnode)
        

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
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

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
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

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
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

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
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

    def runTest(self):
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

        DocumentCollectionHelper.SaveDocumentCollection(DocumentCollection.documentcollection, 'test.history.db', 'test.content.db')

        matches = DocumentCollectionHelper.GetSQLObjects(DocumentCollection.documentcollection, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, TestPropertyOwner1)
        self.assertEqual(matches[0].id, test1id)
        matches = DocumentCollectionHelper.GetSQLObjects(DocumentCollection.documentcollection, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 5")
        self.assertEqual(len(matches), 0)

        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

        #DocumentCollection.documentcollection = DocumentCollection.DocumentCollection()
        DocumentCollectionHelper.LoadDocumentCollection(DocumentCollection.documentcollection, 'test.history.db', 'test.content.db')
        test1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        test1id = test1.id
        self.assertEqual(len(test1.propertyowner2s), 1)
        for testitem1 in test3.propertyowner2s:
            self.assertEqual(testitem1id, testitem1.id)
            self.assertEqual(testitem1.cover, 3)
        #print "StoreObjectsInDatabaseTestCase test1 = ", str(test1)
        self.assertEqual(test1.covers, 2)

        matches = DocumentCollectionHelper.GetSQLObjects(DocumentCollection.documentcollection, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, TestPropertyOwner1)
        self.assertEqual(matches[0].id, test1id)
        matches = DocumentCollectionHelper.GetSQLObjects(DocumentCollection.documentcollection, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 5")
        self.assertEqual(len(matches), 0)
    
class StoreObjectsInJSONTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

    def runTest(self):
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
        #print "jsontext = ",jsontext
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)
        DocumentCollection.documentcollection.LoadFromJSON(jsontext)
        test1s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        test1id = test1.id
        self.assertEqual(len(test1.propertyowner2s), 1)
        #print "StoreObjectsInJSONTestCase testitem1 = ", str(testitem1)
        #print "StoreObjectsInJSONTestCase test1 = ", str(test1)
        for testitem1 in test3.propertyowner2s:
            self.assertEqual(testitem1id, testitem1.id)
            self.assertEqual(testitem1.cover, 3)
        self.assertEqual(test1.covers, 2)
    
class MergeChangesMadeInJSONTestCase(unittest.TestCase):
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

    def runTest(self):
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

        #print "MergeChangesMadeInJSONTestCase test2 = ", str(test2)

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

    
class MergeAdvancedChangesMadeInJSONTestCase(unittest.TestCase):
    #Similar to merge changes test but testing things such as out of order reception of edges
    #Orphaned edges and partially orphaned merge edges
    def setUp(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(TestPropertyOwner1)
        DocumentCollection.documentcollection.Register(TestPropertyOwner2)

    def runTest(self):
        #Create an object and set some values
        test1 = TestPropertyOwner1(None)
        test1id = test1.id
        testitem1 = TestPropertyOwner2(None)
        testitem1id = testitem1.id
        test1.propertyowner2s.add(testitem1)
        testitem1.cover = 3
        test1.covers=2        

        DocumentCollection.documentcollection.AddDocumentObject(test1)

        olddc = DocumentCollection.documentcollection

        #Simulate sending the object to another user via conversion to JSON and emailing
        jsontext = DocumentCollection.documentcollection.asJSON()

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

        edge4 = test2.history.edgesbyendnode[test2.currentnode]

        test2.covers = 3
        
        edge3 = test2.history.edgesbyendnode[test2.currentnode]

        #Simulate the first user received the second users changes out of order
        #the second edge is received first. Test it is right 
        DocumentCollection.documentcollection = olddc
        DocumentCollection.documentcollection.LoadFromJSON(JSONEncoder().encode([edge3.asTuple()]))
        test2s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        #print "MergeChangesMadeInJSONTestCase test2 = ", str(test2)

        self.assertEqual(test2.covers, 2)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 3)
        self.assertEqual(testitem2.cover, 3)
         
        #Simulate the first user received the second users changes out of order
        #the first edge is not received make sure everything 
        DocumentCollection.documentcollection.LoadFromJSON(JSONEncoder().encode([edge4.asTuple()]))
        test2s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)

        test2 = test2s[0]

        #print "MergeChangesMadeInJSONTestCase test2 = ", str(test2)

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)

        oldnode = test2.currentnode         

        dummysha1 = hashlib.sha256('Invalid node 1').hexdigest()
        dummysha2 = hashlib.sha256('Invalid node 2').hexdigest()
        edgenull1 = HistoryEdgeNull({dummysha1, dummysha2}, "", "", "", "", test2.id, test2.__class__.__name__)
        edgenull2 = HistoryEdgeNull({test2.currentnode, edgenull1.GetEndNode()}, "", "", "", "", test2.id, test2.__class__.__name__)

        DocumentCollection.documentcollection.LoadFromJSON(JSONEncoder().encode([edgenull2.asTuple()]))
        test2s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        self.assertEqual(oldnode, test2.currentnode)

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)

        DocumentCollection.documentcollection.LoadFromJSON(JSONEncoder().encode([edgenull1.asTuple()]))
        test2s = DocumentCollection.documentcollection.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        self.assertEqual(oldnode, test2.currentnode)

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)

class AddMessageToMessageStoreTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        message = Message()
        message.fromaddress = "Mark_Lockett@hotmail.com"
        message.datetime = datetime.datetime(2013,10,31,12,0,0)
        GetGlobalMessageStore().AddMessage(message)

        self.assertEquals(GetGlobalMessageStore().GetMessages().count(), 1, "Not one message in messagestore")
        self.assertEquals(GetGlobalMessageStore().GetMessages().first().id, message.id, "Message id's don't match")
        self.assertEquals(GetGlobalContactStore().GetContacts().count(), 1, "Not one contact in contactstore")
        self.assertEquals(GetGlobalContactStore().GetContacts().first().emailaddress, message.fromaddress, "Contact email address not correct")

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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")

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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message2.id, "Message id's don't match")

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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message2.id, "Message id's don't match")

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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message2.id, "Message id's don't match")

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

        self.assertEquals(len(l), 2, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        self.assertEquals(l[1].id, message2.id, "Message id's don't match")

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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        
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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        
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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")

        f = MessageFilterByCCAddress("goblin@example.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        self.assertEquals(len(l), 0, "Not zero messages in messagestore")

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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")

        f = MessageFilterByBCCAddress("cc1@example.com")
        l = GetGlobalMessageStore().GetMessagesByFilter(f)

        self.assertEquals(len(l), 0, "Not zero messages in messagestore")

class AddContactToContactStoreTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "mlockett@bigpond.com"
        GetGlobalContactStore().AddContact(contact)

        self.assertEquals(GetGlobalContactStore().GetContacts().count(), 1, "Not one message in messagestore")
        self.assertEquals(GetGlobalContactStore().GetContacts().first().id, contact.id, "Message id's don't match")

class FilterContactsByEmailAddressCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        contact1 = Contact() 
        contact1.name = "Mark Lockett"
        contact1.emailaddress = "mlockett@bigpond.com"
        contact2 = Contact()

        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        public_key = key.publickey().exportKey("PEM")        

        contact2.name = "Johnny Hello"
        contact2.emailaddress = "hello@example.com"
        contact2.publickey = public_key
        GetGlobalContactStore().AddContact(contact1)
        GetGlobalContactStore().AddContact(contact2)

        f = ContactFilterEmailAddress("hello@example.com")
        l = GetGlobalContactStore().GetContactsByFilter(f)

        self.assertEquals(len(l), 1, "Not one contact in contactstore")
        self.assertEquals(l[0].id, contact2.id, "Contact id's don't match")
        self.assertEquals(contact1.publickey, "", "Public key field not set")
        self.assertEquals(contact2.publickey, public_key, "Public key field not set")
        
        
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

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        
class ReceiveEmailByPOPTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        pop = mockpoplib.POP3("mail.example.com", 0)
        pop.user("mlockett")
        pop.pass_("password")
        numMessages = len(pop.list()[1])
        self.assertEquals(numMessages, 1,"Not one message waiting on pop server")
        rawbody = pop.retr(1)[1]

        message = Message.fromrawbodytest(rawbody)

        self.assertEquals(message.subject, "Hello world", "Incorrect subject")
        self.assertEquals(message.body, """
test body
hello

""", "Incorrect body")
        self.assertFalse(message.senderislivewireenabled, "Sender not livewire enabled")
        
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

        self.assertEquals(GetGlobalMessageStore().GetMessages().count(), 1, "Not one message in messagestore")
        self.assertEquals(GetGlobalMessageStore().GetMessages().first().id, message.id, "Message id's don't match")
        self.assertEquals(GetGlobalContactStore().GetContacts().count(), 1, "Not one contact in contactstore")
        self.assertEquals(GetGlobalContactStore().GetContacts().first().emailaddress, message.fromaddress, "Contact email address not correct")

class DetectsLivewireEnabledSender(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        pop = mockpoplib.POP3("mail.example.com", 1)
        pop.user("mlockett")
        pop.pass_("password")
        numMessages = len(pop.list()[1])
        self.assertEquals(numMessages, 1,"Not one message waiting on pop server")
        rawbody = pop.retr(1)[1]

        message = Message.fromrawbodytest(rawbody)
        GetGlobalMessageStore().AddMessage(message)

        self.assertTrue(message.senderislivewireenabled, "Sender not livewire enabled")
        self.assertTrue(GetGlobalContactStore().GetContacts().first().islivewire, "Contact not set up to be livewire")
        
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
        self.assertEquals(numMessages, 1,"Not one message waiting on pop server")
        rawbody = pop.retr(1)[1]

        message = Message.fromrawbodytest(rawbody)
        GetGlobalMessageStore().AddMessage(message)

        self.assertTrue(message.senderislivewireenabled, "Sender not livewire enabled")
        self.assertTrue(GetGlobalContactStore().GetContacts().first().islivewire, "Contact not set up to be livewire")
        
class AddSettingToSettingStoreTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        setting = Setting()
        setting.name = "TestMe"
        setting.value = "Test value"
        GetGlobalSettingStore().AddSetting(setting)

        setting2 = GetGlobalSettingStore().GetSetting("TestMe")
        self.assertEquals(setting2.value, "Test value", "Setting value didn't match")
        setting3 = GetGlobalSettingStore().GetSetting("TestMe2")
        self.assertIsNone(setting3, "Unknown setting returning incorrect value")

class FastSettingAccessFunctionsTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        GetGlobalSettingStore().SaveSetting("TestMe2", "Blah")

        self.assertEquals(GetGlobalSettingStore().LoadSetting("TestMe2"), "Blah", "Setting value didn't match")
        self.assertEquals(GetGlobalSettingStore().LoadSetting("TestMe"), "", "Unknown setting returning incorrect value")

class FastSettingChangeValueTestCase(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        GetGlobalSettingStore().SaveSetting("TestMe2", "Blah")
        GetGlobalSettingStore().SaveSetting("TestMe2", "Blah2")

        self.assertEquals(GetGlobalSettingStore().LoadSetting("TestMe2"), "Blah2", "Setting value didn't match")

class SendAndReceiveUnencryptedEmail(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        sender = 'mark@livewire.io'
        receivers = ['mlockett@livewire.io']

        message = """From: Mark Lockett <mark@livewire.io>
        To: Mark Lockett <mlockett@livewire.io>
        Subject: SMTP e-mail test

        Frist post!!!!!!
        """

        smtpObj = smtplib.SMTP('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        for i in range(numMessages):
            messages = M.retr(i+1)[1]
            self.assertEquals(len(messages), 1, "Test number of messages")
            for j in messages:
                k = j.find('\\n') #The POP3 - SMTP cycle adds some extra formatting clean it up
                message2 = j[k + 2:]
                message2 = message2.replace('\\n', '\n')
                message2 = message2[:len(message)]
                self.assertEquals(message, message2, "Test message received was correct")

        M.dele(1)
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Messages should not be deleted yet")
        M.quit()

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 0, "Messages not deleted")

class SendAndReceiveEncryptedEmail(unittest.TestCase):
    #Example implementation from http://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/
    def setUp(self):
        InitSessionTesting()


    def runTest(self):
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        sender = 'mark@livewire.io'
        receivers = ['mlockett@livewire.io']

        secretmessage = "Frist post!!!!!!"
        public_key = key.publickey()
        enc_data = public_key.encrypt(secretmessage, 32)[0]

        message = """From: Mark Lockett <mark@livewire.io>
        To: Mark Lockett <mlockett@livewire.io>
        Subject: SMTP e-mail test

        """ + base64.b64encode(enc_data)

        smtpObj = smtplib.SMTP('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        for i in range(numMessages):
            messages = M.retr(i+1)[1]
            self.assertEquals(len(messages), 1, "Test number of messages")
            for j in messages:
                k = j.find('\\n') #The POP3 - SMTP cycle adds some extra formatting clean it up
                message2 = j[k + 2:]
                message2 = message2.replace('\\n', '\n')
                message2 = message2[:len(message)]
                lines = message2.split("\n")
                enc_data2 = "\n".join(lines[4:])
                enc_data2 = base64.b64decode(enc_data2)
                self.assertEquals(enc_data, enc_data2, "Encrypted data matches")
                secretmessage2 = key.decrypt(enc_data2)
                self.assertEquals(secretmessage, secretmessage2, "Secret message received was correct")

        M.dele(1)
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Messages should not be deleted yet")
        M.quit()

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 0, "Messages not deleted")

class EstablishLivewireEncryptedLink(unittest.TestCase):
    def setUp(self):
        InitSessionTesting()

    def runTest(self):
        sender = 'mlockett1@livewire.io'
        receivers = ['mlockett2@livewire.io']

        message = """From: Mark Lockett1 <mlockett1@livewire.io>
To: Mark Lockett2 <mlockett2@livewire.io>
Date: """ + datetime.datetime.now().strftime("%c") + """
Content-Type: text/plain

Subject: SMTP e-mail test

Frist post!!!!!!

======================================================================================
Livewire enabled emailer http://wwww.livewirecommunicator.org (mlockett1@livewire.io)
======================================================================================
        """

        smtpObj = smtplib.SMTP('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett2")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        for i in range(numMessages):
            messages = M.retr(i+1)[1]
            self.assertEquals(len(messages), 1, "Test number of messages")
            for j in messages:
                message2 = j
                message2 = message2.replace('\\n', '\n')

                message2 = Message.fromrawbodytest(message2)
                GetGlobalMessageStore().AddMessage(message2)

                self.assertTrue(message2.senderislivewireenabled, "Sender not livewire enabled")
                self.assertTrue(GetGlobalContactStore().GetContacts().first().islivewire, "Contact not set up to be livewire")


        #mlockett2 now knows that mlockett1 is livewire enabled so we need to tell it our private key
        sender = 'mlockett2@livewire.io'
        receivers = ['mlockett1@livewire.io']

        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        public_key = key.publickey().exportKey("PEM")        
    
        begin_livewire = "-----BEGIN-LIVEWIRE-ENCODED-MESSAGE---------------------------------------------------"
        end_livewire   = "-----END-LIVEWIRE-ENCODED-MESSAGE-----------------------------------------------------"

        message = """From: Mark Lockett2 <mlockett2@livewire.io>
To: Mark Lockett1 <mlockett1@livewire.io>
Date: """ + datetime.datetime.now().strftime("%c") + """
Content-Type: text/plain
Subject: Livewire encoded message

"""
        message += begin_livewire + "\n"

        messageid = str(uuid.uuid4())
        d = {"id":messageid,"class":"identity","email": sender,"key":public_key}
        l = ["XR1", d]
        l = JSONEncoder().encode(l)
        hash = SHA256.new(l).digest()
        signature = key.sign(hash, '')
        l2 = [l, str(signature[0])]
        l2 = JSONEncoder().encode(l2)
        line = base64.b64encode(l2)
        n = 30
        lines = [line[i:i+n] for i in range(0, len(line), n)]
        message += '\n'.join(lines) + "\n"
        message += end_livewire + "\n"

        message += """
======================================================================================
Livewire enabled emailer http://wwww.livewirecommunicator.org (mlockett2@livewire.io)
======================================================================================
"""

        smtpObj = smtplib.SMTP('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett1")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        public_key = None
        for i in range(numMessages):
            messages = M.retr(i+1)[1]
            self.assertEquals(len(messages), 1, "Test number of messages")

            headers = list()
            body = list()
            inheader = True
            for j in messages:
                k = j.find('\\n') #The POP3 - SMTP cycle adds some extra formatting clean it up
                message2 = j[k + 2:]
                message2 = message2.replace('\\n', '\n')
                lines = message2.split("\n")
                
                for line in lines:
                    if line == "":
                        inheader = False
                    elif inheader:
                        headers.append(line)
                    else:
                        body.append(line)

                
                isencodedmessage = False
                for line in headers:
                    if line[:8] == "Subject:":
                        isencodedmessage = line == "Subject: Livewire encoded message"
                    if line[:6] == "From: ":
                        k = line.find("<")
                        self.assertTrue(k > 0, "< not found")
                        fromemail = line[k + 1:]
                        k = fromemail.find(">")
                        self.assertTrue(k > 0, "> not found")
                        fromemail = fromemail[:k]
                
                inlivewirearea = False
                wasinlivewirearea = False
                wasinendlivewirearea = False
                message = []
                for line in body:
                    if line == begin_livewire:
                        inlivewirearea = True
                        wasinlivewirearea = True
                    elif line == end_livewire:
                        inlivewirearea = False
                        wasinendlivewirearea = True
                    elif inlivewirearea:
                        message.append(line)

                self.assertTrue(isencodedmessage, "Sender not livewire enabled")
                self.assertTrue(wasinlivewirearea, "Livewire begin marker not detected")
                self.assertTrue(wasinendlivewirearea, "Livewire end marker not detected")
                self.assertTrue(fromemail == "mlockett2@livewire.io", "Incorrect sender")

                message = "".join(message)
                line = base64.b64decode(message)
                line = JSONDecoder().decode(line)
                self.assertTrue(len(line) == 2, "Message is not an iterable of length two") 
                l = line[0]
                sig = long(line[1])
                l2 = JSONDecoder().decode(l)
                self.assertTrue(len(l2) == 2, "Message is not an iterable of length two") 
                self.assertTrue(l2[0] == "XR1", "Protocol version incorrect")
                d = l2[1]
                self.assertTrue(isinstance(d, dict), "d must be a dict")
                self.assertTrue(len(d) == 4, "d must contain 4 elements")
                self.assertTrue(d["class"] == "identity", "Message must be of class identity")
                self.assertTrue(d["email"] == fromemail, "Source email must match the message")
                public_key = RSA.importKey(d["key"])
                
                hash = SHA256.new(l).digest()
                verified = public_key.verify(hash, (sig, ))
                self.assertTrue(verified, "Signature not verified") 
	                
                contact = Contact()
                contact.name = "Mark Lockett"
                contact.emailaddress = fromemail
                contact.public_key = d["key"]
                GetGlobalContactStore().AddContact(contact)
                contacts = GetGlobalContactStore().GetContactsByEmailAddress(fromemail)
                self.assertTrue(len(list(contacts)) == 1, "Wrong number of matching contacts")
                self.assertTrue(contacts.first().public_key == d["key"])
                
        M.dele(1)
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Messages should not be deleted yet")
        M.quit()

        M = poplib.POP3('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 0, "Messages not deleted")

        
class StartTestingMailServerDummyTest(unittest.TestCase):
    def setUp(self):
        testingmailserver.StartTestingMailServer("livewire.io", {"mlockett":"","mlockett1":"","mlockett2":""})

    def runTest(self):
        pass        

class StopTestingMailServerDummyTest(unittest.TestCase):
    def setUp(self):
        testingmailserver.StopTestingMailServer()

    def runTest(self):
        pass        

def suite():
    suite = unittest.TestSuite()
    
    suite.addTest(SimpleCoversTestCase())
    suite.addTest(MergeHistoryCoverTestCase())
    suite.addTest(MergeHistorySendEdgeCoverTestCase())
    suite.addTest(ListItemChangeHistoryTestCase())
    suite.addTest(SimpleItemTestCase())
    suite.addTest(AdvancedItemTestCase())
    suite.addTest(MergeHistoryCommentTestCase())
    suite.addTest(StoreObjectsInDatabaseTestCase())
    suite.addTest(StoreObjectsInJSONTestCase())
    suite.addTest(MergeChangesMadeInJSONTestCase())
    suite.addTest(MergeAdvancedChangesMadeInJSONTestCase())

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

    suite.addTest(StartTestingMailServerDummyTest())
    suite.addTest(SendAndReceiveUnencryptedEmail())
    suite.addTest(SendAndReceiveEncryptedEmail())
    suite.addTest(EstablishLivewireEncryptedLink())

    suite.addTest(StopTestingMailServerDummyTest())

    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
 
    
    

    
