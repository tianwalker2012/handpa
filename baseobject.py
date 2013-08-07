# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 16:41:50 2013

@author: apple
"""
import types
def isSerializable(obj):
    invert_op = getattr(obj, "serialize", None)
    if callable(invert_op):
        return 1
    else:
        return 0

def isMap(obj):
    return isinstance(obj, types.DictType)

def isList(obj):
    return isinstance(obj, types.ListType)

def serializeList(lists, proc):
    res = []
    for val in lists:
        res.append(proc(val, proc))
    return res

#find the power of passing method
#I love this game
def serializeMap(maps, proc):
    res = {}
    for key in maps:
      val = maps[key]
      res[key] = proc(val, proc)
    #print "serialize map get called src:",maps,", dest:",res
    return res

class BaseObject:
    def __init__(self):
        print "base get called"

    
    #initialize object by the value from the database
    #Will iterate the object map to get value out. 
    def populate(self,values):
        for key in self.__dict__:
            if values.get(key, None):
                self.__dict__[key] = values[key]

     #I will serialize the value to things I could store
    def serialize(self):
         res = {}
         def proc(inVal, prc):
             if isMap(inVal):
                 return serializeMap(inVal, prc)
             elif isList(inVal):
                 return serializeList(inVal, prc)
             elif isSerializable(inVal):
                 return inVal.serialize()
             else:
                 return inVal

         for key in self.__dict__:
             val = self.__dict__.get(key, None)
             if val:
                 res[key] = proc(val, proc)
         return res
