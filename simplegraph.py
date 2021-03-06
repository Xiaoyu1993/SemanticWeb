#!/usr/bin/env python
# coding: utf-8

# In[2]:
import csv

class SimpleGraph:
    def __init__(self):
        self._spo = {}
        self._pos = {}
        self._osp = {}
        # instantiated a new triple: 
        # self._pos = {predicate:{object:set([subject])}}
        # notice the order of p,o,s on the right side of the equation
        # query for triple: 
        # for subject in self._pos[predicate][object]: 
        #     yield (subject, predicate, object)
        
    # permutes the subject, predicate, and object to match the ordering of each index
    def add(self, (sub, pred, obj)):
        self._addToIndex(self._spo, sub, pred, obj)
        self._addToIndex(self._pos, pred, obj, sub)
        self._addToIndex(self._osp, obj, sub, pred)
        
    # add the terms to the index, creating a dictionary and set if the terms are not already in the index
    def _addToIndex(self, index, a, b, c):
        if a not in index: index[a] = {b:set([c])}
        else:
            if b not in index[a]: index[a][b] = set([c])
            else: index[a][b].add(c)
                
    # find all triples that match a pattern, permutes them, and removes them from each index
    def remove(self, (sub, pred, obj)):
        triples = list(self.triples((sub, pred, obj)))
        for(delSub, delPred, delObj) in triples:
            self._removeFromIndex(self._spo, delSub, delPred, delObj)
            self._removeFromIndex(self._pos, delPred, delObj, delSub)
            self._removeFromIndex(self._osp, delObj, delSub, delPred)
      
    # walk down the index, cleaning up empty intermediate dictionaries and sets while removing the terms of the triple
    def _removeFromIndex(self, index, a, b, c):
        try:
            bs = index[a]
            cset = bs[b]
            cset.remove(c)
            if len(cset) == 0:del bs[b]
            if len(bs) == 0: del index[a]
        # KeyErrors occur if a term was missing, which means that it wasn't a valid delete:
        except KeyError:
            pass  
        
    # load the triples in the graph to comma-separated file
    def load(self, filename):
        f = open(filename, "rb")
        reader = csv.reader(f)
        for sub, pred, obj in reader:
            sub = unicode(sub, "UTF-8")
            pred = unicode(pred, "UTF-8")
            obj = unicode(obj, "UTF-8")
            self.add((sub, pred, obj))
        f.close()
    
    # save the triples in the graph to comma-separated file
    def save(self, filename):
        f = open(filename, "wb")
        writer = csv.writer(f)
        for sub, pred, obj in self.triples((None, None, None)):
            writer,writerow([sub.encode("UTF-8"),
                            pred.encode("UTF-8"),
                            obj.encode("UTF-8")])
        f.close()
        
    # take a (subject, predicate, object) pattern and returns all triples that match the pattern
    def triples(self, (sub, pred, obj)):
        #check which terms are present in order to use the correct index
        try:
            if sub != None:
                if pred != None:
                    # sub pred obj
                    if obj != None:
                        if obj in self._spo[sub][pred]:
                            yield (sub, pred, obj)
                    # sub pred None
                    else:
                        for retObj in self._spo[sub][pred]:
                            yield (sub, pred, retObj)
                else:
                    #sub None obj
                    if obj != None:
                        for retPred in self._osp[obj][sub]:
                            yield (sub, retPred, obj)
                    # sub None None
                    else:
                        for retPred, objSet in self._spo[sub].items():
                            for retObj in objSet:
                                yield (sub, retPred, retObj)
            else:
                if pred != None:
                    # None pred obj
                    if obj != None:
                        for retSub in self._pos[pred][obj]:
                            yield (retSub, pred, obj)
                    # None pred None
                    else:
                        for retObj, subSet in self._pos[pred].items():
                            for retSub in subSet:
                                yield (retSub, pred, retObj)
                else:
                    # None None obj
                    if obj != None:
                        for retSub, predSet in self._osp[obj].items():
                            for retPred in predSet:
                                yield (retSub, retPred, obj)
                    # None None None
                    else:
                        for retSub, predSet in self._spo.items():
                            for retPred, objSet in predSet.items():
                                for retObj in objSet:
                                    yield (retSub, retPred, retObj)
        # KeyErros occur if a query term wasn't in the index, so we yield nothing
        except KeyError:
            pass
        
    # a convenience method for querying a single value of a single triple
    def value(self, sub=None, pred=None, obj=None):
        for retSub, retPred, retObj in self. triples((sub, pred, obj)):
            if sub is None: return retSub
            if pred is None: return retPred
            if obj is None: return retObj
            break
        return None

