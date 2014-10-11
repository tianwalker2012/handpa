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

def cleanUser(user):
    strID = str(user['_id'])
    strDate = str(user['createdTime'])
    user.pop('_id', None)
    user['personID'] = strID
    user['createdTime'] = strDate
    return user

def cleanInfoPoint(infoPoint):
    infoPoint['infoID'] = str(infoPoint.get('_id'))
    infoPoint.pop('_id', None)
    return infoPoint

def fillTask(photoTask):
    photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':str(photoTask['_id'])},[('sequence', 1)])
    phs = []
    for ph in photos:
        infoPts = MongoUtil.fetchSome('InfoPoint', {'photoID':str(ph['_id'])})
        if infoPts:        
            ph['infos'] = [cleanInfoPoint(infoPt) for infoPt in infoPts]
        phs.append(cleanStoredPhoto(ph))
    taskID = str(photoTask['_id'])
    photoTask.pop('_id', None)
    photoTask['createdTime'] = str(photoTask['createdTime'])
    photoTask['photos'] = phs;
    photoTask['taskID'] = taskID
    return photoTask

def fetchPhotoInfo(photoID):
    infoPts = MongoUtil.fetchSome('InfoPoint', {'photoID':photoID})
    web.debug('info for:%s=%i' % (photoID, infoPts.count()))
    return [info for info in infoPts]
    

class InfoPoint:
    def GET(self, cmd):
        return self.POST(cmd);
    def POST(self, cmd):
        params = web.input()
        for key in params:
            web.debug('param %s,%s' % (key, params[key]))
        if cmd == 'create':
            data = {'x':params.x, 
                    'y':params.y,
                    'photoID':params.photoID,
                    'title':params.title,
                    'type':params.type,
                    'comment':params.comment}
            
            MongoUtil.create('InfoPoint', data)
            return simplejson.dumps({'infoID':str(data.get('_id'))})
        elif cmd == 'update':
            data = {'x':params.x, 
                    'y':params.y,
                    'photoID':params.photoID,
                    'title':params.title,
                    'type':params.type,
                    'comment':params.comment}
            data['_id'] = ObjectId(params.infoID)
            MongoUtil.update('InfoPoint', data)
            return '{}'
        elif cmd == 'remove':
            MongoUtil.remove('InfoPoint', {'_id':ObjectId(params.infoID)})
            return '{}'

class Account:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        params = web.input()
        web.debug('params:%r' % params.get('personID'))
        if cmd == 'create':
            user = {"createdTime":datetime.now(chinaTime)+timedelta(hours=9)}
            MongoUtil.save('P3dUser', user)
            return simplejson.dumps(cleanUser(user))
        elif cmd == 'query':
            #tasks = None
            queryCond = {'$nor':[{'isPrivate':True}]}
            start = int(params.start) if params.get('start') else 0
            limit = int(params.limit) if params.get('limit') else 10
            if params.get('personID'):
                queryCond = {'personID':params.personID}
                start = 0
                limit = 200
            web.debug('cond:%r,start:%i,limit:%i' % (queryCond, start, limit)) 
            tasks = MongoUtil.fetchWithLimit('PhotoTask', queryCond, start, limit, [('createdTime', -1)])
            res = []            
            for tk in tasks:
                res.append(fillTask(tk))
            return simplejson.dumps(res)
        elif cmd == 'clean':
            tasks = MongoUtil.fetchAll('PhotoTask')
            count = 0
            for tk in tasks:
                photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':str(tk['_id'])})
                web.debug('photo count:%i, id:%s' % (photos.count(), str(tk['_id'])))
                if photos.count() == 0:
                    MongoUtil.remove('PhotoTask', {'_id':tk['_id']})
                    count += 1
            return '{"count":%i}' % count
                
            
class P3DShow:
    def GET(self):
        return self.POST()
    def POST(self):
        params = web.input()
        photos = MongoUtil.fetchSome('StoredPhoto', {'taskID':params.taskID},[('sequence', 1)])
        pts = []
        def process(pht):
            pts.append(pht)
            return pht.get('remoteURL')
        imgUrls = [process(pt) for pt in photos];        
        #for pt in photos:
        infos = []
        i = 0
        for pt in pts:
            pinfos = fetchPhotoInfo(str(pt.get('_id')))
            for info in pinfos:
                web.debug('get info out')
                info['pos'] = i
                infos.append(info)
            i += 1
        render = web.template.render('templates', globals={'simplejson':simplejson})
        return render.show3d({"imagelist":imgUrls, "zoomlist":imgUrls,'infos':infos})

class IDCreator:
    def GET(self, cmd):
        return self.POST(cmd)
    def POST(self, cmd):
        if cmd == 'create':
            params = web.input()
            store = {"personID":params.personID, "createdTime":datetime.now(chinaTime)+timedelta(hours=9)}
            name = params.get('name')
            if name:
                store['name'] = name
            MongoUtil.save('PhotoTask', store)
            res = {"id":str(store.get('_id'))}
            return simplejson.dumps(res)
        elif cmd == 'query':
            params = web.input()
            web.debug("query data:%r" % params)
            if params.id:
                photoTask = MongoUtil.fetchByID('PhotoTask', ObjectId(params.id))
                if photoTask:
                    fillTask(photoTask)
                return simplejson.dumps(photoTask)

        elif cmd == 'update':
            params = web.input()
            if params.get('taskID'):
                web.debug('params:%r' % params)
                MongoUtil.update('PhotoTask',{'_id':ObjectId(params.get('taskID')), "name":params['name'], "isPrivate":params['isPrivate']})
            return '{}'
        elif cmd == 'delete':
            params = web.input()
            if params.get('taskID'):
                MongoUtil.remove('PhotoTask', {'_id':ObjectId(params.get('taskID'))})
            return '{}'
        return '{}'
def cleanStoredPhoto(storedPhoto):
    pid = str(storedPhoto.get('_id'))
    storedPhoto['photoID'] = pid
    storedPhoto.pop('_id', None)
    return storedPhoto

class RawPhotoUpload:
    def POST(self):
        x = web.input(file={})
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        #storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'
        taskID = "167791"
        storedDir = '%s/static/%s/' % (os.getcwd(),taskID)         
        makeIfNone(storedDir)
        #web.debug('final stored dir:%s, %s' % (storedDir,isOriginal))
        baseURL = 'http://'+ web.ctx.env.get('HTTP_HOST') +'/static/'+taskID+'/'
        filePath = x['file'].filename.replace('\\','/').split('/')[-1]
        postFix = filePath.split('.')[-1]
        hashedName = hashlib.md5(filePath + str(datetime.now(chinaTime))).hexdigest() + '.' + postFix
        imageFileName = storedDir+hashedName;
        fout = open(imageFileName, 'w')
        fout.write(x.file.file.read())
        fout.close()
        remoteURL = baseURL + hashedName
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        result = {"url":remoteURL}
        return simplejson.dumps(result)

class PhotoUploader:
    def GET(self):
        params = web.input();
        cmd = params.cmd
        if cmd == 'del':
            photoID = params.photoID
            MongoUtil.remove('StoredPhoto', {'_id':ObjectId(photoID)})
            #Need to delete the uploaded photo too
        elif cmd == 'update':
            photoIDs = params.photoID.split(',')
            #sequences = params.sequence.split(',')
            for i in range(0, len(photoIDs)):
                photoID = photoIDs[i]
                #sequence = sequences[i]
                web.debug('photoID:'+photoID)
                MongoUtil.updateByConds('StoredPhoto', {'_id':ObjectId(photoID)}, {'sequence':i})
        return '{}'

    def POST(self):
        x = web.input(myfile={})
        taskID = x["taskID"]
        photoID = x.get("photoID")
        sequence = x.get("sequence")
        isOriginal = x.get("isOriginal")
        #storedDir = '/home/ec2-user/root/www/static/'+userSession+'/'
        storedDir = '/home/ec2-user/root/www/static/'+taskID+'/'
        #storedDir = '%s/static/%s/' % (os.getcwd(),taskID)         
        makeIfNone(storedDir)
        web.debug('final stored dir:%s, %s' % (storedDir,isOriginal))
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
            oldRemoteURL = storedPhoto['remoteURL']
            storedPhoto['remoteURL'] = remoteURL
            if isOriginal and int(isOriginal) == 1:
                storedPhoto['originalURL'] = remoteURL
            elif not storedPhoto.get('originalURL'):
                storedPhoto['originalURL'] = oldRemoteURL
            MongoUtil.update('StoredPhoto',storedPhoto)
        else:
            storedPhoto = {'taskID':taskID, 'sequence':int(sequence), 'remoteURL':remoteURL, 'originalURL':remoteURL}
            MongoUtil.save('StoredPhoto', storedPhoto)
        
        #task = MongoUtil.fetchByID('PhotoTask', ObjectId(taskID))
        
        return simplejson.dumps(cleanStoredPhoto(storedPhoto))