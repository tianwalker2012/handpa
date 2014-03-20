# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 12:40:56 2014

@author: apple
"""
import web
import simplejson
import hashlib
from datetime import datetime
from mongoUtil import MongoUtil
from bson.objectid import ObjectId
from imageutil import ImageUtil
import re
import os
import math

def cleanConversation(conversation):
    if 'date' in conversation:
        conversation['date'] = str(conversation['date'])
    return conversation

def cleanConversations(conversations):
    for cs in conversations:
        cleanConversation(cs)
    return conversations

def cleanPhoto(photo):
    #pid = ''
    if '_id' in photo:
        pid = photo['_id']
        del photo['_id']
        photo['photoID'] = str(pid)
    if 'personID' in photo:
        photo['personID'] = str(photo['personID'])
    if 'createdTime' in photo:
        photo['createdTime'] = str(photo['createdTime'])
    if 'matchedUsers' in photo:
        del photo['matchedUsers']
    if 'screenURL' in photo:
        photo['screenURL'] = re.sub(r"\d*\.\d*\.\d*\.\d*:\d*",web.ctx.env.get('HTTP_HOST'),photo['screenURL'])
    if 'conversations' in photo:
        cleanConversations(photo['conversations'])
    photo.pop('photoRelations', None)
    #photo.pop('photoRelations', None)
    return photo

def cleanNote(note):
    web.debug('Clean note get called')
    if '_id' in note:
        noteID = str(note['_id'])
        note.pop('_id', None)
        note['noteID'] = noteID
    if 'matchID' in note:
        photo = MongoUtil.fetchByID('photos', ObjectId(note['matchID']))
        note['matchedPhoto'] = cleanPhoto(photo)
    if 'srcID' in note:        
        photo = MongoUtil.fetchByID('photos', ObjectId(note['srcID']))
        note['srcPhoto'] = cleanPhoto(photo)
    if 'createdTime' in note:
        note['createdTime'] = str(note['createdTime'])
    if 'photoID' in note:
        photo = MongoUtil.fetchByID('photos', ObjectId(note['photoID']))
        note['photo'] = cleanPhoto(photo)
    web.debug("final notes:%r" % note)
    return note

class Notify:
    def GET(self):
        return self.process();        
    def POST(self):
        return self.process();
    def process(self):
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')    
        web.debug('Notify userSession:'+ userSession)
        if not userSession:
                web.ctx.status = '406 Not login'
                return 'not userID'
        notes = MongoUtil.fetchPage('notes',{'personID':userSession},0,5,[('createdTime', -1)])
        #web.debug('notes count:%i' % len(notes))
        res = []
        for note in notes:
           res.append(cleanNote(note))
        web.debug('Total friend:'+ str(len(res)))
        return simplejson.dumps(res)        
        
    
    