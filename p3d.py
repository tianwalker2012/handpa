# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 10:54:59 2014

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

class P3DShow:
    def GET(self):
        return self.POST();
    def POST(self):
        params = web.input()
        photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':params.taskID},[('sequence', 1)])
        imgUrls = [pt.get('remoteURL') for pt in photos];        
        #for pt in photos:
        render = web.template.render('templates', globals={'simplejson':simplejson})
        return render.show3d({"imagelist":imgUrls, "zoomlist":imgUrls})
class IDCreator:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        if cmd == 'create':
            store = {"createdTime":datetime.now(chinaTime)+timedelta(hours=9)}
            MongoUtil.save('PhotoTask', store)
            res = {"id":str(store.get('_id'))}
            return simplejson.dumps(res)
        elif cmd == 'query':
            params = web.input()
            web.debug("query data:%r" % params)
            if params.id:
                photoTask = MongoUtil.fetchByID('PhotoTask', ObjectId(params.id))
                if photoTask:
                    photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':params.id},[('sequence', 1)])
                    phs = []
                    for ph in photos:
                        phs.append(cleanStoredPhoto(ph))
                    photoTask.pop('_id', None)
                    photoTask['photos'] = phs;
                    photoTask['createdTime'] = str(photoTask['createdTime'])
                return simplejson.dumps(photoTask)

def cleanStoredPhoto(storedPhoto):
    pid = str(storedPhoto.get('_id'))
    storedPhoto['photoID'] = pid
    storedPhoto.pop('_id', None)
    return storedPhoto
    
    
class PhotoUploader:
    def GET(self):
        params = web.input();
        cmd = params.cmd
        if cmd == 'del':
            photoID = params.photoID
            MongoUtil.remove('StoredPhoto', {'_id':ObjectId(photoID)})

        elif cmd == 'update':
            photoIDs = params.photoID.split(',')
            sequences = params.sequence.split(',')
            for i in range(0, len(photoIDs)):
                photoID = photoIDs[i]
                sequence = sequences[i]
                web.debug('photoID:'+photoID)
                MongoUtil.updateByConds('StoredPhoto', {'_id':ObjectId(photoID)}, {'sequence':sequence})
        return '{}'

    def POST(self):
        x = web.input(myfile={})
        taskID = x["taskID"]
        photoID = x.get("photoID")
        sequence = x["sequence"]
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'
        storedDir = '%s/static/%s/' % (os.getcwd(),taskID)         
        makeIfNone(storedDir)
        web.debug('final stored dir:%s' % storedDir)
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/'+taskID+'/'
        filePath = x['myfile'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(x.myfile.file.read())
        fout.close()
        ImageUtil.resize(imageFileName, 60, 'tb')
        #storedPhoto['screenURL'] = baseURL+hashedName
        remoteURL = baseURL + hashedName
        storedPhoto = None
        if photoID:
            storedPhoto = MongoUtil.fetchByID('StoredPhoto', ObjectId(photoID))
            storedPhoto.remoteURL = remoteURL
            MongoUtil.update('StoredPhoto',storedPhoto)
        else:
            storedPhoto = {'taskID':taskID, 'sequence':int(sequence), 'remoteURL':remoteURL}
            MongoUtil.save('StoredPhoto', storedPhoto)
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        
        return simplejson.dumps(cleanStoredPhoto(storedPhoto))