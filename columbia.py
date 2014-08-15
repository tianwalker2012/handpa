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
            web.header('Content-Type', 'application/javascript')
            pts = MongoUtil.fetchPage('columbia',{}, 0, 1)
            histData = MongoUtil.fetch('histgram', {})
            histGram = histData.get("data")
            tc = pts.count() if pts else 0
            histGram = histGram if histGram else {}
            return "var totalPerson=" + tc +";var hist="+simplejson.dumps(histGram)+";"
        if cmd == 'upload':
            params = web.input();
            #passTime = params.passTime
            #ua = params.ua
            #jsonData = simplejson.loads(params)
            jsonData = {}
            ctime = params.get('time')
            if ctime:
                jsonData['time'] = ctime
            if params.get('meter'):
                jsonData['meter'] = params['meter']
            #meter = params.meter
            web.debug("passTime:%r" % jsonData)
            MongoUtil.save('columbia', jsonData)
            if ctime:
                histData = MongoUtil.fetch('histgram', {})
                histGram = histData.get("data")
                if not histData:
                    histGram = {}
                    histData = {"data":histGram}
                    MongoUtil.save('histgram',histData)
                
                if not histGram:
                    histGram = {}
                    histData["data"] = histGram
                val = histGram.get(str(ctime))
                if val:
                    ++val
                    histGram[str(ctime)] = val
                else:
                    histGram[str(ctime)] = 1
                MongoUtil.update('histgram', histData)
                total = 1
                beating = 1
                for tm in histGram:
                    intTm = int(tm)
                    if intTm > ctime:
                        total += histGram.get(tm)
                        beating += histGram.get(tm)
                    else:
                        total  += histGram.get(tm)
                
                return 100 * beating/total
            
            
