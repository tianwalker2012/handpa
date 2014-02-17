# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 22:52:53 2013

@author: apple
"""
from datetime import datetime 
from baseobject import BaseObject
from user import fetchUser
from mongoUtil import MongoUtil
from time import sleep
from bson.objectid import ObjectId

imgColName = 'images'
class LoadedImage:
    loadedImages = []

#Will assign value to the loadedImages. Yes. 
def getAllImages():
    listImages = MongoUtil.fetchAll(imgColName,'created_at')
    del LoadedImage.loadedImages[:]  
    for imgMap in listImages:
        img = Image()
        img.populate(imgMap)
        LoadedImage.loadedImages.append(img)

#Clean all test data
def removeAllImages():
    MongoUtil.removeAll(imgColName)
    
class Image(BaseObject):
    counter = 1

    def save(self):
        values = self.serialize()        
        rd = MongoUtil.save(imgColName, values)
        self._id = rd       
        
    def __init__(self):
        Image.counter += 1
        #self.id = Image.counter
        self._id = None
        #self.author = None
        self.authorID = None
        self.created_at = datetime.now()
        self.url = ''
        self.longitude = 0.0
        self.latitude = 0.0
        self.locLabel = ""
        #comment will inserted by user and can be uploaded 
        self.description = ""

#Just store the object, keep it simple and stupid,
#get the image storage done
class CombinedImage(BaseObject):
    def __init__(self, imageOne, imageTwo, url, iconURL):
        self.imageOne = imageOne
        self.imageTwo = imageTwo
        self.imageURL = url
        self.iconURL = iconURL
        #used to find out in which position this image at.
        #so we could check the image out
        self.position = 0

def updateURL():
    import re
    photos = MongoUtil.fetchSome('photos',{},'_id')
    #print "total fetched",len(photos)
    for ph in photos:
        print "value:", str(ph) 
        if 'screenURL' in ph:
            print 'update called'
            staticURL = ph['screenURL']     
            print "replace static url", staticURL
            ph['screenURL'] = re.sub(r"\d*\.\d*\.\d*\.\d*",'172.13.1.10',staticURL)
            ph['width'] = 3.0
            ph['height'] = 4.0
            ph['matchedUsers'] = []
            ph['photoRelations'] = []
            MongoUtil.update('photos', ph)



if __name__ == "__main__":
    #updateURL();
    photos = MongoUtil.fetchPage('photos', {'personID':ObjectId('530157b4e7b5b99901f147ea')}, 0, 5, [('createdTime', -1)])
    print "fetched back"
    for ph in photos:
        print "photo is:%r" % (ph)
    
    photos = MongoUtil.fetchSome('photos', {'personID':ObjectId('530157b4e7b5b99901f147ea')})
    print "different fetch method"
    for ph in photos:
        print "photo is:%r" % (ph)
    
    
    
    
    
    