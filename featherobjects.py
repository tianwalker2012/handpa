# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 14:27:59 2014

@author: apple
"""

from datetime import datetime 
from baseobject import BaseObject
from user import fetchUser
from mongoUtil import save
from mongoUtil import fetchAll
from mongoUtil import removeAll
import simplejson
import json


#Streamline the storage functionality
class FeatherBase(BaseObject):
    def __init__(self):
        self.colName = None
    
    def saveToCol(self, colName):
        values = self.serialize()        
        rd = save(colName, values)
        self._id = rd  

    def save(self):
        self.saveToCol(self.colName)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = list(obj.timetuple())[0:6]
        else:
            encoded_object =json.JSONEncoder.default(self, obj)
        return encoded_object

class Person(FeatherBase):
    def __init__(self):
        self.colName = 'ft_person'
        self._id = None
        self.name = None
        self.email = None
        self.loginID = None
        self.mobile = None
        self.avatar = None
        self.joinedTime = None
        self.joined = 0
        self.friends = []

#Information like verification image also store here
class LoginInfo(FeatherBase):
    def __init__(self):
        self.colName = 'ft_login'
        self._id = None
        self.personID = None
        self.name = None
        self.password = None

#The relationship among users
class FriendShip(FeatherBase):
    def __init__(self):
        self.colName = 'ft_friendship'
        self._id = None
        self.ownerID = None
        self.friendID = None
        self.status = 0
        
class UploadedImage(FeatherBase):
    def __init__(self):
        self.colName = 'ft_uploaded'
        self._id = None
        self.thumbnail = None
        self.screenURL = None
        self.originalURL = None
        self.assetURL = None 
        #used to map the server image with the image in the album
        self.uploaded = 0
        self.personID = None
        self.latitude = 0.0
        self.longitude = 0.0
        self.uploadTime = None
        self.createdTime = None
        self.shotTime = None
        self.combined = []


if __name__ == "__main__":
    tian = Person()
    tian.joinedTime = datetime.now()
    tian.save()
    print "stored id:", str(tian._id)
    print "json serializer:", str(simplejson.dumps(tian.serializeJson()))
    
    