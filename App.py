import DocumentCollection
from collections import defaultdict
import uuid
from json import JSONEncoder, JSONDecoder
import DocumentCollectionHelper
import os

class App(object):
    #A livewire app. A thing that shall send and receive edges

    def __init__(self, demux):
        self.dcdict = dict()
        self.demux = demux
        self.shares = defaultdict(list)
        self.saveddcs = set()

    def CreateNewDocumentCollection(self, dcid):
        dc = DocumentCollection.DocumentCollection()
        if dcid is not None:
            dc.id = dcid
        self.dcdict[dc.id] = dc
        dc.AddListener(self)
        
        return dc

    def Share(self, dc1, emailaddress):
        self.shares[dc1.id].append(emailaddress)
        message = self.demux.GetEncodedMessage({"id":str(uuid.uuid4()),"class":"createdocumentcollection","email": emailaddress,
            "appname":self.__class__.__name__,"dcid":dc1.id,"dcjson":dc1.asJSON()})

        #print "Share message = ",message
        self.demux.SendPlainEmail([emailaddress], "Livewire encoded message", message)

    def GetDocumentCollectionByID(self, id):
        return self.dcdict[id]

    def GetDocumentCollections(self):
        return [v for (k,v) in self.dcdict.iteritems()]

    def AddDocumentObject(self, dc, obj):
        if dc.id in self.saveddcs:
            self.SaveAndKeepUpToDate(dc, self.loaddir)

    def EdgesAdded(self, dc, edges):
        shares = self.shares[dc.id]
        if len(shares) > 0:
            l = [a.asTuple() for a in edges]
            l = JSONEncoder().encode({"history":l,"immutableobjects":[]})
            for emailaddress in shares:
                message = self.demux.GetEncodedMessage({"id":str(uuid.uuid4()),"class":"edges","email": emailaddress,
                    "appname":self.__class__.__name__,"dcid":dc.id,"edges":l})
                self.demux.SendPlainEmail([emailaddress], "Livewire encoded message", message)
        if dc.id in self.saveddcs:
            self.SaveAndKeepUpToDate(dc, self.loaddir)

    def ImmutableObjectAdded(self, dc, obj):
        shares = self.shares[dc.id]
        if len(shares) > 0:
            d = obj.asDict()
            for emailaddress in shares:
                message = self.demux.GetEncodedMessage({"id":str(uuid.uuid4()),"class":"immutableobject","email": emailaddress,
                    "appname":self.__class__.__name__,"dcid":dc.id,"immutableobject":d})
                self.demux.SendPlainEmail([emailaddress], "Livewire encoded message", message)
        if dc.id in self.saveddcs:
            self.SaveAndKeepUpToDate(dc, self.loaddir)
        
    def LoadDocumentCollectionFromDisk(self, loaddir):
        for filename in os.listdir(loaddir):
            if filename.endswith(".history.db") or filename.startswith(self.__class__.__name__): 
                dcid = filename[len(self.__class__.__name__):-len(".history.db")]
                dc = self.CreateNewDocumentCollection(dcid)
                DocumentCollectionHelper.LoadDocumentCollection(dc, os.path.join(loaddir, filename), os.path.join(loaddir, filename.replace('.history.', '.content.')))

        
    def SaveAndKeepUpToDate(self, dc, loaddir):
        self.loaddir = loaddir
        self.saveddcs.add(dc.id)
        DocumentCollectionHelper.SaveDocumentCollection(dc, os.path.join(loaddir, self.__class__.__name__ + dc.id + '.history.db'),
                                                        os.path.join(loaddir, self.__class__.__name__ + dc.id + '.content.db'))

