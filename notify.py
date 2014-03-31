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

def cleanPerson(person):
    if '_id' in person:
        pid = person['_id']
        del person['_id']
        person['personID'] = str(pid)
    if 'password' in person:
        del person['password']
    if 'createTime' in person:
        person['createTime'] = str(person['createTime'])
    person.pop('friends', None)
    return person

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
    if 'matchedID' in note:
        photo = MongoUtil.fetchByID('photos', ObjectId(note['matchedID']))
        web.debug('matchID is %s, %r' % (note['matchedID'], photo))
        if photo:
            if not 'uploaded' in photo or not photo['uploaded']:
                return None   
            note['matchedPhoto'] = cleanPhoto(photo)
    if 'sender' in note:
        person = MongoUtil.fetchID('persons', ObjectId(note['sender']))
        web.debug('sender detail:%r' % person)
        if person:
            note['senderPerson'] = cleanPerson(person)

    if 'srcID' in note:        
        photo = MongoUtil.fetchByID('photos', ObjectId(note['srcID']))
        if photo:
            note['srcPhoto'] = cleanPhoto(photo)
    if 'createdTime' in note:
        note['createdTime'] = str(note['createdTime'])
    if 'photoID' in note:
        photo = MongoUtil.fetchByID('photos', ObjectId(note['photoID']))
        if photo:
            note['photo'] = cleanPhoto(photo)

    if 'otherID' in note:
        person = MongoUtil.fetchByID('persons', ObjectId(note['otherID']))
        if person:
            note['person'] = cleanPerson(person)
    
    web.debug("final notes:%r" % note)
    return note

class Notify:
    def GET(self):
        return self.process();        
    def POST(self):
        return self.process();
    def process(self):
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID') 
        params = web.data()
        jsons = simplejson.loads(params if params else '{}')
        web.debug('Notify userSession: %s, %r' % (userSession, jsons))
        if not userSession:
                web.ctx.status = '406 Not login'
                return 'not userID'   
        remove = True
        startPage = 0
        pageSize = 10
        if 'keep' in jsons:
            remove = jsons['keep']
        
        if 'startPage' in jsons:
            startPage = jsons['startPage']
        
        if 'pageSize' in jsons:
            pageSize = jsons['pageSize']

        query = {'personID':userSession,}
        if remove:
            query = {'personID':userSession, 'remove':{'$ne':'1'}}
        
        notes = MongoUtil.fetchPage('notes',query,startPage,pageSize,[('createdTime', -1)])
        #web.debug('notes count:%i' % len(notes))
        res = []
        for note in notes:
           cleanedNote = cleanNote(note)
           if cleanedNote:
               res.append(cleanedNote)
               if remove:
                   note['remove'] = '1'
                   MongoUtil.update('notes', note)
        web.debug('Total friend:'+ str(len(res)))
        return simplejson.dumps(res)        
        
    
    