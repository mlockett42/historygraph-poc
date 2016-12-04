from historygraph import DocumentCollection
from collections import defaultdict
import uuid
from json import JSONEncoder, JSONDecoder
import DocumentCollectionHelper
import os
import utils

class App(object):
    #A livewire app. A thing that shall send and receive edges

    def __init__(self, demux):
        self.dcdict = dict()
        self.demux = demux
        self.shares = defaultdict(list)
        self.saveddcs = set()

    def CreateNewDocumentCollection(self, dcid):
        dc = DocumentCollection()
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

    def HasDocumentCollection(self, id):
        return id in self.dcdict

    def GetDocumentCollections(self):
        return [v for (k,v) in self.dcdict.iteritems()]

    def AddDocumentObject(self, dc, obj):
        if dc.id in self.saveddcs:
            self.SaveAndKeepUpToDate(dc, self.loaddir)

    def UpdateShares(self):
        #utils.log_output("Update shares called")
        #Resend to all of our sharees
        for dc in self.dcdict.values():
            #utils.log_output("Updating share for " + str(dc.id))
            shares = self.shares[dc.id]
            (historyedges, immutableobjects) = dc.getAllEdges()
            if len(shares) > 0:
                #l = [a.asTuple() for a in edges]
                #utils.log_output("EdgesAdded l = ",l)
                l = JSONEncoder().encode({"history":historyedges,"immutableobjects":immutableobjects})
                for emailaddress in shares:
                    #utils.log_output("Update share " + emailaddress + " for dc = " + dc.id)
                    message = self.demux.GetEncodedMessage({"id":str(uuid.uuid4()),"class":"edges","email": emailaddress,
                        "appname":self.__class__.__name__,"dcid":dc.id,"edges":l})
                    #utils.log_output("Sending shares email edge l = ", l)
                    self.demux.SendPlainEmail([emailaddress], "Livewire encoded message", message)


    def EdgesAdded(self, dc, edges):
        """
        shares = self.shares[dc.id]
        if len(shares) > 0:
            l = [a.asTuple() for a in edges]
            #utils.log_output("EdgesAdded l = ",l)
            l = JSONEncoder().encode({"history":l,"immutableobjects":[]})
            for emailaddress in shares:
                message = self.demux.GetEncodedMessage({"id":str(uuid.uuid4()),"class":"edges","email": emailaddress,
                    "appname":self.__class__.__name__,"dcid":dc.id,"edges":l})
                self.demux.SendPlainEmail([emailaddress], "Livewire encoded message", message)
        """
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
        saveddcs = self.saveddcs
        self.saveddcs = set()
        #print "LoadDocumentCollectionFromDisk Looking for files in " + loaddir
        for filename in os.listdir(loaddir):
            #print "LoadDocumentCollectionFromDisk Found file " + filename
            if filename.endswith(".history.db") and filename.startswith(self.__class__.__name__): 
                dcid = filename[len(self.__class__.__name__):-len(".history.db")]
                dc = self.CreateNewDocumentCollection(dcid)
                DocumentCollectionHelper.LoadDocumentCollection(dc, os.path.join(loaddir, filename), os.path.join(loaddir, filename.replace('.history.', '.content.')))
        self.saveddcs = saveddcs
        
    def SaveAndKeepUpToDate(self, dc, loaddir):
        pass
        #self.loaddir = loaddir
        #self.saveddcs.add(dc.id)
        #DocumentCollectionHelper.SaveDocumentCollection(dc, os.path.join(loaddir, self.__class__.__name__ + dc.id + '.history.db'),
        #                                                os.path.join(loaddir, self.__class__.__name__ + dc.id + '.content.db'))

    def SaveDC(self, dc, loaddir):
        DocumentCollectionHelper.SaveDocumentCollection(dc, os.path.join(loaddir, self.__class__.__name__ + dc.id + '.history.db'),
                                                        os.path.join(loaddir, self.__class__.__name__ + dc.id + '.content.db'))

    def SaveAllDCs(self):
        loaddir = self.demux.appdir
        for dc in self.dcdict.values():
            #utils.log_output("app.py SaveALlDCs saving dc.id=",dc.id)
            #os.remove(os.path.join(loaddir, self.__class__.__name__ + dc.id + '.history.db'))
            #os.remove(os.path.join(loaddir, self.__class__.__name__ + dc.id + '.content.db'))
            DocumentCollectionHelper.SaveDocumentCollection(dc, os.path.join(loaddir, self.__class__.__name__ + dc.id + '.history.db'),
                                                            os.path.join(loaddir, self.__class__.__name__ + dc.id + '.content.db'))
            

