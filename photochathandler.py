# -*- coding: utf-8 -*-
"""
Created on Thu May 29 15:31:50 2014

@author: apple
"""
import web
import simplejson
import hashlib
from datetime import datetime, timedelta
from mongoUtil import MongoUtil
from bson.objectid import ObjectId
from imageutil import ImageUtil
from pushSender import sendPush
from i18nStrings import localInfo
from notify import cleanNote
import re
import os
import math
import string
import random
from random import randint
from pytz import timezone
import pytz


chinaTime = timezone('Asia/Shanghai')
def cleanChat(photoChat):
    if photoChat.get('_id'):
        photoChat['chatID'] = str(photoChat['_id'])
        photoChat.pop('_id', None)
    if photoChat.get('createdTime'):
        photoChat['createdTime'] = str(photoChat['createdTime'])
    return photoChat

class PhotoChatHandler:
    def POST(self):
        return self.GET()

    def GET(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        #web.debug("photo operation data:"+ str(params)+","+str(userSession))
        jsons = simplejson.loads(params)
        web.debug('chat detail:%r' % jsons)
        cmd = jsons['cmd']
        if cmd == 'add':
            return self.addComments(userSession, jsons)
        elif cmd == 'query':
            return self.queryComments(userSession, jsons)
    
    def queryComments(self, userSession, jsons):
        photoID = jsons.get('photoID')
        otherPhotoID = jsons.get('otherPhotoID')
        chatID = jsons.get('chatID')
        photoChats = None
        if chatID:
            photoChats = MongoUtil.fetchSome('photochat', {'_id':ObjectId(chatID)})  
        else:
            photoChats = MongoUtil.fetchSome('photochat', {'photos':photoID,'photos':otherPhotoID}, [('createdTime',1)])
        res = []
        for pc in photoChats:
            res.append(cleanChat(pc))
        return simplejson.dumps(res)
        #web.debug('full result:%s' % fullRes)
        #return '{}'#fullRes
            
        #ph['createdTime'] = datetime.strptime(ph['createdTime'], '%Y-%m-%d %H:%M:%S.%f')
    def addComments(self, userSession, jsons):
        photoID = jsons.get('photoID')
        otherPhotoID = jsons.get('otherPhotoID')
        #otherPersonID = jsons.get('otherPersonID')
        createdTime = datetime.strptime(jsons['createdTime'], '%Y-%m-%d %H:%M:%S.%f')
        photos = [photoID, otherPhotoID]
        text = jsons.get('text')
        #photo = MongoUtil.fetchByID('photos', ObjectId(photoID))
        #photo['conversations'] = [{'text':text, 'date':createdTime}]
        #MongoUtil.update('photos', photo)
        chatID = MongoUtil.save('photochat',{'photos':photos, 'text':text, 'speakerID':userSession, 'createdTime':createdTime})
        recievePhoto = MongoUtil.fetchByID('photos', ObjectId(otherPhotoID))
        if recievePhoto:
            self.sendTextNotes(otherPhotoID,userSession, photoID, str(recievePhoto.get('personID')), userSession, text, createdTime, chatID)
        return '{}'
    
    def sendTextNotes(self, recievePhotoID,userSession,senderPhotoID, otherPersonID, senderPersonID, text, createdTime, chatID):
        noteDict = {'type':'textSend','speakerID':userSession,'personID':otherPersonID,'chatID':str(chatID), 'photos':[recievePhotoID, senderPhotoID], 'text':text, 'createdTime':datetime.now(chinaTime) + timedelta(hours = 8)}
        noteID = MongoUtil.save('notes', noteDict)
        web.debug('stored noteID:%r' % noteID)        
        person = MongoUtil.fetchByID('persons',ObjectId(otherPersonID))
        otherPerson = MongoUtil.fetchByID('persons', ObjectId(senderPersonID))        
        token = person.get('pushToken')
        if len(text) > 20:
            text = text[:20]
        name = otherPerson.get('name')
        if len(name) > 8:
            name = name[:8]
        if(token):
            web.debug('find token:%s' % person.get('pushToken'))
            #filledNote = cleanNote(noteDict)
            otherPerson = MongoUtil.fetchByID('persons', ObjectId(senderPersonID))
            sendPush(token,localInfo(person.get('lang'), '%s说:%s') % (name, text),{'noteID':str(noteDict['_id'])}, person.get('prodFlag'))     
        else:
            web.debug('user %s have no token' % recievePersonID)        