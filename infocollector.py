# -*- coding: utf-8 -*-
"""
Created on Sun May 11 12:22:30 2014

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

"""Collect information from the client side"""
class InfoCollector:
    def GET(self):
        return self.process();        
    def POST(self):
        return self.process();
    def process(self):
        userSession = web.ctx.env.get('HTTP_X_CURRENT_PERSONID') 
        params = web.data()
        #jsons = simplejson.loads(params if params else '{}')
        web.debug('info from userSession: %s, %r' % (userSession, params))
        if not userSession:
                web.ctx.status = '406 Not login'
                return 'not userID'   
        MongoUtil.save('remote_logs', {'personID':userSession, 'data':params, 'createdTime':datetime.now()})
        return '{}'