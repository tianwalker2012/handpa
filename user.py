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
  self.mongoObjID = None



if __name__ == "__main__":
 user1 = fetchUser("Coolguy")
 user1.name = "tiange2016"
 print "assigned name:", user1.name
 storeUser(user1)
 userfetched = fetchUser("Coolguy")
 print "current name:", userfetched.name
 user2 = user('random');
 storeUser(user2);
 userfetched = fetchUser('random')
 print "verify save new object,",userfetched.serialize()
 
 #userfetched.populate({"nickName":"Tiange2013","status":3})
 #stored = userfetched.serialize()
 #print "stored value:", stored
 #print "have serialize:",isSerializable(userfetched),",counter case:",isSerializable('cool')
 #print "if is types:", isinstance([], types.ListType),", map type:",isinstance({}, types.DictType)
 