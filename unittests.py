import sys
sys.path.insert(0, '/home/mark/code/livewirepy/doop')

import unittest
from Document import Document
from FieldInt import FieldInt
from DocumentObject import DocumentObject
from FieldList import FieldList
import uuid

class Covers(Document):
    def __init__(self, id):
        super(Covers, self).__init__(id)
    covers = FieldInt()

class SimpleCoversTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def runTest(self):
        #Test merging together simple covers documents
        test = Covers(None)
        test.covers = 1
        #Test we can set a value
        assert test.covers == 1
        test2 = Covers(test.id)
        test.history.Replay(test2)
        #Test we can rebuild a simple object by playing an edge
        assert test2.covers == 1
        #Test these are just the same history object but it was actually copied
        assert test.history is not test2.history
        
        test3 = test2.Clone()
        #Test the clone is the same as the original. But not just refering to the same object
        assert test3.covers == test2.covers
        assert test2 is not test3
        assert test2.history is not test3.history
        
        test = Covers(None)
        test.covers = 1
        test.covers = 2
        test2 = Covers(test.id)
        test.history.Replay(test2)
        assert test.covers == 2
        assert test.history is not test2.history
        assert test is not test2
    
class MergeHistoryCoverTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def runTest(self):
        #Test merge together two simple covers objects
        test = Covers(None)
        test.covers = 1
        test2 = test.Clone()
        test.covers = 2
        test2.covers = 3
        test3 = test.Merge(test2)
        #In a merge conflict between two integers the greater one is the winner
        assert test3.covers == 3

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
        pass

    def runTest(self):
        #Test that various types of changes create was changed events
        test1 = TestPropertyOwner1(None)
        test1.bWasChanged = False
        test2 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(test2)
        assert test1.bWasChanged == True
        test1.bWasChanged = False
        test2.cover = 1
        assert test1.bWasChanged == True
        test1.bWasChanged = False
        test2.cover = 1
        assert test1.bWasChanged == True
        test1.propertyowner2s.remove(test2.id)
        assert len(test1.propertyowner2s) == 0

class SimpleItemTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def runTest(self):
        test1 = TestPropertyOwner1(None)
        testitem = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem)
        testitem.cover = 1
        #Test semantics for retriving objects
        assert len(test1.propertyowner2s) == 1
        for po2 in test1.propertyowner2s:
            assert po2.__class__.__name__ == TestPropertyOwner2.__name__
            assert po2.cover == 1

        test1 = TestPropertyOwner1(None)
        testitem = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem)
        testitem.cover = 1
        test1.propertyowner2s.remove(testitem.id)

        test2 = TestPropertyOwner1(test1.id)
        test1.history.Replay(test2)

        #Check that replaying correctly removes the object
        assert len(test2.propertyowner2s) == 0

        test1 = TestPropertyOwner1(None)
        testitem = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem)
        testitem.cover = 1
        test2 = test1.Clone()
        
        assert len(test2.propertyowner2s) == 1
        for po2 in test2.propertyowner2s:
            assert po2.__class__.__name__ == TestPropertyOwner2.__name__
            assert po2.cover == 1

class AdvancedItemTestCase(unittest.TestCase):
    def setUp(self):
        pass

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
        assert len(test3.propertyowner2s) == 0

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
        assert len(test3.propertyowner2s) == 0

        #Test merging changes to different objects in the same document works
        test1 = TestPropertyOwner1(None)
        testitem1 = TestPropertyOwner2(None)
        test1.propertyowner2s.add(testitem1)
        test2 = test1.Clone()
        testitem1.cover = 3
        test2.covers=2
        test3 = test2.Merge(test1)
        assert len(test1.propertyowner2s) == 1
        for item1 in test1.propertyowner2s:
            assert item1.cover == 3
        assert test3.covers == 2

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
        assert testitem2.cover == 3
        assert testitem2.quantity == 2
        assert testitem1.cover == 2
        assert testitem1.quantity == 3
        
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
        assert testitem2.cover == 3
        assert testitem2.quantity == 2
        assert testitem1.cover == 2
        assert testitem1.quantity == 3
    
    
def suite():
    suite = unittest.TestSuite()
    suite.addTest(SimpleCoversTestCase())
    suite.addTest(MergeHistoryCoverTestCase())
    suite.addTest(ListItemChangeHistoryTestCase())
    suite.addTest(SimpleItemTestCase())
    suite.addTest(AdvancedItemTestCase())
    
    return suite


runner = unittest.TextTestRunner()
runner.run(suite())
 
    
    

    
