# -*- coding: utf-8 -*-
"""
Created on Sun Jul 13 13:01:00 2014

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
class TouchHandler:
    def GET(self):
        return self.POST()
    
    def POST(self):
        params = web.data()
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID')
        uploaded = simplejson.loads(params)
        web.debug("%s touch %s" % (userSession, str(params)))
        touches = uploaded.get('touches');
        touchPerson = MongoUtil.fetch('persons', {'_id':ObjectId(userSession)})
        personID = uploaded.get('personID')
        #if not personID or not userSession:
        ps = MongoUtil.fetch('persons', {'_id':ObjectId(personID)})
        token = ps.get('pushToken')            
        note = {'personID':str(ps['_id']), 'type':'touched','touches':touches, 'otherID':userSession, 'createdTime':datetime.now(chinaTime)+timedelta(8)};
        MongoUtil.save('notes', note)
        if token:
            lang = ps.get('lang')
            message = localInfo(lang, '%s摸了你一下') % touchPerson.get('name')
            sendPush(token, message, {'noteID':str(note['_id'])}, ps.get('prodFlag'))
        return '{}'
        
            