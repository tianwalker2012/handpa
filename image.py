# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 22:52:53 2013

@author: apple
"""
from datetime import datetime 
from baseobject import BaseObject
from user import fetchUser
from mongoUtil import save
from mongoUtil import fetchAll
from mongoUtil import removeAll
from time import sleep


imgColName = 'images'

class LoadedImage:
    loadedImages = []

#Will assign value to the loadedImages. Yes. 
def getAllImages():
    listImages = fetchAll(imgColName,'created_at')
    del LoadedImage.loadedImages[:]  
    for imgMap in listImages:
        img = Image()
        img.populate(imgMap)
        LoadedImage.loadedImages.append(img)

#Clean all test data
def removeAllImages():
    removeAll(imgColName)
    
class Image(BaseObject):
    counter = 1

    def save(self):
        values = self.serialize()        
        rd = save(imgColName, values)
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

if __name__ == "__main__":
    img = Image()
    img.description = 'hello1'
    img.save()  
    
    img1 = Image()
    img1.description = 'hello2'
    img1.save()

    img2 = Image()
    img2.description = 'hello3'
    img2.save()
    
    getAllImages()
    for img in LoadedImage.loadedImages:
        print 'result:',img.serialize()
    removeAllImages()
    print "after remove"
    del LoadedImage.loadedImages[:]
    getAllImages()
    for img in LoadedImage.loadedImages:
        print 'result:',img.serialize()
    
    
    