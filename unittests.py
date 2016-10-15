import sys
sys.path.insert(0, '/home/mark/code/livewirepy/doop')

import unittest
from Document import Document
from FieldIntRegister import FieldIntRegister
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
import mysmtplib as smtplib
import mypoplib as poplib
from Crypto.PublicKey import RSA
from Crypto import Random
import base64
import time
from json import JSONEncoder, JSONDecoder
from Crypto.Hash import SHA256
import DocumentCollectionHelper
import hashlib
from HistoryEdgeNull import HistoryEdgeNull
import timeit
from ImmutableObject import ImmutableObject
from App import App
from Demux import Demux
from mock import patch, Mock, MagicMock
import os
from FieldIntCounter import FieldIntCounter
from checkers import CheckersGame
import utils
from checkers import CheckersApp


class Covers(Document):
    def __init__(self, id):
        super(Covers, self).__init__(id)
    covers = FieldIntRegister()

class SimpleCoversTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

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
        self.dc = DocumentCollection.DocumentCollection()

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
    cover = FieldIntRegister()
    quantity = FieldIntRegister()

class TestPropertyOwner1(Document):
    covers = FieldIntRegister()
    propertyowner2s = FieldList(TestPropertyOwner2)
    def WasChanged(self, changetype, propertyowner, propertyname, propertyvalue, propertytype):
        super(TestPropertyOwner1, self).WasChanged(changetype, propertyowner, propertyname, propertyvalue, propertytype)
        self.bWasChanged = True

class MergeHistorySendEdgeCoverTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(Covers)

    def runTest(self):
        #Test merging together by receiving an edge
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        test.covers = 2
        test2.covers = 3
        edge = test2.history.edgesbyendnode[test2.currentnode]
        history = test.history.Clone()
        history.AddEdges([edge])
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
        history.AddEdges([edge4])
        test3 = Covers(test.id)
        history.Replay(test3)
        #edge4 should be orphaned and not played
        self.assertEqual(test3.covers, 2)
        #Once edge3 is added we should replay automatically to 4
        history.AddEdges([edge3])
        test4 = Covers(test.id)
        history.Replay(test4)
        #edge4 should be orphaned and not played
        self.assertEqual(test4.covers, 4)

        #Test live adding of edges
        test5.AddEdges([edge3])
        self.assertEqual(test5.covers, 3)
        
        #Test live adding of orphaned edges
        #print "Adding edge 4"
        test6.AddEdges([edge4])
        self.assertEqual(test6.covers, 1)
        #print "Adding edge 3"
        test6.AddEdges([edge3])
        self.assertEqual(test6.covers, 4)

        #Test adding a Null edge where we don't  have one of the start nodes.
        #In the old way        
        dummysha = hashlib.sha256('Invalid node').hexdigest()
        history = test.history.Clone()
        edgenull = HistoryEdgeNull({test6.currentnode, dummysha}, "", "", "", "", test6.id, test6.__class__.__name__)
        history.AddEdges([edgenull])
        test6 = Covers(test.id)
        history.Replay(test6)
        self.assertEqual(test6.covers, 2)

        #In the new way
        test6 = test.Clone()
        oldnode = test6.currentnode
        edgenull = HistoryEdgeNull({test6.currentnode, dummysha}, "", "", "", "", test6.id, test6.__class__.__name__)
        test6.AddEdges([edgenull])
        self.assertEqual(test6.covers, 2)
        self.assertEqual(test6.currentnode, oldnode)
        

class ListItemChangeHistoryTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()

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
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

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

        dc2 = DocumentCollection.DocumentCollection()
        dc2.Register(TestPropertyOwner1)
        dc2.Register(TestPropertyOwner2)
        test2 = TestPropertyOwner1(test1.id)
        dc2.AddDocumentObject(test2)
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
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

    def runTest(self):
        #Test changing them deleting a sub element
        test1 = TestPropertyOwner1(None)
        self.dc.AddDocumentObject(test1)
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
        self.dc.AddDocumentObject(test1)
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
        self.dc.AddDocumentObject(test1)
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
        self.dc.AddDocumentObject(test1)
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
        self.dc.AddDocumentObject(test1)
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
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

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
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

    def runTest(self):
        #Test writing the history to a sql lite database
        test1 = TestPropertyOwner1(None)
        self.dc.AddDocumentObject(test1)
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
        self.dc.AddDocumentObject(test3)

        test1s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)

        DocumentCollectionHelper.SaveDocumentCollection(self.dc, 'test.history.db', 'test.content.db')

        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, TestPropertyOwner1)
        self.assertEqual(matches[0].id, test1id)
        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 5")
        self.assertEqual(len(matches), 0)

        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

        #DocumentCollection.documentcollection = DocumentCollection.DocumentCollection()
        DocumentCollectionHelper.LoadDocumentCollection(self.dc, 'test.history.db', 'test.content.db')
        test1s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        test1id = test1.id
        self.assertEqual(len(test1.propertyowner2s), 1)
        for testitem1 in test3.propertyowner2s:
            self.assertEqual(testitem1id, testitem1.id)
            self.assertEqual(testitem1.cover, 3)
        #print "StoreObjectsInDatabaseTestCase test1 = ", str(test1)
        self.assertEqual(test1.covers, 2)

        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, TestPropertyOwner1)
        self.assertEqual(matches[0].id, test1id)
        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM TestPropertyOwner1 WHERE covers > 5")
        self.assertEqual(len(matches), 0)
    
class StoreObjectsInJSONTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

    def runTest(self):
        #Test writing the history to a sql lite database
        test1 = TestPropertyOwner1(None)
        self.dc.AddDocumentObject(test1)
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
        self.dc.AddDocumentObject(test3)

        test1s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test1s), 1)

        jsontext = self.dc.asJSON()
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)
        self.dc.LoadFromJSON(jsontext)
        test1s = self.dc.GetByClass(TestPropertyOwner1)
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
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

    def runTest(self):
        #Create an object and set some values
        test1 = TestPropertyOwner1(None)
        self.dc.AddDocumentObject(test1)
        test1id = test1.id
        testitem1 = TestPropertyOwner2(None)
        testitem1id = testitem1.id
        test1.propertyowner2s.add(testitem1)
        testitem1.cover = 3
        test1.covers=2        

        self.dc.AddDocumentObject(test1)

        #Simulate sending the object to another user via conversion to JSON and emailing
        jsontext = self.dc.asJSON()

        #Make some local changes
        test1.covers = 4

        #Simulate the other user (who received the email with the edges) getting the document and loading it into memory
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)
        self.dc.LoadFromJSON(jsontext)
        tpo1s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(tpo1s), 1)
        test2 = tpo1s[0]

        self.assertEqual(len(test2.propertyowner2s), 1)

        #The second user makes some changes and sends them back to the first
        for testitem2 in test2.propertyowner2s:
            testitem2.cover = 4

        test2.covers = 3
        
        jsontext = self.dc.asJSON()
        
        #Simulate the first user received the second users changes
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)
        self.dc.LoadFromJSON(jsontext)
        test2s = self.dc.GetByClass(TestPropertyOwner1)
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

    
class MergeAdvancedChangesMadeInJSONTestCase(unittest.TestCase):
    #Similar to merge changes test but testing things such as out of order reception of edges
    #Orphaned edges and partially orphaned merge edges
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

    def runTest(self):
        #Create an object and set some values
        test1 = TestPropertyOwner1(None)
        test1id = test1.id
        testitem1 = TestPropertyOwner2(None)
        testitem1id = testitem1.id
        test1.propertyowner2s.add(testitem1)
        testitem1.cover = 3
        test1.covers=2        

        self.dc.AddDocumentObject(test1)

        olddc = self.dc

        #Simulate sending the object to another user via conversion to JSON and emailing
        jsontext = self.dc.asJSON()

        #Simulate the other user (who received the email with the edges) getting the document and loading it into memory
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)
        self.dc.LoadFromJSON(jsontext)
        tpo1s = self.dc.GetByClass(TestPropertyOwner1)
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
        self.dc = olddc
        self.dc.LoadFromJSON(JSONEncoder().encode({"history":[edge3.asTuple()],"immutableobjects":[]}))
        test2s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        self.assertEqual(test2.covers, 2)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 3)
        self.assertEqual(testitem2.cover, 3)
         
        #Simulate the first user received the second users changes out of order
        #the first edge is not received make sure everything 
        self.dc.LoadFromJSON(JSONEncoder().encode({"history":[edge4.asTuple()],"immutableobjects":[]}))
        test2s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)

        test2 = test2s[0]

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)

        oldnode = test2.currentnode         

        dummysha1 = hashlib.sha256('Invalid node 1').hexdigest()
        dummysha2 = hashlib.sha256('Invalid node 2').hexdigest()
        edgenull1 = HistoryEdgeNull({dummysha1, dummysha2}, "", "", "", "", test2.id, test2.__class__.__name__)
        edgenull2 = HistoryEdgeNull({test2.currentnode, edgenull1.GetEndNode()}, "", "", "", "", test2.id, test2.__class__.__name__)

        self.dc.LoadFromJSON(JSONEncoder().encode({"history":[edgenull2.asTuple()],"immutableobjects":[]}))
        test2s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        self.assertEqual(oldnode, test2.currentnode)

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)

        self.dc.LoadFromJSON(JSONEncoder().encode({"history":[edgenull1.asTuple()],"immutableobjects":[]}))
        test2s = self.dc.GetByClass(TestPropertyOwner1)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]

        self.assertEqual(oldnode, test2.currentnode)

        self.assertEqual(test2.covers, 3)
        for testitem2 in test2.propertyowner2s:
            self.assertEqual(testitem2.cover, 4)
        self.assertEqual(testitem2.cover, 4)


class FreezeTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(Covers)

    def runTest(self):
        #Test merging together by receiving an edge
        test = Covers(None) 
        test.covers = 1
        test2 = test.Clone()
        test.covers = 2
        test2.covers = 3
        test.Freeze()
        edge = test2.history.edgesbyendnode[test2.currentnode]
        test.AddEdges([edge])
        # Normally we would receive the edge and play it. The new edge would win the conflict and update the object but that shouldn't
        # happened because we are frozen
        self.assertEqual(test.covers, 2)
        # Once we unfreeze the updates should play
        test.Unfreeze()
        self.assertFalse(test.history.HasDanglingEdges())
        self.assertEqual(test.covers, 3)

class FreezeThreeWayMergeTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(Covers)

    def runTest(self):
        #Test merging together by receiving an edge
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        test3 = test.Clone()
        test.covers = 2
        test2.covers = 3
        test3.covers = 4
        test.Freeze()
        edge2 = test2.history.edgesbyendnode[test2.currentnode]
        edge3 = test3.history.edgesbyendnode[test3.currentnode]
        test.AddEdges([edge2, edge3])
        # Normally we would receive the edge and play it. The new edge would win the conflict and update the object but that shouldn't
        # happened because we are frozen
        self.assertEqual(test.covers, 2)
        # Once we unfreeze the updates should play
        test.Unfreeze()
        #print "test.id=",test.id
        self.assertFalse(test.history.HasDanglingEdges())
        self.assertEqual(test.covers, 4)

class LargeMergeTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(Covers)

    def runTest(self):
        #Test merging together performance by receiving large numbers of edges
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        for i in range(2,52):
            test.covers = i
        for i in range(52,102):
            test2.covers = i
        # Perform this merge. This simulate databases that have been disconnected for a long time
        def wrapper(func, *args, **kwargs):
            def wrapped():
                return func(*args, **kwargs)
            return wrapped
        def test_add_edges(test, test2):
            test.AddEdges([v for (k, v) in test2.history.edgesbyendnode.iteritems()])
        wrapped = wrapper(test_add_edges, test, test2)
        time_taken = timeit.timeit(wrapped, number=1)
        #print "time_taken=",time_taken #Comment out because I don't need to see this on every run
        self.assertEqual(test.covers, 101)

class MessageTest(ImmutableObject):
    # A demo class of an immutable object. It emulated a simple text message broadcast at a certain time
    # similar to a tweet
    messagetime = FieldIntRegister() # The time in epoch milliseconds of the message
    text = FieldText() # The text of the message

class ImmutableClassTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(Covers)

    def runTest(self):
        t = int(round(time.time() * 1000))
        m = MessageTest(messagetime=t, text="Hello")
        self.assertEqual(m.messagetime, t)
        self.assertEqual(m.text, "Hello")
        
        was_exception = False
        with self.assertRaises(AssertionError):
            m.messagetime = int(round(time.time() * 1000))
            

class StoreImmutableObjectsInJSONTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(MessageTest)

    def runTest(self):
        #Test writing the immutable object to an sql lite database
        t = int(round(time.time() * 1000))
        m = MessageTest(messagetime=t, text="Hello")
        self.dc.AddImmutableObject(m)
        test1id = m.GetHash()

        test1s = self.dc.GetByClass(MessageTest)
        self.assertEqual(len(test1s), 1)

        jsontext = self.dc.asJSON()

        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(MessageTest)
        self.dc.LoadFromJSON(jsontext)
        test1s = self.dc.GetByClass(MessageTest)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        self.assertEqual(test1id, test1.GetHash())

class StoreImmutableObjectsInDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(MessageTest)

    def runTest(self):
        #Test writing the immutable object to an sql lite database
        t = int(round(time.time() * 1000))
        m = MessageTest(messagetime=t, text="Hello")
        self.dc.AddImmutableObject(m)
        test1id = m.GetHash()

        DocumentCollectionHelper.SaveDocumentCollection(self.dc, 'test.history.db', 'test.content.db')

        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM MessageTest WHERE messagetime > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, MessageTest)
        self.assertEqual(matches[0].GetHash(), test1id)
        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM MessageTest WHERE messagetime < 5")
        self.assertEqual(len(matches), 0)

        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(MessageTest)

        DocumentCollectionHelper.LoadDocumentCollection(self.dc, 'test.history.db', 'test.content.db')

        test1s = self.dc.GetByClass(MessageTest)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        test1id = test1.GetHash()

        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM MessageTest WHERE messagetime > 1")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].__class__, MessageTest)
        self.assertEqual(matches[0].GetHash(), test1id)
        matches = DocumentCollectionHelper.GetSQLObjects(self.dc, 'test.content.db', "SELECT id FROM MessageTest WHERE messagetime < 5")
        self.assertEqual(len(matches), 0)

class TestUpdateHandler(object):
    #Handle update requests to us
    def WasChanged(self, source):
        self.covers = source.covers
    
class SimpleCoversUpdateTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(TestPropertyOwner1)
        self.dc.Register(TestPropertyOwner2)

    def runTest(self):
        #Test merging together simple covers documents
        test = Covers(None)
        test.covers = 1
        handler = TestUpdateHandler()
        test.AddHandler(handler.WasChanged)
        self.assertEqual(len(test.change_handlers), 1)
        test.covers = 2
        self.assertEqual(handler.covers, 2)
        test.RemoveHandler(handler.WasChanged)
        self.assertEqual(len(test.change_handlers), 0)
        test.covers = 3
        self.assertEqual(handler.covers, 2)
    
class FreezeUpdateTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(Covers)

    def runTest(self):
        #Test merging together by receiving an edge
        test = Covers(None) 
        test.covers = 1

        test2 = test.Clone()
        handler = TestUpdateHandler()
        test.AddHandler(handler.WasChanged)
        test.covers = 2
        test2.covers = 3
        test.Freeze()
        self.assertEqual(handler.covers, 2)
        edge = test2.history.edgesbyendnode[test2.currentnode]
        test.AddEdges([edge])
        # Normally we would receive the edge and play it. The new edge would win the conflict and update the object but that shouldn't
        # happened because we are frozen
        self.assertEqual(test.covers, 2)
        self.assertEqual(handler.covers, 2)
        # Once we unfreeze the updates should play
        test.Unfreeze()
        self.assertFalse(test.history.HasDanglingEdges())
        self.assertEqual(test.covers, 3)
        self.assertEqual(handler.covers, 3)


class AddMessageToMessageStoreTestCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        message = Message()
        message.fromaddress = "Mark_Lockett@hotmail.com"
        message.datetime = datetime.datetime(2013,10,31,12,0,0)
        self.demux.messagestore.AddMessage(message, None)

        self.assertEquals(self.demux.messagestore.GetMessages().count(), 1, "Not one message in messagestore")
        self.assertEquals(self.demux.messagestore.GetMessages().first().id, message.id, "Message id's don't match")
        self.assertEquals(self.demux.contactstore.GetContacts().count(), 1, "Not one contact in contactstore")
        self.assertEquals(self.demux.contactstore.GetContacts().first().emailaddress, message.fromaddress, "Contact email address not correct")

class FilterByDateTestCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        message1 = Message()
        message1.datetime = datetime.datetime(2013,10,31,12,0,0)
        message2 = Message()
        message2.datetime = datetime.datetime(2013,11,1,12,0,0)
        message3 = Message()
        message3.datetime = datetime.datetime(2013,10,30,12,0,0)
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)
        self.demux.messagestore.AddMessage(message3, None)

        f = MessageFilterDateTime(datetime.datetime(2013,10,31,0,0,0), datetime.datetime(2013,10,31,23,59,59))
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")

class FilterBySubjectCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)
        self.demux.messagestore.AddMessage(message3, None)

        f = MessageFilterSubject("Hello2")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message2.id, "Message id's don't match")

class FilterByBodyCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)
        self.demux.messagestore.AddMessage(message3, None)

        f = MessageFilterBody("Hello2")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message2.id, "Message id's don't match")

class FilterAndCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)
        self.demux.messagestore.AddMessage(message3, None)

        f1 = MessageFilterBody("Hello2")
        f2 = MessageFilterSubject("blarg")
        f = MessageFilterAnd(f1, f2)
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message2.id, "Message id's don't match")

class FilterOrCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)
        self.demux.messagestore.AddMessage(message3, None)

        f1 = MessageFilterBody("Hello2")
        f2 = MessageFilterSubject("blarg1")
        f = MessageFilterOr(f1, f2)
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 2, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        self.assertEquals(l[1].id, message2.id, "Message id's don't match")

class FilterByFromAddressCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')
        
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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)
        self.demux.messagestore.AddMessage(message3, None)

        f = MessageFilterFromAddress("mlockett@bigpond.com")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        
class FilterByToAddressCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)

        f = MessageFilterByToAddress("Mark_Lockett@hotmail.com")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        
class FilterByCCAddressCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)

        f = MessageFilterByCCAddress("cc1@example.com")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")

        f = MessageFilterByCCAddress("goblin@example.com")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 0, "Not zero messages in messagestore")

class FilterByBCCAddressCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)

        f = MessageFilterByBCCAddress("bcc1@example.com")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")

        f = MessageFilterByBCCAddress("cc1@example.com")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 0, "Not zero messages in messagestore")

class AddContactToContactStoreTestCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "mlockett@bigpond.com"
        self.demux.contactstore.AddContact(contact)

        self.assertEquals(self.demux.contactstore.GetContacts().count(), 1, "Not one message in messagestore")
        self.assertEquals(self.demux.contactstore.GetContacts().first().id, contact.id, "Message id's don't match")

class FilterContactsByEmailAddressCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.contactstore.AddContact(contact1)
        self.demux.contactstore.AddContact(contact2)

        f = ContactFilterEmailAddress("hello@example.com")
        l = self.demux.contactstore.GetContactsByFilter(f)

        self.assertEquals(len(l), 1, "Not one contact in contactstore")
        self.assertEquals(l[0].id, contact2.id, "Contact id's don't match")
        self.assertEquals(contact1.publickey, "", "Public key field not set")
        self.assertEquals(contact2.publickey, public_key, "Public key field not set")
        
        
class FilterByTagCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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
        self.demux.messagestore.AddMessage(message1, None)
        self.demux.messagestore.AddMessage(message2, None)

        f = MessageFilterByTag("Awesome")
        l = self.demux.messagestore.GetMessagesByFilter(f)

        self.assertEquals(len(l), 1, "Not one message in messagestore")
        self.assertEquals(l[0].id, message1.id, "Message id's don't match")
        
class AddMessageDoesNotDuplicateContacts(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "Mark_Lockett@hotmail.com"
        self.demux.contactstore.AddContact(contact)

        message = Message()
        message.fromaddress = "Mark_Lockett@hotmail.com"
        message.datetime = datetime.datetime(2013,10,31,12,0,0)
        self.demux.messagestore.AddMessage(message, None)

        self.assertEquals(self.demux.messagestore.GetMessages().count(), 1, "Not one message in messagestore")
        self.assertEquals(self.demux.messagestore.GetMessages().first().id, message.id, "Message id's don't match")
        self.assertEquals(self.demux.contactstore.GetContacts().count(), 1, "Not one contact in contactstore")
        self.assertEquals(self.demux.contactstore.GetContacts().first().emailaddress, message.fromaddress, "Contact email address not correct")

class AddSettingToSettingStoreTestCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        setting = Setting()
        setting.name = "TestMe"
        setting.value = "Test value"
        self.demux.settingsstore.AddSetting(setting)

        setting2 = self.demux.settingsstore.GetSetting("TestMe")
        self.assertEquals(setting2.value, "Test value", "Setting value didn't match")
        setting3 = self.demux.settingsstore.GetSetting("TestMe2")
        self.assertIsNone(setting3, "Unknown setting returning incorrect value")

class FastSettingAccessFunctionsTestCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        self.demux.settingsstore.SaveSetting("TestMe2", "Blah")

        self.assertEquals(self.demux.settingsstore.LoadSetting("TestMe2"), "Blah", "Setting value didn't match")
        self.assertEquals(self.demux.settingsstore.LoadSetting("TestMe"), "", "Unknown setting returning incorrect value")

class FastSettingChangeValueTestCase(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        self.demux.settingsstore.SaveSetting("TestMe2", "Blah")
        self.demux.settingsstore.SaveSetting("TestMe2", "Blah2")

        self.assertEquals(self.demux.settingsstore.LoadSetting("TestMe2"), "Blah2", "Setting value didn't match")

class SendAndReceiveUnencryptedEmail(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

    def runTest(self):
        sender = 'mark@livewire.io'
        receivers = ['mlockett@livewire.io']

        message = """From: Mark Lockett <mark@livewire.io>
        To: Mark Lockett <mlockett@livewire.io>
        Subject: SMTP e-mail test

        Frist post!!!!!!
        """

        smtpObj = smtplib.SMTP_SSL('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        for i in range(numMessages):
            lines = M.retr(i+1)[1]
            message2 = '\n'.join(lines[1:]) #Build the message. The first line is inserted by the emailer
            self.assertEquals(message, message2) #, "Test message received was correct")

        M.dele(1)
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Messages should not be deleted yet")
        M.quit()

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 0, "Messages not deleted")

class SendAndReceiveEncryptedEmail(unittest.TestCase):
    #Example implementation from http://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')


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

        smtpObj = smtplib.SMTP_SSL('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        for i in range(numMessages):
            lines = M.retr(i+1)[1]
            lines = lines[1:] #Lines 
            enc_data2 = "\n".join(lines[4:])
            enc_data2 = base64.b64decode(enc_data2)
            self.assertEquals(enc_data, enc_data2)#, "Encrypted data matches")
            secretmessage2 = key.decrypt(enc_data2)
            self.assertEquals(secretmessage, secretmessage2)#, "Secret message received was correct")

        M.dele(1)
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Messages should not be deleted yet")
        M.quit()

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 0, "Messages not deleted")

class EstablishLivewireEncryptedLink(unittest.TestCase):
    @patch.object(Demux, 'get_database_filename')
    def setUp(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

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

        smtpObj = smtplib.SMTP_SSL('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett2")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        for i in range(numMessages):
            lines = M.retr(i+1)[1]
            message2 = '\n'.join(lines)

            message2 = Message.fromrawbody(message2)
            self.demux.messagestore.AddMessage(message2, None)

            self.assertTrue(message2.senderislivewireenabled, "Sender not livewire enabled")
            self.assertTrue(self.demux.contactstore.GetContacts().first().islivewire, "Contact not set up to be livewire")


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

        smtpObj = smtplib.SMTP_SSL('localhost', 10025)
        smtpObj.sendmail(sender, receivers, message)         

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett1")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Test number of messages")
        public_key = None
        for i in range(numMessages):
            lines = M.retr(i+1)[1]

            headers = list()
            body = list()
            inheader = True
                
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
            self.demux.contactstore.AddContact(contact)
            contacts = self.demux.contactstore.GetContactsByEmailAddress(fromemail)
            self.assertTrue(len(list(contacts)) == 1, "Wrong number of matching contacts")
            self.assertTrue(contacts.first().public_key == d["key"])
                
        M.dele(1)
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 1, "Messages should not be deleted yet")
        M.quit()

        M = poplib.POP3_SSL('localhost', 10026)
        M.user("mlockett")
        M.pass_("")
        numMessages = len(M.list()[1])
        self.assertEquals(numMessages, 0, "Messages not deleted")

class EstablishLivewireEncryptedLinkUsingDemux(unittest.TestCase):
    def setUp(self):
        testingmailserver.ResetMailDict()

    @patch.object(Demux, 'get_database_filename')
    def runTest(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        demux1 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')
        demux2 = Demux(myemail='mlockett2@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett2',smtppass='',
                       popuser='mlockett2',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

        message = """
Frist post!!!!!!

"""
        demux1.SendPlainEmail(receivers = ['mlockett2@livewire.io'], subject = "SMTP e-mail test", message=message)

        messages = demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)

        time.sleep(0.01) #Give background thread a chance to run
        
        demux2.CheckEmail()

        messages = demux2.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 1)
        message = messages[0]
        self.assertTrue(message.senderislivewireenabled) # Sender is not livewire enabled

        #mlockett2 now knows that mlockett1 is livewire enabled The demux should have already sent to mlockett1 our public key
        
        time.sleep(0.01) #Give background thread a chance to run
        
        messages = demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)

        demux1.CheckEmail() #Demux 1 should receive a message from demux2 and recognise it is livewire enabled and get the public key

        contacts = demux1.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertTrue(contacts[0].islivewire)
        self.assertEqual(contacts[0].publickey, demux2.key.publickey().exportKey("PEM"))

        time.sleep(0.01) #Give background thread a chance to run

        demux2.CheckEmail() #Demux 2 should receive a message from demux1 with it's public key

        #Each demux should now have the public key of the other one

        contacts = demux2.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertEqual(contacts[0].publickey, demux1.key.publickey().exportKey("PEM") )
        self.assertTrue(contacts[0].islivewire)

        #Send an encrypted email 
        message = """
Second post!!!!!!


"""
        demux1.SendEncryptedEmail(demux1.contactstore.GetContacts()[0], subject = "Encrypted SMTP e-mail test", message=message)

        time.sleep(0.01) #Give background thread a chance to run

        demux2.CheckEmail() #Demux 2 should receive an encrypted message from demux1
        
        messages = demux2.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 2)
        message = messages[1]
        self.assertEqual(message.subject, "Encrypted SMTP e-mail test")
        self.assertTrue(message.body.find("Second post!!!!!!") > 0, "Second post!!!!!!")
        self.assertTrue(message.senderislivewireenabled) # Sender is not livewire enabled
        self.assertTrue(message.messageisencrypted) # This message was encrypted


class EstablishLivewireEncryptedLinkUsingDemuxExistingContact(unittest.TestCase):
    def setUp(self):
        testingmailserver.ResetMailDict()

    @patch.object(Demux, 'get_database_filename')
    def runTest(self, mock_get_database_filename):
        mock_get_database_filename.return_value = ':memory:'
        demux1 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')
        demux2 = Demux(myemail='mlockett2@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett2',smtppass='',
                       popuser='mlockett2',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

        #Create the contacts manually
        contact = Contact()
        contact.name = "Mark Lockett"
        contact.emailaddress = "<mlockett1@livewire.io>"
        demux2.contactstore.AddContact(contact)
        contacts = demux2.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertFalse(contacts[0].islivewire)

        message = """

Frist post!!!!!!

"""
        demux1.SendPlainEmail(receivers = ['mlockett2@livewire.io'], subject = "SMTP e-mail test", message=message)

        messages = demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)

        time.sleep(0.01) #Give background thread a chance to run
        
        demux2.CheckEmail()

        messages = demux2.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 1)
        message = messages[0]
        self.assertTrue(message.senderislivewireenabled) # Sender is not livewire enabled

        #mlockett2 now knows that mlockett1 is livewire enabled The demux should have already sent to mlockett1 our public key
        
        time.sleep(0.01) #Give background thread a chance to run
        
        messages = demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)


        demux1.CheckEmail() #Demux 1 should receive a message from demux2 and recognise it is livewire enabled and get the public key

        contacts = demux1.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertTrue(contacts[0].islivewire)
        self.assertEqual(contacts[0].publickey, demux2.key.publickey().exportKey("PEM"))

        time.sleep(0.01) #Give background thread a chance to run

        demux2.CheckEmail() #Demux 2 should receive a message from demux1 with it's public key

        #Each demux should now have the 

        contacts = demux2.contactstore.GetContacts()

        contacts = list(contacts)

        self.assertEqual(len(list(contacts)), 1)
        self.assertEqual(contacts[0].publickey, demux1.key.publickey().exportKey("PEM") )
        self.assertTrue(contacts[0].islivewire)


class CoversApp(App):
    def MessageReceived(s):
        pass

    def CreateNewDocumentCollection(self, dcid):
        dc = super(CoversApp, self).CreateNewDocumentCollection(dcid)
        dc.Register(TestPropertyOwner1)
        dc.Register(MessageTest)
        return dc
        
class DemuxTestCase(unittest.TestCase):
    def setUp(self):
        testingmailserver.ResetMailDict()
        self.demux1 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')
        self.demux2 = Demux(myemail='mlockett2@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett2',smtppass='',
                       popuser='mlockett2',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

        message = """
Frist post!!!!!!

"""
        self.demux1.SendPlainEmail(receivers = ['mlockett2@livewire.io'], subject = "SMTP e-mail test", message=message)

        messages = self.demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)

        time.sleep(0.01) #Give background thread a chance to run
        
        self.demux2.CheckEmail()

        messages = self.demux2.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 1)
        message = messages[0]
        self.assertTrue(message.senderislivewireenabled) # Sender is not livewire enabled

        #mlockett2 now knows that mlockett1 is livewire enabled The demux should have already sent to mlockett1 our public key
        
        time.sleep(0.01) #Give background thread a chance to run
        
        messages = self.demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)

        self.demux1.CheckEmail() #Demux 1 should receive a message from demux2 and recognise it is livewire enabled and get the public key

        contacts = self.demux1.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertTrue(contacts[0].islivewire)
        self.assertEqual(contacts[0].publickey, self.demux2.key.publickey().exportKey("PEM"))

        time.sleep(0.01) #Give background thread a chance to run

        self.demux2.CheckEmail() #Demux 2 should receive a message from demux1 with it's public key

        #Each demux should now have the 

        contacts = self.demux2.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertEqual(contacts[0].publickey, self.demux1.key.publickey().exportKey("PEM") )
        self.assertTrue(contacts[0].islivewire)

    def runTest(self):

        app1 = CoversApp(self.demux1)
        app2 = CoversApp(self.demux2)

        self.demux1.RegisterApp(app1)
        self.demux2.RegisterApp(app2)

        dc1 = app1.CreateNewDocumentCollection(None)
        test_a = TestPropertyOwner1(None)
        test_a.covers = 1
        dc1.AddDocumentObject(test_a)
        test_b = TestPropertyOwner1(None)
        test_b.covers = 10
        dc1.AddDocumentObject(test_b)
        testingmailserver.ResetMailDict() #Remove this line emails not being correctly deleted over pop
        app1.Share(dc1, 'mlockett2@livewire.io')

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()

        dc2 = app2.GetDocumentCollectionByID(dc1.id)

        self.assertEqual(len(dc2.objects[TestPropertyOwner1.__name__]), 2)
        test_a2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_a.id)
        test_b2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_b.id)

        self.assertEqual(test_a.id, test_a2.id)
        self.assertEqual(test_a.covers, test_a2.covers)
        self.assertEqual(test_b.id, test_b2.id)
        self.assertEqual(test_b.covers, test_b2.covers)

        test_a.covers = 2 #This should share the update automatically

        t = int(round(time.time() * 1000))
        m = MessageTest(messagetime=t, text="Hello")
        dc1.AddImmutableObject(m)
        test1id = m.GetHash()

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()
        
        self.assertEqual(len(dc2.objects[TestPropertyOwner1.__name__]), 2)
        test_a2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_a.id)

        self.assertEqual(test_a.id, test_a2.id)
        self.assertEqual(test_a.covers, 2)
        self.assertEqual(test_a2.covers, 2)
        self.assertEqual(test_a.covers, test_a2.covers)

        test1s = dc2.GetByClass(MessageTest)
        self.assertEqual(len(test1s), 1)
        test1 = test1s[0]
        self.assertEqual(m.messagetime, test1.messagetime)
        self.assertEqual(m.text, test1.text)
        self.assertEqual(m._prevhash, test1._prevhash)
        self.assertEqual(m.GetHash(), test1.GetHash())
        m_b = dc2.GetObjectByID(MessageTest.__name__, m.GetHash())
        self.assertEqual(m.GetHash(), m_b.GetHash())
        self.assertEqual(m.messagetime, m_b.messagetime)
        self.assertEqual(m.text, m_b.text)

        #Test the transmission of sequenced immutable objects including that we get 
        t = int(round(time.time() * 1000))
        m1 = MessageTest(messagetime=t, text="Hello 1")
        self.assertEqual(m1._prevhash, '')
        m2 = MessageTest(messagetime=t + 1, text="Hello 2", _prevhash = m1.GetHash())
        self.assertEqual(m2._prevhash, m1.GetHash())
        m3 = MessageTest(messagetime=t + 2, text="Hello 3", _prevhash = m2.GetHash())
        self.assertEqual(m3._prevhash, m2.GetHash())

        #Add two objects to the dc we expect a request for the second one
        dc1.AddImmutableObject(m1)
        dc1.AddImmutableObject(m3)

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()
        self.assertEqual(len(dc2.objects[MessageTest.__name__]), 3)
        m1_b = dc2.GetObjectByID(MessageTest.__name__, m1.GetHash())
        m3_b = dc2.GetObjectByID(MessageTest.__name__, m3.GetHash())
        self.assertEqual(m1_b.messagetime, m1.messagetime)
        self.assertEqual(m1_b.text, m1.text)
        self.assertEqual(m3_b.messagetime, m3.messagetime)
        self.assertEqual(m3_b.text, m3.text)

        time.sleep(0.01) #Give the email a chance to send. Demux 2 should have sent a request for m2 to demux1 
        dc1.AddImmutableObject(m2)
        self.demux1.CheckEmail()
        
        time.sleep(0.01) #Give the email a chance to send. Demux 1 should have sent m2 to demux2 
        self.demux2.CheckEmail()
        self.assertEqual(len(dc2.objects[MessageTest.__name__]), 4)
        m2_b = dc2.GetObjectByID(MessageTest.__name__, m2.GetHash())
        self.assertEqual(m2_b.messagetime, m2.messagetime)
        self.assertEqual(m2_b.text, m2.text)

class DemuxEdgeAuthenticationTestCase(DemuxTestCase):
    def runTest(self):
        #demux1 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
        #               popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')
        #demux2 = Demux(myemail='mlockett2@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett2',smtppass='',
        #               popuser='mlockett2',poppass='',popport=10026, popserver='localhost', fromfile=':memory:')

        app1 = CoversApp(self.demux1)
        app2 = CoversApp(self.demux2)

        self.demux1.RegisterApp(app1)
        self.demux2.RegisterApp(app2)

        dc1 = app1.CreateNewDocumentCollection(None)
        test_a = TestPropertyOwner1(None)
        test_a.covers = 1
        dc1.AddDocumentObject(test_a)
        testingmailserver.ResetMailDict() #Remove this line emails not being correctly deleted over pop
        app1.Share(dc1, 'mlockett2@livewire.io')

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()

        l = app2.GetDocumentCollections()
        self.assertEqual(len(l), 1)
        dc2 = l[0]

        self.assertEqual(len(dc2.objects[TestPropertyOwner1.__name__]), 1)
        test_a2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_a.id)

        self.assertEqual(test_a.id, test_a2.id)
        self.assertEqual(test_a.covers, test_a2.covers)

        random_generator = Random.new().read
        self.demux1.key = RSA.generate(1024, random_generator) #Create a new key to pretend to impersonate demux1

        test_a.covers = 2 #This should share the update automatically, but because we have changed the key it should be rejected

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()
        
        self.assertEqual(len(dc2.objects[TestPropertyOwner1.__name__]), 1)
        test_a2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_a.id)

        self.assertEqual(test_a.id, test_a2.id)
        self.assertEqual(test_a2.covers, 1) #The change to 2 above should have been rejected


class DemuxCanSaveAndLoadTestCase(unittest.TestCase):
    def setUp(self):
        if os.path.exists('/tmp/testdump.db'):
            os.remove('/tmp/testdump.db')
        else:
            pass

    def runTest(self):
        self.assertFalse(os.path.exists('/tmp/testdump.db'))
        self.demux = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile='/tmp/testdump.db')
        self.assertTrue(os.path.exists('/tmp/testdump.db'))
        demux2 = Demux(fromfile = '/tmp/testdump.db')
        self.assertEqual(self.demux.myemail, demux2.myemail)
        self.assertEqual(self.demux.smtpserver, demux2.smtpserver)
        self.assertEqual(self.demux.smtpport, demux2.smtpport)
        self.assertEqual(self.demux.smtpuser, demux2.smtpuser)
        self.assertEqual(self.demux.smtppass, demux2.smtppass)
        self.assertEqual(self.demux.popserver, demux2.popserver)
        self.assertEqual(self.demux.popuser, demux2.popuser)
        self.assertEqual(self.demux.poppass, demux2.poppass)
        self.assertEqual(self.demux.popport, demux2.popport)
        self.assertEqual(self.demux.key, demux2.key)

class CounterTestContainer(Document):
    def __init__(self, id):
        super(CounterTestContainer, self).__init__(id)
    testcounter = FieldIntCounter()

class SimpleCounterTestCase(unittest.TestCase):
    def runTest(self):
        #Test merging together simple counter documents
        test = CounterTestContainer(None)
        #Test we default to zero
        self.assertEqual(test.testcounter.get(), 0)
        #Test adding and subtract gives reasonable values
        test.testcounter.add(1)
        self.assertEqual(test.testcounter.get(), 1)
        test.testcounter.add(1)
        self.assertEqual(test.testcounter.get(), 2)
        test.testcounter.subtract(1)
        self.assertEqual(test.testcounter.get(), 1)

class MergeCounterTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()

    def runTest(self):
        #Test merge together two simple covers objects
        test = CounterTestContainer(None)
        test.testcounter.add(1)
        self.assertEqual(test.testcounter.get(), 1)
        test2 = test.Clone()
        test.testcounter.subtract(1)
        test2.testcounter.add(1)
        test3 = test.Merge(test2)
        self.assertEqual(test3.testcounter.get(), 1)
        

class MergeCounterChangesMadeInJSONTestCase(unittest.TestCase):
    def setUp(self):
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(CounterTestContainer)

    def runTest(self):
        #Create an object and set some values
        test1 = CounterTestContainer(None)
        test1id = test1.id

        self.dc.AddDocumentObject(test1)
        test1.testcounter.add(1)
        self.assertEqual(test1.testcounter.get(), 1)

        olddc = self.dc

        sharedcurrentnode = test1.currentnode
        #Simulate sending the object to another user via conversion to JSON and emailing
        jsontext = self.dc.asJSON()

        #Simulate making local conflicting changes
        test1.testcounter.subtract(1)
        self.assertEqual(test1.testcounter.get(), 0)

        #Simulate the other user (who received the email with the edges) getting the document and loading it into memory
        self.dc = DocumentCollection.DocumentCollection()
        self.dc.Register(CounterTestContainer)
        self.dc.LoadFromJSON(jsontext)
        self.assertEqual(jsontext, self.dc.asJSON())
        tpo1s = self.dc.GetByClass(CounterTestContainer)
        self.assertEqual(len(tpo1s), 1)
        test2 = tpo1s[0]

        #print "test1 edges=",[str(edge) for edge in test1.history.GetAllEdges()]
        #print "test2 edges=",[str(edge) for edge in test2.history.GetAllEdges()]
        self.assertEqual(sharedcurrentnode, test2.currentnode)
        #The second user makes some changes and sends them back to the first
        test2.testcounter.add(1)
        self.assertEqual(test2.testcounter.get(), 2)

        edgenext = test2.history.edgesbyendnode[test2.currentnode]


        #Simulate the first user received the second users changes out of order
        #the second edge is received first. Test it is right 
        self.dc = olddc
        self.dc.LoadFromJSON(JSONEncoder().encode({"history":[edgenext.asTuple()],"immutableobjects":[]}))
        test2s = self.dc.GetByClass(CounterTestContainer)
        self.assertEqual(len(test2s), 1)
        test2 = test2s[0]
        #print "test2 edges=",[str(edge) for edge in test2.history.GetAllEdges()]

        self.assertEqual(test2.testcounter.get(), 1)


class CheckersBoardSquareColourTestCase(unittest.TestCase):
    def runTest(self):
        checkersgame = CheckersGame(None)
        for x in range(8):
            for y in range(8):
                assert checkersgame.GetSquareColour(x, y) == "W" if ((x + y) % 2 == 0) else "B"

class CheckersBoardInitialValidityTestCase(unittest.TestCase):
    def runTest(self):
        # CreateBoard needs a list of 8 lists of 8 strings
        # Test if rejects non lists
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard(None)
        #Test it reject len != 8
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard(list())
        #Test in rejects list items not being lists themselves
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard(list(range(8)))
        #Test it rejects in the inner lists don't have length 8
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard([list() for r in range(8)])
        #Test it rejects if the members of the inner list are not string
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard([list(range(8)) for r in range(8)])
        #Test we cannot enter an invalid piece code
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard([['','Hello','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ])
        #Test we cannot place a piece on a white square
        with self.assertRaises(AssertionError):
            checkersgame = CheckersGame(None)
            checkersgame.CreateBoard([['W','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ['','','','','','','',''],
                                      ])
        #Check we can create a valid board
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','B','','WK','','BK'],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        self.assertIs(checkersgame.GetPieceAt(0,0), None)
        p = checkersgame.GetPieceAt(1,0)
        self.assertEqual(p.pieceside, "W")
        self.assertEqual(p.piecetype, "")
        p = checkersgame.GetPieceAt(3,0)
        self.assertEqual(p.pieceside, "B")
        self.assertEqual(p.piecetype, "")
        p = checkersgame.GetPieceAt(5,0)
        self.assertEqual(p.pieceside, "W")
        self.assertEqual(p.piecetype, "K")
        p = checkersgame.GetPieceAt(7,0)
        self.assertEqual(p.pieceside, "B")
        self.assertEqual(p.piecetype, "K")

        #Check we can create a valid board to start a game
        checkersgame = CheckersGame(None)
        checkersgame.CreateDefaultStartBoard()
        for y in range(8):
            for x in range(8):
                if ((x + y) % 2) == 0:
                    self.assertIs(checkersgame.GetPieceAt(x,y), None)
                else:
                    p = checkersgame.GetPieceAt(x,y)
                    if y <= 2:
                        self.assertEqual(p.pieceside, "W")
                        self.assertEqual(p.piecetype, "")
                    elif y >= 5:
                        self.assertEqual(p.pieceside, "B")
                        self.assertEqual(p.piecetype, "")
                    else:
                        self.assertIs(p, None)

class CheckersBoardValidMovesTestCase(unittest.TestCase):     
    def runTest(self):
        # Check a white pawn can move as expected     
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(1,0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 2)
        self.assertIn((0,1), validmoves)
        self.assertIn((2,1), validmoves)

        # Check a black pawn can move as expected     
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','B','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,7)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 2)
        self.assertIn((1,6), validmoves)
        self.assertIn((3,6), validmoves)

        # Check a white king can move as expected     
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','WK','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 4)
        self.assertIn((1,0), validmoves)
        self.assertIn((3,0), validmoves)
        self.assertIn((1,2), validmoves)
        self.assertIn((3,2), validmoves)

        # Check a black king can move as expected     
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','BK','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 4)
        self.assertIn((1,0), validmoves)
        self.assertIn((3,0), validmoves)
        self.assertIn((1,2), validmoves)
        self.assertIn((3,2), validmoves)

        # Check a piece cannot move off the board     
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','WK','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(1,0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 2)
        self.assertIn((0,1), validmoves)
        self.assertIn((2,1), validmoves)

        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['WK','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(0,1)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 2)
        self.assertIn((1,0), validmoves)
        self.assertIn((1,2), validmoves)

        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','','WK'],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(7,0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 1)
        self.assertIn((6,1), validmoves)

        # Check a piece cannot move in the space occupied by another piece and we cannot capture our own pieces
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','BK','','','','',''],
                                  ['','','','BK','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validcaptures = w.GetValidCaptures()[0]
        self.assertEqual(len(validcaptures),0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 3)
        self.assertIn((1,0), validmoves)
        self.assertIn((3,0), validmoves)
        self.assertIn((1,2), validmoves)

        # Check a we can capture an opposing piece
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','BK','','','','',''],
                                  ['','','','WK','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validcaptures = w.GetValidCaptures()[0]
        self.assertEqual(len(validcaptures),1)
        self.assertIn((4,3), validcaptures)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 4)
        self.assertIn((1,0), validmoves)
        self.assertIn((3,0), validmoves)
        self.assertIn((1,2), validmoves)
        self.assertIn((4,3), validmoves)

        # Check a pawn cannot capture backwards
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','B','','','','',''],
                                  ['','','','WK','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validcaptures = w.GetValidCaptures()[0]
        self.assertEqual(len(validcaptures),0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 2)
        self.assertIn((1,0), validmoves)
        self.assertIn((3,0), validmoves)

        # Check a we cannot capture an opposing piece if it is blocked
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','BK','','','','',''],
                                  ['','','','WK','','','',''],
                                  ['','','','','WK','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validcaptures = w.GetValidCaptures()[0]
        self.assertEqual(len(validcaptures),0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 3)
        self.assertIn((1,0), validmoves)
        self.assertIn((3,0), validmoves)
        self.assertIn((1,2), validmoves)

        # Check a we cannot capture an opposing piece by moving off screen
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','WK','','','',''],
                                  ['','','BK','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(2,1)
        validcaptures = w.GetValidCaptures()[0]
        self.assertEqual(len(validcaptures),0)
        validmoves = w.GetValidMoves()
        self.assertEqual(len(validmoves), 3)
        self.assertIn((1,0), validmoves)
        self.assertIn((1,2), validmoves)
        self.assertIn((3,2), validmoves)

        # Check a can move a piece to a valid location
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(1, 0)
        w.MoveTo(2,1)
        checkersgame.assertBoardEquals([
                                  ['','','','','','','',''],
                                  ['','','W','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])

        # Check we cannot move a piece out of turn
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['B','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(0, 7)
        with self.assertRaises(AssertionError):
            w.MoveTo(1,6)

        # Check we can manually advance the turn and move
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['B','','','','','','',''],
                                  ])
        checkersgame.turn.add(1)
        w = checkersgame.GetPieceAt(0, 7)
        w.MoveTo(1,6)

        # Check we cannot move a piece to an invalid location
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['B','','','','','','',''],
                                  ])
        checkersgame.turn.add(1)
        w = checkersgame.GetPieceAt(0, 7)
        with self.assertRaises(AssertionError):
            w.MoveTo(2,5)

        # Check we can capture a piece
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','','','','',''],
                                  ['','','B','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(1, 0)
        w.MoveTo(3,2)
        checkersgame.assertBoardEquals([
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','W','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        # Check we can capture multiple pieces
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','','','','',''],
                                  ['','','B','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','B','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w = checkersgame.GetPieceAt(1, 0)
        w.MoveTo(3,2)
        checkersgame.assertBoardEquals([
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','W','','','',''],
                                  ['','','B','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        w.MoveTo(1,4)
        checkersgame.assertBoardEquals([
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','W','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])


    
class CheckersBoardVictoryConditionTestCase(unittest.TestCase):     
    def runTest(self):
        # If all of the other players pieces are gone we have won
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        self.assertTrue(checkersgame.HasPlayerWon("W"))
        self.assertFalse(checkersgame.HasPlayerWon("B"))

        # If all of the other players pieces are gone we have won
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','',''],
                                  ['','','B','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        self.assertFalse(checkersgame.HasPlayerWon("W"))
        self.assertTrue(checkersgame.HasPlayerWon("B"))

        # A player has lost if they have no move available
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','','','','','','','W'],
                                  ['','','','','','','B',''],
                                  ['','','','','','B','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ])
        self.assertFalse(checkersgame.HasPlayerWon("W"))
        self.assertTrue(checkersgame.HasPlayerWon("B"))

        # If both players have moves available no body has won
        checkersgame = CheckersGame(None)
        checkersgame.CreateBoard([['','W','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','','','','','',''],
                                  ['','','B','','','','',''],
                                  ])
        self.assertFalse(checkersgame.HasPlayerWon("W"))
        self.assertFalse(checkersgame.HasPlayerWon("B"))

class ReloadAppTestCase(unittest.TestCase):
    def setUp(self):
        testingmailserver.ResetMailDict()
        utils.setup_app_dir("/run/shm/demux1")
        self.demux1 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:', appdir = "/run/shm/demux1")

    def runTest(self):

        app1 = CoversApp(self.demux1)

        self.demux1.RegisterApp(app1)

        dc1 = app1.CreateNewDocumentCollection(None)
        app1.SaveAndKeepUpToDate(dc1, "/run/shm/demux1")
        test_a = TestPropertyOwner1(None)
        test_a.covers = 1
        dc1.AddDocumentObject(test_a)
        test_b = TestPropertyOwner1(None)
        test_b.covers = 10
        dc1.AddDocumentObject(test_b)
        app1.SaveDC(dc1, "/run/shm/demux1")

        time.sleep(0.5)

        demux2 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:', appdir = "/run/shm/demux1")


        app2 = CoversApp(demux2)

        demux2.RegisterApp(app2)

        self.assertEqual(len(app2.GetDocumentCollections()), 1)
        dc2 = app2.GetDocumentCollections()[0]

        self.assertEqual(len(dc2.objects[TestPropertyOwner1.__name__]), 2)
        test_a2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_a.id)
        test_b2 = dc2.GetObjectByID(TestPropertyOwner1.__name__, test_b.id)
        
        self.assertEqual(test_a.id, test_a2.id)
        self.assertEqual(test_a.covers, test_a2.covers)
        self.assertEqual(test_b.id, test_b2.id)
        self.assertEqual(test_b.covers, test_b2.covers)


class ShareAndReloadCheckersGameTestCase(unittest.TestCase):
    def setUp(self):
        testingmailserver.ResetMailDict()
        utils.setup_app_dir("/run/shm/demux1")
        utils.setup_app_dir("/run/shm/demux2")
        self.demux1 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:', appdir = "/run/shm/demux1")
        self.demux2 = Demux(myemail='mlockett2@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett2',smtppass='',
                       popuser='mlockett2',poppass='',popport=10026, popserver='localhost', fromfile=':memory:', appdir = "/run/shm/demux2")
        message = """
Frist post!!!!!!

"""

        self.demux1.SendPlainEmail(receivers = ['mlockett2@livewire.io'], subject = "SMTP e-mail test", message=message)

        messages = self.demux1.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 0)

        time.sleep(0.01) #Give background thread a chance to run
        
        self.demux2.CheckEmail()

        messages = self.demux2.messagestore.GetMessages()
        self.assertEqual(len(list(messages)), 1)
        message = messages[0]
        self.assertTrue(message.senderislivewireenabled) # Sender is not livewire enabled

        #mlockett2 now knows that mlockett1 is livewire enabled The demux should have already sent to mlockett1 our public key
        
        time.sleep(0.01) #Give background thread a chance to run
        
        messages = self.demux1.messagestore.GetMessages()

        self.assertEqual(len(list(messages)), 0)

        self.demux1.CheckEmail() #Demux 1 should receive a message from demux2 and recognise it is livewire enabled and get the public key

        contacts = self.demux1.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertTrue(contacts[0].islivewire)
        self.assertEqual(contacts[0].publickey, self.demux2.key.publickey().exportKey("PEM"))

        time.sleep(0.01) #Give background thread a chance to run

        self.demux2.CheckEmail() #Demux 2 should receive a message from demux1 with it's public key

        #Each demux should now have the 

        contacts = self.demux2.contactstore.GetContacts()

        self.assertEqual(len(list(contacts)), 1)
        self.assertEqual(contacts[0].publickey, self.demux1.key.publickey().exportKey("PEM") )
        self.assertTrue(contacts[0].islivewire)

    def runTest(self):
        app1 = CheckersApp(self.demux1)
        app2 = CheckersApp(self.demux2)

        self.demux1.RegisterApp(app1)
        self.demux2.RegisterApp(app2)

        dc1 = app1.CreateNewDocumentCollection(None)
        app1.SaveAndKeepUpToDate(dc1, "/run/shm/demux1")
        app1.Share(dc1, 'mlockett2@livewire.io')

        checkersgame = CheckersGame(None)
        dc1.AddDocumentObject(checkersgame)
        checkersgame.CreateDefaultStartBoard()
        self.assertEqual(len(checkersgame.history.edgesbyendnode), 120)

        self.assertEqual(checkersgame.GetTurnColour(), "W")

        #Test the default board is laid out correctly
        for y in range(8):
            for x in range(8):
                if ((x + y) % 2) == 0:
                    self.assertIs(checkersgame.GetPieceAt(x,y), None)
                else:
                    p = checkersgame.GetPieceAt(x,y)
                    if y <= 2:
                        self.assertEqual(p.pieceside, "W")
                        self.assertEqual(p.piecetype, "")
                    elif y >= 5:
                        self.assertEqual(p.pieceside, "B")
                        self.assertEqual(p.piecetype, "")
                    else:
                        self.assertIs(p, None)

        self.assertEqual(len(dc1.objects[CheckersGame.__name__]), 1)

        app1.SaveDC(dc1, "/run/shm/demux1")

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()

        dc2 = app2.GetDocumentCollectionByID(dc1.id)
        checkersgame2 = dc2.GetObjectByID(CheckersGame.__name__, checkersgame.id)
        self.assertEqual(len(checkersgame2.history.edgesbyendnode), 120)
        app2.SaveAndKeepUpToDate(dc2, "/run/shm/demux2")

        self.assertEqual(len(dc2.objects[CheckersGame.__name__]), 1)
        checkersgame2 = dc2.GetObjectByID(CheckersGame.__name__, checkersgame.id)
        self.assertEqual(len(checkersgame2.history.edgesbyendnode), 120)

        self.assertEqual(checkersgame2.GetTurnColour(), "W")

        #print "All pieces = " + str([(p.x, p.y) for p in checkersgame2.pieces])

        #Test the default board is laid out correctly
        for y in range(8):
            for x in range(8):
                if ((x + y) % 2) == 0:
                    self.assertIs(checkersgame2.GetPieceAt(x,y), None, "x = " + str(x) + ", y = " + str(y))
                else:
                    p = checkersgame2.GetPieceAt(x,y)
                    if y <= 2:
                        self.assertEqual(p.pieceside, "W", "x = " + str(x) + ", y = " + str(y))
                        self.assertEqual(p.piecetype, "", "x = " + str(x) + ", y = " + str(y))
                    elif y >= 5:
                        self.assertEqual(p.pieceside, "B", "x = " + str(x) + ", y = " + str(y))
                        self.assertEqual(p.piecetype, "", "x = " + str(x) + ", y = " + str(y))
                    else:
                        self.assertIs(p, None)

        #Test the default board is laid out correctly
        for y in range(8):
            for x in range(8):
                if ((x + y) % 2) == 0:
                    self.assertIs(checkersgame2.GetPieceAt(x,y), None)
                else:
                    p = checkersgame2.GetPieceAt(x,y)
                    if y <= 2:
                        self.assertEqual(p.pieceside, "W")
                        self.assertEqual(p.piecetype, "")
                    elif y >= 5:
                        self.assertEqual(p.pieceside, "B")
                        self.assertEqual(p.piecetype, "")
                    else:
                        self.assertIs(p, None)

        w = checkersgame.GetPieceAt(1, 2)
        w.MoveTo(2,3)
        self.assertEqual(len(checkersgame.history.edgesbyendnode), 122)
        checkersgame.turn.add(1)
        self.assertEqual(len(checkersgame.history.edgesbyendnode), 123)
        checkersgame.assertBoardEquals([
                                  ['','W','','W','','W','','W'],
                                  ['W','','W','','W','','W',''],
                                  ['','','','W','','W','','W'],
                                  ['','','W','','','','',''],
                                  ['','','','','','','',''],
                                  ['B','','B','','B','','B',''],
                                  ['','B','','B','','B','','B'],
                                  ['B','','B','','B','','B',''],
                                  ])

        self.assertEqual(checkersgame.GetTurnColour(), "B")

        time.sleep(0.01) #Give the email a chance to send
        self.demux2.CheckEmail()

        self.assertEqual(len(app2.GetDocumentCollections()), 1)
        dc2 = app2.GetDocumentCollections()[0]
        games = dc2.GetByClass(CheckersGame)
        self.assertEqual(len(games), 1)

        checkersgame2 = games[0]
        self.assertEqual(len(checkersgame2.history.edgesbyendnode), 123)

        app2.SaveDC(dc2, "/run/shm/demux2")

        time.sleep(1)

        demux2 = Demux(myemail='mlockett1@livewire.io', smtpserver='localhost',smtpport=10025,smtpuser='mlockett1',smtppass='',
                       popuser='mlockett1',poppass='',popport=10026, popserver='localhost', fromfile=':memory:', appdir = "/run/shm/demux2")


        time.sleep(1)
        #print "Reloading"

        app2 = CheckersApp(demux2)


        demux2.RegisterApp(app2)

        self.assertEqual(len(app2.GetDocumentCollections()), 1)
        dc2 = app2.GetDocumentCollections()[0]
        games = dc2.GetByClass(CheckersGame)
        self.assertEqual(len(games), 1)

        #print "dc2.objects=",dc2.objects

        #self.assertEqual(len(dc2.objects[CheckersGame.__name__]), 1)
        #checkersgame2 = dc2.GetObjectByID(CheckersGame.__name__, checkersgame.id)
        checkersgame2 = games[0]
        self.assertEqual(len(checkersgame2.history.edgesbyendnode), 123)

        self.assertEqual(checkersgame2.GetTurnColour(), "B")

        currentpieces2 = [(t.x, t.y, t.id) for t in checkersgame2.GetCurrentPieces().values()]
        #print "currentpieces2 = " + str(currentpieces2)
        checkersgame2.assertBoardEquals([
                                  ['','W','','W','','W','','W'],
                                  ['W','','W','','W','','W',''],
                                  ['','','','W','','W','','W'],
                                  ['','','W','','','','',''],
                                  ['','','','','','','',''],
                                  ['B','','B','','B','','B',''],
                                  ['','B','','B','','B','','B'],
                                  ['B','','B','','B','','B',''],
                                  ])















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
    smtplib.testingmode = True
    poplib.testingmode = True

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
    suite.addTest(FreezeTestCase())
    suite.addTest(LargeMergeTestCase())
    suite.addTest(FreezeThreeWayMergeTestCase())
    suite.addTest(ImmutableClassTestCase())
    suite.addTest(StoreImmutableObjectsInJSONTestCase())
    suite.addTest(StoreImmutableObjectsInDatabaseTestCase())
    suite.addTest(SimpleCoversUpdateTestCase())
    suite.addTest(FreezeUpdateTestCase())

    suite.addTest(SimpleCounterTestCase())
    suite.addTest(MergeCounterTestCase())
    suite.addTest(MergeCounterChangesMadeInJSONTestCase())

    suite.addTest(FastSettingChangeValueTestCase())
    suite.addTest(FastSettingAccessFunctionsTestCase())
    suite.addTest(AddSettingToSettingStoreTestCase())
    suite.addTest(AddMessageDoesNotDuplicateContacts())
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

    suite.addTest(CheckersBoardSquareColourTestCase())
    suite.addTest(CheckersBoardInitialValidityTestCase())
    suite.addTest(CheckersBoardValidMovesTestCase())
    suite.addTest(CheckersBoardVictoryConditionTestCase())

    suite.addTest(StartTestingMailServerDummyTest())
    suite.addTest(SendAndReceiveUnencryptedEmail())
    suite.addTest(SendAndReceiveEncryptedEmail())
    suite.addTest(EstablishLivewireEncryptedLink())
    suite.addTest(EstablishLivewireEncryptedLinkUsingDemux())
    suite.addTest(EstablishLivewireEncryptedLinkUsingDemuxExistingContact())

    suite.addTest(DemuxTestCase())
    suite.addTest(DemuxEdgeAuthenticationTestCase())

    #Next two test comment due to timing related non deterministric failures also they run slow
    suite.addTest(ReloadAppTestCase())

    suite.addTest(ShareAndReloadCheckersGameTestCase())
    suite.addTest(StopTestingMailServerDummyTest())

    suite.addTest(DemuxCanSaveAndLoadTestCase())

    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
 
    
    

    

