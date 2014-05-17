# -*- coding: utf-8 -*-
"""
Created on Fri May 16 16:55:29 2014

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

class ChatHandler:
    def GET(self):
       return self.POST();

    def queryChat(self, userSession, paramJson):
        pids = paramJson.get('photos')
        chatInfos = MongoUtil.fetchSome('chats', {'photos':pids[0], 'photos':pids[1]},{'createdTime':-1})        
        res = []
        for chatText in chatInfos:
            chatText['_id'] = str(chatText['_id'])
            chatText['createdTime'] = str(chatText['createdTime'])
            res.append(chatText)
        return simplejson.dumps(res)        
    def cleanChat(self, chat):
        chat['_id'] = str(chat.get('_id'))
        chat['createdTime'] = str(chat['createdTime'])
    def uploadChat(self, userSession, paramJson):
        #pid1 = paramJson.get('photoID1')
        #pid2 = paramJson.get('photoID2')
        pids = paramJson.get('photos')
        createdTime = paramJson.get('createdTime')
        otherPid = paramJson.get('otherPid')
        timeStamp = datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S.%f")
        text = paramJson.get('text')
        #createdTime = targetText('createdTime')
        chatInfo = {'photos':pids, 'createdTime':timeStamp,'speaker':userSession,'text':text}
        chatID = MongoUtil.save('chats', chatInfo)
        noteID = MongoUtil.save('notes', {'type':'chat','personID':otherPid,'chatID':str(chatID),'createdTime':timeStamp})
        """            
            likedPush = MongoUtil.fetch('sent_like', {'likePerson':personID, 'photoID':photoID})
            if likedPush:
                return
            ps = MongoUtil.fetchByID('persons', ObjectId(photo['personID']))
            likePerson = MongoUtil.fetchByID('persons', ObjectId(personID))
            if not ps:
                return
            token = ps.get('pushToken')
            if token:
                MongoUtil.save('sent_like', {'likePerson':personID, 'photoID':photoID})
                lang = ps.get('lang')
                message = localInfo(lang, '%s喜欢了你的照片' % likePerson.get('name'))
                sendPush(token, message, {'noteID':str(noteID)}, ps.get('prodFlag') != '1')
            
       """
        
        return simplejson.dumps({'_id':str(chatID)})
        
    def POST(self):
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        params = web.data()
        web.debug('user:'+str(userSession)+",parameters:"+str(params))
        paramJson = simplejson.loads(params)
        cmd = paramJson.get('cmd')
        
        if cmd == 'upload':
            return self.uploadChat(userSession, paramJson)
        elif cmd == 'query':
            return self.queryChat(userSession, paramJson)
        