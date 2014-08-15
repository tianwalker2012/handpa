# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 11:11:05 2014

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

class ScoreSupporter:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        if cmd == 'total':
            pts = MongoUtil.fetchPage('columbia',{}, 0, 1)
            return pts.count()
        if cmd == 'upload':
            params = web.data();
            #passTime = params.passTime
            #ua = params.ua
            jsonData = simplejson.loads(params)
            web.debug("passTime:%r", jsonData)
            ctime = jsonData.get('time')
            MongoUtil.save('columbia', jsonData)
            if ctime:
                histGram = MongoUtil.fetch('histgram', {})
                if not histGram:
                    histGram = {}
                
                val = histGram.get(ctime)
                if val:
                    ++val
                    histGram[ctime] = val
                else:
                    histGram[ctime] = 1
                MongoUtil.update('histgram', histGram)
                total = 1
                beating = 1
                for tm in histGram:
                    if tm > ctime:
                        total += histGram.get(tm)
                        beating += histGram.get(tm)
                    else:
                        total  += histGram.get(tm)
                
                return 100 * beating/total
            
            
