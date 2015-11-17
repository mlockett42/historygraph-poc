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
    #suite.addTest(SendAndReceiveUnencryptedEmail())
    
    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
 
    
    

    
