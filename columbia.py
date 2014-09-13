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

def makeIfNone(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

class BirdData:
    def GET(self):
        return self.POST();
    def POST(self):
        web.debug(web.data())
        uploaded = simplejson.loads(web.data())
        MongoUtil.create('TrainedBird', uploaded)
        web.debug('id is:%s', str(uploaded.get('_id')))
        return 'success'
class Helmet:
    def GET(self):
        return self.POST();

    def POST(self):
        cookie = web.cookies(visitCount=0)
        web.debug('visit count:%r' % cookie.visitCount)
        vcount = int(cookie.visitCount)
        vcount += 1
        web.setcookie('visitCount',vcount, 360000,path='/')
        if vcount == 1:
            MongoUtil.save("PhotoUsage", {"useCount":1})
        render = web.template.render('templates')
        return render.photo({"visitCount":vcount})
        
class ScoreSupporter:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        if cmd == 'total':
            web.header('Content-Type', 'application/javascript')
            pts = MongoUtil.fetchPage('columbia',{}, 0, 1)
            histData = MongoUtil.fetch('histgram', {})
            
            histGram = {}
            if histData:
                histGram = histData.get("data")
            tc = pts.count() if pts else 0
            #histGram = histGram if histGram else {}
            return "var totalPerson=%i" % tc +";var hist="+simplejson.dumps(histGram)+";"
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
                histGram = None;#histData.get("data")
                if not histData:
                    histGram = {}
                    histData = {"data":histGram}
                    MongoUtil.save('histgram',histData)
                else:
                    histGram = histData.get("data")
                
                if not histGram:
                    histGram = {}
                    histData["data"] = histGram
                val = histGram.get(str(ctime))
                
                if val:
                    val += 1;
                    web.debug("value is:%i, time:%s" % (val, str(ctime)))
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

class RawUploader:
    def GET(self):
        return '{}'

    def POST(self):
        #x = web.input(myfile={})
        data = web.data()[23:].decode('base64')
        #web.debug('data:%r' % data)
        
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '/home/ec2-user/root/www/static/raw/'
        storedDir = '%s/static/%s/' % (os.getcwd(),'raw')         
        makeIfNone(storedDir)
        web.debug('final stored dir:%s' % storedDir)
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/raw/'
        #filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        
        postFix = 'jpg'#filePath.split('.')[-1]
        hashedName = hashlib.md5('raw' + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(data)
        fout.close()
        #ImageUtil.resize(imageFileName, 60, 'tb')
        #storedPhoto['screenURL'] = baseURL+hashedName
        remoteURL = baseURL + hashedName
        #storedPhoto = None
        """        
        if photoID:
            storedPhoto = MongoUtil.fetchByID('StoredPhoto', ObjectId(photoID))
            storedPhoto['remoteURL'] = remoteURL
            MongoUtil.update('StoredPhoto',storedPhoto)
        else:
            storedPhoto = {'taskID':taskID, 'sequence':int(sequence), 'remoteURL':remoteURL}
            MongoUtil.save('StoredPhoto', storedPhoto)
        """
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        
        return remoteURL#simplejson.dumps(cleanStoredPhoto(storedPhoto))         
            
