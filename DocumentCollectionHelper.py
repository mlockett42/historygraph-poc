#DocumentCollectionHelper.py
# A collection of functions that work with DocumentCollections and do thing not available in pyjs

import sqlite3
import os
from collections import defaultdict
from historygraph import HistoryEdge
from historygraph import HistoryGraph
from historygraph import FieldCollection
from historygraph import FieldIntRegister
from historygraph import DocumentObject
from historygraph import ImmutableObject
from historygraph import FieldIntCounter
from historygraph import FieldList
from historygraph import Document

def SaveDocumentCollection(dc, filenameedges, filenamedata):
    try:
        os.remove(filenameedges)
    except:
        pass
    c = sqlite3.connect(filenameedges)
    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS edge (
                    documentid text, 
                    documentclassname text, 
                    edgeclassname text, 
                    endnodeid text, 
                    startnode1id text, 
                    startnode2id text, 
                    propertyownerid text, 
                    propertyname text, 
                    propertyvalue text, 
                    propertytype text
                )''')
    c.execute("DELETE FROM edge")
    for classname in dc.objects:
        if issubclass(dc.classes[classname], Document):
            documentdict = dc.objects[classname]
            for (documentid, document) in documentdict.iteritems():
                history = document.history
                for edgeid in history.edgesbyendnode:
                    edge = history.edgesbyendnode[edgeid]
                    startnodes = list(edge.startnodes)
                    if len(edge.startnodes) == 1:
                        startnode1id = startnodes[0]
                        startnode2id = ""
                    elif len(edge.startnodes) == 2:
                        startnode1id = startnodes[0]
                        startnode2id = startnodes[1]
                    else:
                        assert False
                    
                    if edge.propertytype is None:
                        propertytypename = ""
                    else:
                        propertytypename = edge.propertytype
                    c.execute("INSERT INTO edge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (document.id, document.__class__.__name__, 
                        edge.__class__.__name__, edge.GetEndNode(), startnode1id, startnode2id, edge.propertyownerid, edge.propertyname,
                        edge.propertyvalue, propertytypename))

    c.commit()
    c.close()

    try:
        os.remove(filenamedata)
    except:
        pass
    database = sqlite3.connect(filenamedata)
    foreignkeydict = defaultdict(list)
    for classname in dc.classes:
        theclass = dc.classes[classname]
        variables = [a for a in dir(theclass) if not a.startswith('__') and not callable(getattr(theclass,a))]
        for a in variables:
            if isinstance(getattr(theclass, a), FieldCollection) or isinstance(getattr(theclass, a), FieldList):
                foreignkeydict[getattr(theclass, a).theclass.__name__].append((classname, a, isinstance(getattr(theclass, a), FieldList)))
    columndict = defaultdict(list)
    for classname in dc.classes:
        theclass = dc.classes[classname]
        variables = [a for a in dir(theclass) if not a.startswith('__') and not callable(getattr(theclass,a))]
        for a in variables:
            if isinstance(getattr(theclass, a), FieldCollection) == False and isinstance(getattr(theclass, a), FieldList) == False:
                columndict[classname].append((a, "int" if isinstance(getattr(theclass, a), FieldIntRegister) else "text"))
    for k in foreignkeydict:
        for (classname, a, isfieldlist) in foreignkeydict[k]:
            columndict[k].append((classname + "id", "text"))
            if isfieldlist:
                columndict[k].append((classname + "order", "int"))
    for classname in columndict:
        columnlist = columndict[classname]
        sql = "CREATE TABLE " + classname + " (id text "
        for (a, thetype) in columnlist:
            sql += ","
            sql += a + " " + thetype
        sql += ")"

        database.execute(sql)
    
    already_saved = set()
    for documentid in dc.objects:
        objlist = [obj for (objid, obj) in dc.objects[documentid].iteritems() if (isinstance(obj, Document) or isinstance(obj, ImmutableObject))]
        for obj in objlist:
            if isinstance(obj, ImmutableObject):
                SaveDocumentObject(database, obj, None, foreignkeydict, columndict, None)
            else:
                SaveDocumentObject(database, obj, obj.GetDocument(), foreignkeydict, columndict, None)

    database.commit()
    database.close()

def SaveDocumentObject(database, documentobject, parentobject, foreignkeydict, columndict, order):
    variables = [a for a in dir(documentobject.__class__) if not a.startswith('__') and not callable(getattr(documentobject.__class__,a))]
    for a in variables:
        if isinstance(getattr(documentobject.__class__, a), FieldCollection) or isinstance(getattr(documentobject.__class__, a), FieldList):
            order2 = 0
            for childobj in getattr(documentobject, a):
                SaveDocumentObject(database, childobj, documentobject, foreignkeydict, columndict, order2)
                order2 += 1
    foreignkeyclassname = ""
    isfieldlist = False
    if documentobject.__class__.__name__ in foreignkeydict:
        if len(foreignkeydict[documentobject.__class__.__name__]) == 0:
            pass #No foreign keys to worry about
        elif len(foreignkeydict[documentobject.__class__.__name__]) == 1:
            (foreignkeyclassname, a, isfieldlist) = foreignkeydict[documentobject.__class__.__name__][0]
        else:
            assert False #Only one foreign key allowed
    sql = "INSERT INTO " + documentobject.__class__.__name__ + " VALUES (?"
    values = list()
    for (columnname, columntype) in columndict[documentobject.__class__.__name__]:
        sql += ",?"
        
        if foreignkeyclassname != "" and foreignkeyclassname + "id" == columnname:
            values.append(parentobject.id)
        elif foreignkeyclassname != "" and foreignkeyclassname + "order" == columnname and isfieldlist:
            values.append(order)
        elif type(getattr(documentobject, columnname)) == FieldIntCounter.FieldIntCounterImpl:
            values.append(getattr(documentobject, columnname).value)
        else:
            values.append(getattr(documentobject, columnname))
    sql += ")"
    if isinstance(documentobject, DocumentObject):
        #print "values=",values
        #print "type(values)=",type(values)
        #print "tuple([documentobject.id] + values)=",tuple([documentobject.id] + values)
        database.execute(sql, tuple([documentobject.id] + values))
    elif isinstance(documentobject, ImmutableObject):
        database.execute(sql, tuple([documentobject.GetHash()] + values))
    else:
        assert False


def GetSQLObjects(documentcollection, filenamedata, query):
    database = sqlite3.connect(filenamedata)
    ret = list()
    cur = database.cursor()    
    cur.execute(query)

    rows = cur.fetchall()
    for row in rows:
        for classname in documentcollection.objects:
            for (objid, obj) in documentcollection.objects[classname].iteritems():
                if isinstance(obj, DocumentObject):
                    if obj.id == row[0]:
                        ret.append(obj)
                elif isinstance(obj, ImmutableObject):
                    if obj.GetHash() == row[0]:
                        ret.append(obj)
                else:
                    assert False
    return ret
        
def LoadDocumentCollection(dc, filenameedges, filenamedata):
    dc.objects = defaultdict(dict)
    #dc.classes = dict()
    dc.historyedgeclasses = dict()
    for theclass in HistoryEdge.__subclasses__():
        dc.historyedgeclasses[theclass.__name__] = theclass

    c = sqlite3.connect(filenameedges)
    cur = c.cursor()    
    c.execute('''CREATE TABLE IF NOT EXISTS edge (
                    documentid text, 
                    documentclassname text, 
                    edgeclassname text, 
                    endnodeid text PRIMARY KEY, 
                    startnode1id text, 
                    startnode2id text, 
                    propertyownerid text, 
                    propertyname text, 
                    propertyvalue text, 
                    propertytype text
                )''')
    c.commit()
    cur.execute("SELECT documentid, documentclassname, edgeclassname, endnodeid, startnode1id, startnode2id, propertyownerid, propertyname, propertyvalue, propertytype FROM edge")

    historygraphdict = defaultdict(HistoryGraph)
    documentclassnamedict = dict()

    rows = cur.fetchall()
    for row in rows:
        documentid = str(row[0])
        documentclassname = str(row[1])
        edgeclassname = str(row[2])
        endnodeid = str(row[3])
        startnode1id = str(row[4])
        startnode2id = str(row[5])
        propertyownerid = str(row[6])
        propertyname = str(row[7])
        propertyvaluestr = str(row[8])
        propertytypestr = str(row[9])

        if documentid in historygraphdict:
            historygraph = historygraphdict[documentid]
        else:
            historygraph = HistoryGraph()
            historygraphdict[documentid] = historygraph
            documentclassnamedict[documentid] = documentclassname
        if propertytypestr == "FieldIntRegister" or propertytypestr == "FieldIntCounter" or propertytypestr == "int":
            propertytype = int
            propertyvalue = int(propertyvaluestr)
        elif propertytypestr == "FieldText" or propertytypestr == "basestring":
            propertytype = basestring
            propertyvalue = str(propertyvaluestr)
        elif propertytypestr == "" and edgeclassname == "HistoryEdgeNull":
            propertytype = None
            propertyvalue = ""
        else:
            propertytype = dc.classes[propertytypestr]
            propertyvalue = propertyvaluestr
        documentclassnamedict[documentid] = documentclassname
        if startnode2id == "":
            startnodes = {startnode1id}
        else:
            startnodes = {startnode1id, startnode2id}
        edge = dc.historyedgeclasses[edgeclassname](startnodes, propertyownerid, propertyname, propertyvalue, propertytypestr, documentid, documentclassname)
        history = historygraphdict[documentid]
        history.AddEdges([edge])

    #nulledges = list()
    for documentid in historygraphdict:
        #print "Creating doc id = ",documentid
        doc = dc.classes[documentclassnamedict[documentid]](documentid)
        doc.dc = dc
        history = historygraphdict[documentid]
        #print ("len(history.edgesbyendnode)=",len(history.edgesbyendnode))
    #    nulledges.extend(history.MergeDanglingBranches())
        history.RecordPastEdges()
        history.ProcessConflictWinners()
        history.Replay(doc)
        dc.AddDocumentObject(doc)
    #
    #SaveEdges(dc, filenameedges, nulledges)

    #Load all of the immutable objects

    c = sqlite3.connect(filenamedata) #Return the database that can used for get sql objects

    for (classname, theclass) in dc.classes.iteritems():
        if issubclass(theclass, ImmutableObject):
            variables = [a for a in dir(theclass) if not a.startswith('__') and not callable(getattr(theclass,a))]
            sql = "SELECT id"
            for v in variables:
                sql += ", " + v
            sql += " FROM " + theclass.__name__.lower()

            cur = c.cursor()    
            cur.execute(sql)

            rows = cur.fetchall()
            d = dict()
            for row in rows:
                for i in range(len(variables)):
                    d[variables[i]] = row[i + 1]
                obj = theclass(**d)
                assert obj.GetHash() == row[0]
                dc.AddImmutableObject(obj)

    return c
