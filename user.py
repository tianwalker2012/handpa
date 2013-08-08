#!/usr/bin/python
# -*- coding: utf-8 -*- 
from datetime import datetime
from baseobject import BaseObject
from baseobject import isSerializable
from mongoUtil import fetch
from mongoUtil import create
from mongoUtil import update
from mongoUtil import save
from mongoUtil import fetchByID
from baseobject import isMap

import types
datastore = {}

userColName = "users"


def fetchUserByID(uid):
    res = fetchByID(userColName, uid)
    if res:
        outUser = user('dummy')
        outUser.populate(res)
        return outUser
    outUser = user('dummy')
    outUser.nickName = "羽毛控"
    return outUser

def fetchUser(openid):
    res = fetch(userColName,{"openid": openid})
    print "fetched back:",res
    outUser = user(openid)
    if not res:
        objid = create(userColName,{"openid": openid})
        outUser._id = objid
        return outUser
    else:
        outUser.populate(res); 
        return outUser;

def storeUser(inUser):
    """I assume the objectID existence will make mongodb aware that I am actually
    want to update the object
    """
    serialized = inUser.serialize()
    print "try to store user:",serialized
    save(userColName, serialized)



class user(BaseObject):
 def __init__(self, openid):
  self.openid = openid
  self._id = None
  self.created_at = datetime.now()
  self.updated_at = datetime.now()
  self.status = 1
  self.name = ""
  self.nickName = "羽毛游客"
  self.longitude = 0.0
  self.latitude = 0.0
  #will store the latest local label. 
  self.locLabel = None
  #what's the purpose of the combined?
  #make sure the 
  self.pendingImage = None
  #the previously combined Image
  #I could use a array to handle multiple images. 
  #or we could hold on to it.
  #mean we are busy doing this.
  self.pendingCombine = 0
  self.combinedImage = None
  self.combinedHistory = {}
  #What's the purpose of this member?
  #Make sure only the first message is the right one
  self.lastMessage = {}
  self.mongoObjID = None
  self.avatar = None


class TestObjSerialize(BaseObject):
    def __init__(self):
        self.name = "cool guy"
        self.property1 = {"Cool":"Guy"}
        self.property2 = {"Hot":"Girl"}

if __name__ == "__main__":
 user1 = fetchUser("Coolguy")
 user1.name = "tiange2016"
 print "assigned name:", user1.name
 storeUser(user1)
 userfetched = fetchUser("Coolguy")
 print "current name:", userfetched.name
 user2 = user('random2013');
 user2.nickName = "tiange2013"
 storeUser(user2);
 
 orgObj = user('origin')
 for key in orgObj.__dict__:
     print  key,":",orgObj.__dict__[key]
 
 userfetched = fetchUser('random2013')
 for key in userfetched.__dict__:
     print  "suspects:",key,":",userfetched.__dict__[key]

 userfetched.lastMessage['cool'] = 'Message'
 
 print 'serialized:',userfetched.serialize()
 
 userfetched.lastMessage = {"hot ":"hot message"}
 print "hot message:",userfetched.serialize()
 userfetched.nickName = "Brand new"
 storeUser(userfetched)
 userNew = fetchUser("random2013")
 for key in userNew.__dict__:
     print  "brandnew,",key,":",userNew.__dict__[key]
 print 'serialize:',userNew.serialize()
 
 """
 user2.lastMessage = {"Message":"RealMessage"}
 user2.lastMessage['Coolmessage'] = "Cool message"
 if isMap(user2.lastMessage):
     print "last message is map"
 else:
     print "last message is not map"
 print "verify save new object,",userfetched.serialize()
 userNative = user('hahaha')
 userNative.lastMessage = {"nativeproperty":"really really native"}
 print "Native user serialized:", userNative.serialize()
 ts = TestObjSerialize()
 print "serialize obj:", ts.serialize()
 """
 #userfetched.populate({"nickName":"Tiange2013","status":3})
 #stored = userfetched.serialize()
 #print "stored value:", stored
 #print "have serialize:",isSerializable(userfetched),",counter case:",isSerializable('cool')
 #print "if is types:", isinstance([], types.ListType),", map type:",isinstance({}, types.DictType)
 